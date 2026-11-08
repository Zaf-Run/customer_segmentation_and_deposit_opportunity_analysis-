"""
01_clean_validate_export.py
Validates the raw bank file, builds a clean customer table, and exports
star schema tables for Power BI.

Run from the project root:  python python/01_clean_validate_export.py
Needs: pandas, numpy
"""
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "bank-full.csv"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- load
raw = pd.read_csv(RAW, sep=";")
checks = []  # (check, result, status)


def log(name, result, ok=True):
    checks.append((name, result, "PASS" if ok else "REVIEW"))


# ---------------------------------------------------------------- validate
log("Row count", len(raw))
log("Column count", raw.shape[1])
log("Missing values (all columns)", int(raw.isna().sum().sum()), raw.isna().sum().sum() == 0)
log("Exact duplicate rows", int(raw.duplicated().sum()), raw.duplicated().sum() == 0)
log("Age range", f"{raw.age.min()} to {raw.age.max()}", raw.age.between(18, 100).all())
log("Day of month range", f"{raw.day.min()} to {raw.day.max()}", raw.day.between(1, 31).all())
valid_months = {"jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"}
log("Months are valid", sorted(set(raw.month) - valid_months) or "all valid", set(raw.month) <= valid_months)
log("Target y only yes or no", sorted(raw.y.unique()), set(raw.y) == {"yes", "no"})
log("pdays = -1 matches previous = 0", bool(((raw.pdays == -1) == (raw.previous == 0)).all()),
    bool(((raw.pdays == -1) == (raw.previous == 0)).all()))
q1, q3 = raw.balance.quantile([.25, .75])
iqr = q3 - q1
hi, lo = q3 + 1.5 * iqr, q1 - 1.5 * iqr
n_out = int(((raw.balance > hi) | (raw.balance < lo)).sum())
log("Balance outliers by 1.5 x IQR (kept, flagged)", f"{n_out} rows ({n_out / len(raw):.1%})", False)
log("Balance min / max (EUR)", f"{raw.balance.min()} / {raw.balance.max()}", True)
for c in ["job", "education", "contact", "poutcome"]:
    n_unk = int((raw[c] == "unknown").sum())
    log(f"'unknown' in {c}", f"{n_unk} rows ({n_unk / len(raw):.1%})", n_unk / len(raw) < 0.05)
log("Customer ID column present", "No (surrogate key created)", False)
log("Year column present", "No (months cannot be placed on a timeline)", False)

# ---------------------------------------------------------------- clean + engineer
df = raw.copy()
for c in df.select_dtypes(include=["object", "string"]).columns:
    df[c] = df[c].str.strip().str.lower()

df.insert(0, "customer_id", np.arange(1, len(df) + 1))
df = df.rename(columns={"default": "credit_default", "housing": "housing_loan",
                        "loan": "personal_loan", "y": "term_deposit"})
for c in ["credit_default", "housing_loan", "personal_loan", "term_deposit"]:
    df[c + "_flag"] = (df[c] == "yes").astype(int)

# readable labels
df["job"] = df["job"].replace({"admin.": "admin"}).str.replace("-", " ", regex=False).str.title()
for c in ["marital", "education", "contact", "poutcome"]:
    df[c] = df[c].str.title()

# age groups
age_bins = [17, 24, 34, 44, 54, 64, 120]
age_labels = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
df["age_group"] = pd.cut(df.age, age_bins, labels=age_labels).astype(str)

# balance bands (EUR, average yearly balance)
bal_bins = [-np.inf, -1, 0, 500, 1500, 5000, np.inf]
bal_labels = ["1 Overdrawn", "2 Zero", "3 Low (1-500)", "4 Medium (501-1500)", "5 High (1501-5000)", "6 Very high (5000+)"]
df["balance_band"] = pd.cut(df.balance, bal_bins, labels=bal_labels).astype(str)

# month number and campaign intensity
month_num = {m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}
df["month_num"] = df["month"].map(month_num)
df["month"] = df["month"].str.title()
df["contacts_band"] = pd.cut(df.campaign, [0, 1, 3, 6, 1000], labels=["1", "2-3", "4-6", "7+"]).astype(str)

# engagement and product proxies (the file has no transaction history)
df["prior_contacted_flag"] = (df.pdays != -1).astype(int)
df["product_count"] = df.housing_loan_flag + df.personal_loan_flag + df.term_deposit_flag
df["no_product_flag"] = (df.product_count == 0).astype(int)
df["overdrawn_flag"] = (df.balance < 0).astype(int)
df["zero_or_negative_flag"] = (df.balance <= 0).astype(int)
df["balance_outlier_flag"] = ((df.balance > hi) | (df.balance < lo)).astype(int)
# Balance used for deposit totals: negative balances are kept in "net" and floored in "positive"
df["balance_positive"] = df.balance.clip(lower=0)

# ---------------------------------------------------------------- export
df.to_csv(OUT / "bank_customers_clean.csv", index=False)

dim_age = pd.DataFrame({"age_group": age_labels, "age_min": [18, 25, 35, 45, 55, 65],
                        "age_max": [24, 34, 44, 54, 64, 120], "sort_order": range(1, 7)})
dim_bal = pd.DataFrame({"balance_band": bal_labels,
                        "balance_min": [-100000, 0, 1, 501, 1501, 5001],
                        "balance_max": [-1, 0, 500, 1500, 5000, 1000000],
                        "sort_order": range(1, 7)})
dim_month = pd.DataFrame({"month": [m.title() for m in month_num], "month_num": list(month_num.values())})
dim_month["quarter"] = "Q" + ((dim_month.month_num - 1) // 3 + 1).astype(str)
dim_job = pd.DataFrame({"job": sorted(df.job.unique())})
dim_job["job_group"] = dim_job.job.map({
    "Management": "Professional", "Technician": "Professional", "Admin": "Professional",
    "Blue Collar": "Manual and service", "Services": "Manual and service", "Housemaid": "Manual and service",
    "Self Employed": "Business owner", "Entrepreneur": "Business owner",
    "Retired": "Not working", "Student": "Not working", "Unemployed": "Not working",
    "Unknown": "Unknown"})
dim_age.to_csv(OUT / "dim_age_group.csv", index=False)
dim_bal.to_csv(OUT / "dim_balance_band.csv", index=False)
dim_month.to_csv(OUT / "dim_month.csv", index=False)
dim_job.to_csv(OUT / "dim_job.csv", index=False)

report = pd.DataFrame(checks, columns=["check", "result", "status"])
report.to_csv(OUT / "data_validation_report.csv", index=False)
print(report.to_string(index=False))
print(f"\nClean rows: {len(df):,}  columns: {df.shape[1]}")
print("Files written to", OUT)
