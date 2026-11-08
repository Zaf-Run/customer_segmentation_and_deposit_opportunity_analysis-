"""
03_stats_and_charts.py
Statistical validation of the headline findings (two proportion z tests, Wilson
confidence intervals, bootstrap intervals) and the charts used in the README.

Run from the project root:  python python/03_stats_and_charts.py
Needs: pandas, numpy, scipy, matplotlib
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
IMG = ROOT / "images"
IMG.mkdir(exist_ok=True)
df = pd.read_csv(PROC / "bank_customers_clean.csv")
rng = np.random.default_rng(42)

NAVY, TEAL, ORANGE, GREY = "#1F3A5F", "#2A9D8F", "#E76F51", "#9AA5B1"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titlesize": 12, "axes.titleweight": "bold", "figure.dpi": 130})


# ------------------------------------------------------------ helpers
def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def two_prop(mask, label, note):
    a, b = df[mask], df[~mask]
    k1, n1, k2, n2 = a.term_deposit_flag.sum(), len(a), b.term_deposit_flag.sum(), len(b)
    p1, p2 = k1 / n1, k2 / n2
    pp = (k1 + k2) / (n1 + n2)
    z = (p1 - p2) / np.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    pval = 2 * (1 - stats.norm.cdf(abs(z)))
    lo, hi = wilson(k1, n1)
    return dict(comparison=label, group_customers=n1, group_conversion_pct=round(p1 * 100, 1),
                ci95_low=round(lo * 100, 1), ci95_high=round(hi * 100, 1),
                rest_conversion_pct=round(p2 * 100, 1), difference_pts=round((p1 - p2) * 100, 1),
                z=round(z, 1), p_value="<0.0001" if pval < 1e-4 else round(pval, 4),
                significant_at_5pct=bool(pval < 0.05), note=note)


tests = pd.DataFrame([
    two_prop(df.contact == "Cellular", "Cellular vs all other channels", "Channel quality"),
    two_prop(df.contact == "Unknown", "Unknown channel vs the rest", "Channel not recorded"),
    two_prop(df.month == "May", "May contacts vs other months", "Timing"),
    two_prop(df.job == "Blue Collar", "Blue collar vs other jobs", "Segment"),
    two_prop(df.job == "Retired", "Retired vs other jobs", "Segment"),
    two_prop(df.age_group == "65+", "Age 65+ vs younger", "Segment"),
    two_prop(df.poutcome == "Success", "Previous campaign success vs the rest", "Warm leads"),
    two_prop(df.housing_loan_flag == 1, "Housing loan holders vs non holders", "Cross sell"),
    two_prop(df.campaign >= 7, "7+ contacts vs fewer", "Contact pressure"),
])
tests.to_csv(PROC / "statistical_tests.csv", index=False)

# bootstrap 95% interval for the average balance of the main job segments
rows = []
for job, sub in df.groupby("job"):
    v = sub.balance.values
    boots = [rng.choice(v, len(v)).mean() for _ in range(1000)]
    rows.append(dict(job=job, customers=len(v), avg_balance=round(v.mean()), median_balance=round(np.median(v)),
                     ci95_low=round(np.percentile(boots, 2.5)), ci95_high=round(np.percentile(boots, 97.5))))
boot = pd.DataFrame(rows).sort_values("avg_balance", ascending=False)
boot.to_csv(PROC / "bootstrap_avg_balance_by_job.csv", index=False)

# contact intensity and balance band tables for the findings
intensity = df.groupby("contacts_band").agg(customers=("term_deposit_flag", "size"),
                                            conversion_pct=("term_deposit_flag", lambda s: round(s.mean() * 100, 1)))
intensity.to_csv(PROC / "conversion_by_contact_intensity.csv")

# segment summary table (also handy for Power BI sanity checks)
frames = []
for dim, col in [("Age group", "age_group"), ("Job", "job"), ("Marital status", "marital"),
                 ("Education", "education"), ("Balance band", "balance_band")]:
    g = df.groupby(col).agg(customers=("customer_id", "size"), total_balance=("balance", "sum"),
                            avg_balance=("balance", "mean"), median_balance=("balance", "median"),
                            term_deposits=("term_deposit_flag", "sum"),
                            conversion=("term_deposit_flag", "mean"),
                            zero_or_negative=("zero_or_negative_flag", "mean"),
                            no_product=("no_product_flag", "mean")).reset_index().rename(columns={col: "segment"})
    g.insert(0, "dimension", dim)
    g["deposit_share"] = g.total_balance / df.balance.sum()
    g["customer_share"] = g.customers / len(df)
    g["conversion_index"] = g.conversion / df.term_deposit_flag.mean()
    g["balance_index"] = g.avg_balance / df.balance.mean()
    g["missed_signups"] = (df.term_deposit_flag.mean() - g.conversion) * g.customers
    frames.append(g)
seg = pd.concat(frames)
seg.round(4).to_csv(PROC / "segment_summary.csv", index=False)

# ------------------------------------------------------------ charts
# 1 deposit share vs customer share by job
j = seg[seg.dimension == "Job"].sort_values("deposit_share")
fig, ax = plt.subplots(figsize=(8, 5))
y = np.arange(len(j))
ax.barh(y + 0.2, j.deposit_share * 100, 0.4, color=NAVY, label="Share of total balance")
ax.barh(y - 0.2, j.customer_share * 100, 0.4, color=GREY, label="Share of customers")
ax.set_yticks(y, j.segment)
ax.set_xlabel("Percent")
ax.set_title("Management holds 27% of balances from 21% of customers")
ax.legend(frameon=False, loc="lower right")
fig.tight_layout(); fig.savefig(IMG / "01_deposit_share_by_job.png"); plt.close(fig)

# 2 month: share of contacts vs share of sign ups
m = df.groupby("month_num").agg(contacts=("customer_id", "size"), signups=("term_deposit_flag", "sum")).reset_index()
names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
fig, ax = plt.subplots(figsize=(9, 4.5))
x = np.arange(12)
ax.bar(x - 0.2, m.contacts / m.contacts.sum() * 100, 0.4, color=GREY, label="Share of contacts")
ax.bar(x + 0.2, m.signups / m.signups.sum() * 100, 0.4, color=TEAL, label="Share of term deposit sign ups")
ax.set_xticks(x, names); ax.set_ylabel("Percent")
ax.set_title("May takes 30% of contacts but delivers 17.5% of sign ups")
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(IMG / "02_month_contacts_vs_signups.png"); plt.close(fig)

# 3 conversion by channel
c = df.groupby("contact").term_deposit_flag.agg(["mean", "size", "sum"]).sort_values("mean")
fig, ax = plt.subplots(figsize=(6.5, 3.8))
bars = ax.barh(c.index, c["mean"] * 100, color=[ORANGE, TEAL, NAVY])
for b_, (k, n) in zip(bars, zip(c["sum"], c["size"])):
    ax.text(b_.get_width() + 0.3, b_.get_y() + b_.get_height() / 2, f"{b_.get_width():.1f}%  (n={n:,})", va="center")
ax.set_xlim(0, 19); ax.set_xlabel("Term deposit conversion, %")
ax.set_title("Contacts with no recorded channel convert at 4.1%")
fig.tight_layout(); fig.savefig(IMG / "03_conversion_by_channel.png"); plt.close(fig)

# 4 Pareto of balances by decile (positive balances only so the curve is readable)
pos = np.sort(df.balance_positive.values)[::-1]
chunks = np.array_split(pos, 10)
share = np.array([c_.sum() for c_ in chunks]) / pos.sum() * 100
fig, ax = plt.subplots(figsize=(7.5, 4.3))
ax.bar(range(1, 11), share, color=NAVY)
ax2 = ax.twinx(); ax2.plot(range(1, 11), np.cumsum(share), color=ORANGE, marker="o")
ax2.set_ylim(0, 105); ax2.spines["right"].set_visible(True); ax2.set_ylabel("Cumulative %")
ax.set_xlabel("Customer decile by balance (1 = highest)"); ax.set_ylabel("Share of balances, %")
ax.set_xticks(range(1, 11))
ax.set_title(f"Top 10% of customers hold {share[0]:.0f}% of positive balances")
fig.tight_layout(); fig.savefig(IMG / "04_deposit_concentration.png"); plt.close(fig)

# 5 opportunity quadrant: conversion index vs balance index
s = seg[(seg.dimension.isin(["Job", "Age group", "Education", "Marital status"])) & (seg.customers >= 800)]
fig, ax = plt.subplots(figsize=(8.5, 6))
ax.axhline(1, color=GREY, lw=1); ax.axvline(1, color=GREY, lw=1)
ax.scatter(s.balance_index, s.conversion_index, s=s.customers / 40, color=NAVY, alpha=0.55)
for _, r in s.iterrows():
    ax.annotate(r.segment, (r.balance_index, r.conversion_index), fontsize=7.5, xytext=(4, 4), textcoords="offset points")
ax.set_xlabel("Average balance index (1.0 = bank average)"); ax.set_ylabel("Conversion index (1.0 = bank average)")
ax.text(1.55, 0.62, "Lower right: above average balance,\nbelow average conversion\n= deposit campaign target", color=ORANGE, fontsize=9, fontweight="bold")
ax.set_xlim(0.6, 2.2)
ax.set_title("Where balance is high but term deposit uptake is low")
fig.tight_layout(); fig.savefig(IMG / "05_opportunity_quadrant.png"); plt.close(fig)

print(tests[["comparison", "group_conversion_pct", "rest_conversion_pct", "difference_pts", "z", "p_value"]].to_string(index=False))
print()
print(boot.to_string(index=False))
print()
print(intensity.to_string())
print("\nCharts saved to", IMG)
