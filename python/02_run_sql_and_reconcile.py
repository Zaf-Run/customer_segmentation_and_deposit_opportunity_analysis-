"""
02_run_sql_and_reconcile.py
Runs the project SQL (01 to 04) on a local SQLite copy of the data, saves each result
to data/processed/sql_results/, and checks the key numbers against independent pandas
calculations. This lets anyone reproduce the results without installing MySQL.

The SQL is written for MySQL 8 and kept portable, so the same queries run here.
Run from the project root:  python python/02_run_sql_and_reconcile.py
"""
import re
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "sql"
OUT = ROOT / "data" / "processed" / "sql_results"
OUT.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------- staging (replaces 00_load_mysql.sql)
raw = pd.read_csv(ROOT / "data" / "raw" / "bank-full.csv", sep=";")
raw = raw.rename(columns={"default": "credit_default", "day": "day_of_month", "month": "month_name"})
raw.insert(0, "row_id", np.arange(1, len(raw) + 1))
con = sqlite3.connect(":memory:")
raw.to_sql("stg_bank_raw", con, index=False)


def split_statements(text):
    text = re.sub(r"--[^\n]*", "", text)
    return [s.strip() for s in text.split(";") if s.strip()]


def run_file(name, label_prefix):
    """Runs every statement. SELECT results are saved as <label>.csv"""
    text = (SQL / name).read_text()
    labels = re.findall(r"^-- ((?:Q|W)\d+b?)\.", text, flags=re.M)
    results, i = {}, 0
    for stmt in split_statements(text):
        if stmt.upper().startswith("SELECT") or stmt.upper().startswith("WITH"):
            df = pd.read_sql_query(stmt, con)
            key = labels[i] if i < len(labels) else f"{label_prefix}{i + 1}"
            results[key] = df
            df.to_csv(OUT / f"{key}.csv", index=False)
            i += 1
        else:
            con.execute(stmt)
    return results


run_file("01_build_model.sql", "M")
q = run_file("02_business_questions.sql", "Q")
w = run_file("03_window_functions.sql", "W")
dq = run_file("04_data_quality_checks.sql", "D")
dq_df = list(dq.values())[0]
dq_df.to_csv(OUT / "data_quality_checks.csv", index=False)

# ----------------------------------------------------------- independent pandas truth
clean = pd.read_csv(ROOT / "data" / "processed" / "bank_customers_clean.csv")
clean["job_key"] = clean.job.str.lower()
tests = []


def check(name, sql_val, pd_val, tol=0.051):
    ok = abs(float(sql_val) - float(pd_val)) <= tol
    tests.append((name, round(float(sql_val), 3), round(float(pd_val), 3), "PASS" if ok else "FAIL"))


check("Customer rows", len(con.execute("SELECT * FROM customers").fetchall()), len(clean), 0)

# Q1 deposit share by job
q1 = q["Q1"]
share = clean.groupby("job_key").balance.sum() / clean.balance.sum() * 100
for job, v in share.items():
    s = q1[(q1.dimension == "Job") & (q1.segment == job)].deposit_share_pct.iloc[0]
    check(f"Q1 deposit share, job = {job}", s, v)

# Q1 deposit share by age group
share = clean.groupby("age_group").balance.sum() / clean.balance.sum() * 100
for g, v in share.items():
    s = q1[(q1.dimension == "Age group") & (q1.segment == g)].deposit_share_pct.iloc[0]
    check(f"Q1 deposit share, age group = {g}", s, v)

# Q3 adoption
q3 = q["Q3"].set_index("product")
check("Q3 housing loan adoption %", q3.loc["Housing loan", "adoption_pct"], clean.housing_loan_flag.mean() * 100)
check("Q3 personal loan adoption %", q3.loc["Personal loan", "adoption_pct"], clean.personal_loan_flag.mean() * 100)
check("Q3 term deposit adoption %", q3.loc["Term deposit", "adoption_pct"], clean.term_deposit_flag.mean() * 100)

# Q4 inactive proxies
q4 = q["Q4"].iloc[0]
check("Q4 zero or negative balance %", q4.pct_zero_or_negative_balance, clean.zero_or_negative_flag.mean() * 100)
check("Q4 no product %", q4.pct_no_product, clean.no_product_flag.mean() * 100)

# Q5 average and median balance by education
q5 = q["Q5"]
for g, sub in clean.groupby("education"):
    row = q5[(q5.dimension == "Education") & (q5.segment == g.lower())].iloc[0]
    check(f"Q5 average balance, education = {g}", row.avg_balance, sub.balance.mean(), 0.51)
    check(f"Q5 median balance, education = {g}", row.median_balance, sub.balance.median(), 0.01)

# Q6 missed sign ups by job
q6 = q["Q6"]
overall = clean.term_deposit_flag.mean()
for job, sub in clean.groupby("job_key"):
    if len(sub) >= 1000 and sub.term_deposit_flag.mean() < overall:
        row = q6[(q6.dimension == "Job") & (q6.segment == job)].iloc[0]
        check(f"Q6 missed sign ups, job = {job}", row.missed_signups, (overall - sub.term_deposit_flag.mean()) * len(sub), 0.51)

# W1 deciles (same rule as NTILE: first buckets take the extra rows)
w1 = w["W1"]
chunks = np.array_split(np.sort(clean.balance.values)[::-1], 10)
tot = clean.balance.sum()
for i, c in enumerate(chunks, start=1):
    check(f"W1 decile {i} balance share %", w1.loc[w1.decile == i, "share_pct"].iloc[0], c.sum() / tot * 100)

# W3 monthly conversion
w3 = w["W3"]
m = clean.groupby("month_num").term_deposit_flag.mean() * 100
for mn, v in m.items():
    check(f"W3 conversion % month {mn}", w3.loc[w3.month_num == mn, "conversion_pct"].iloc[0], v)

res = pd.DataFrame(tests, columns=["test", "sql_value", "pandas_value", "status"])
res.to_csv(ROOT / "data" / "processed" / "sql_vs_pandas_reconciliation.csv", index=False)
print(dq_df.to_string(index=False))
print()
print(res.status.value_counts().to_string())
print(res[res.status == "FAIL"].to_string(index=False) if (res.status == "FAIL").any() else "All reconciliation checks passed.")
