"""
04_build_excel.py
Builds excel/Bank_Customer_Analytics.xlsx. Cleaning columns and every KPI are live Excel
formulas that read the Data sheet. Run: python python/04_build_excel.py  then recalculate
(LibreOffice or open in Excel).
"""
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

ROOT = Path(__file__).resolve().parents[1]
raw = pd.read_csv(ROOT / "data" / "raw" / "bank-full.csv", sep=";")
N = len(raw)
LAST = N + 1  # last data row

F = "Arial"
NAVY = "1F3A5F"
hdr_font = Font(name=F, bold=True, color="FFFFFF", size=10)
hdr_fill = PatternFill("solid", start_color=NAVY)
base = Font(name=F, size=10)
bold = Font(name=F, size=10, bold=True)
blue = Font(name=F, size=10, color="0000FF")
green = Font(name=F, size=10, color="008000")
title_font = Font(name=F, size=14, bold=True, color=NAVY)
note_font = Font(name=F, size=9, italic=True, color="595959")
yellow = PatternFill("solid", start_color="FFFF00")
thin = Side(style="thin", color="D0D5DB")
box = Border(top=thin, bottom=thin, left=thin, right=thin)

PCT, INT, EUR, DEC2 = "0.0%", "#,##0;(#,##0);-", "#,##0;(#,##0);-", "0.00"

wb = Workbook()


def header(ws, row, labels, col=1):
    for i, t in enumerate(labels):
        c = ws.cell(row=row, column=col + i, value=t)
        c.font, c.fill, c.border = hdr_font, hdr_fill, box
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 32


def put(ws, ref, value, font=base, fmt=None, fill=None):
    c = ws[ref]
    c.value = value
    c.font = font
    c.border = box
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    return c


def widths(ws, w):
    for i, x in enumerate(w, start=1):
        ws.column_dimensions[get_column_letter(i)].width = x


def rng(col):
    return f"Data!${col}$2:${col}${LAST}"


# ============================================================ README
ws = wb.active
ws.title = "README"
ws["A1"] = "Bank Customer and Deposit Analytics: Excel workbook"
ws["A1"].font = title_font
lines = [
    ("Purpose", "Data cleaning, KPI calculation and segment analysis for a retail bank customer file (45,211 customers)."),
    ("Source", "data/raw/bank-full.csv, a bank telemarketing file with one row per customer. It has no branch, no transaction history and no product catalogue."),
    ("Deposit proxy", "Balance is the average yearly balance in EUR. It is used as the deposit measure. Negative balances are kept in net totals."),
    ("Activity proxies", "Inactive is proxied two ways: balance of zero or below, and holding none of the three product flags (housing loan, personal loan, term deposit)."),
    ("Acquisition", "A term deposit sign up (column y = yes) is treated as a customer acquisition win for the campaign."),
    ("", ""),
    ("Sheet guide", ""),
    ("Data", "Raw columns A to M plus formula columns N to U that clean and classify each customer."),
    ("Lookups", "Age group, balance band and contact intensity rules. Blue cells are inputs: change a boundary and every sheet updates."),
    ("KPIs", "Headline measures for the Executive Overview page."),
    ("Segments", "Customers, deposits, balances, conversion and missed sign ups by age group, job, marital status, education and balance band."),
    ("Channel_Month", "Campaign performance by contact channel, month and number of contacts."),
    ("Products", "Product adoption and products held per customer."),
    ("Scenario", "Campaign uplift scenario. Yellow cells are assumptions, not data."),
    ("Validation", "Excel results compared with the Python and SQL results."),
    ("", ""),
    ("Colour code", "Blue text = input. Black = formula. Green = link to another sheet. Yellow fill = assumption to review."),
    ("Pivot tables", "Select any cell in Data, choose Insert > PivotTable, and rebuild the Segments views by dragging job, age_group or balance_band to Rows. Sum of balance and Count of customer_id to Values."),
    ("Cleaning in Excel", 'N job_clean: PROPER(SUBSTITUTE(SUBSTITUTE(TRIM(job),"-"," "),".","")). O, P, U: approximate match LOOKUP against the Lookups sheet. Q to T: flags and product count.'),
]
for i, (a, b) in enumerate(lines, start=3):
    ws.cell(row=i, column=1, value=a).font = bold
    c = ws.cell(row=i, column=2, value=b)
    c.font = base
    c.alignment = Alignment(wrap_text=True, vertical="top")
widths(ws, [20, 120])

# ============================================================ Lookups
lk = wb.create_sheet("Lookups")
lk["A1"] = "Classification rules (inputs)"
lk["A1"].font = title_font
header(lk, 3, ["age_min", "age_max", "age_group"])
for i, (a, b, g) in enumerate([(18, 24, "18-24"), (25, 34, "25-34"), (35, 44, "35-44"),
                               (45, 54, "45-54"), (55, 64, "55-64"), (65, 120, "65+")], start=4):
    put(lk, f"A{i}", a, blue); put(lk, f"B{i}", b, blue); put(lk, f"C{i}", g, blue)
header(lk, 12, ["balance_min (EUR)", "balance_max (EUR)", "balance_band"])
for i, (a, b, g) in enumerate([(-100000, -1, "1 Overdrawn"), (0, 0, "2 Zero"), (1, 500, "3 Low (1-500)"),
                               (501, 1500, "4 Medium (501-1500)"), (1501, 5000, "5 High (1501-5000)"),
                               (5001, 1000000, "6 Very high (5000+)")], start=13):
    put(lk, f"A{i}", a, blue, "#,##0;(#,##0);0"); put(lk, f"B{i}", b, blue, "#,##0;(#,##0);0"); put(lk, f"C{i}", g, blue)
header(lk, 21, ["contacts_min", "contacts_band"])
for i, (a, g) in enumerate([(1, "1"), (2, "2-3"), (4, "4-6"), (7, "7+")], start=22):
    put(lk, f"A{i}", a, blue); put(lk, f"B{i}", g, blue)
lk["A28"] = "Lookups use approximate match, so the min column must stay in ascending order. The max column is for reading only."
lk["A28"].font = note_font
widths(lk, [18, 18, 24])

# ============================================================ Data
d = wb.create_sheet("Data")
cols = ["customer_id", "age", "job", "marital", "education", "balance", "housing", "loan", "contact",
        "month", "campaign", "poutcome", "y",
        "job_clean", "age_group", "balance_band", "term_deposit_flag", "product_count",
        "no_product_flag", "zero_or_negative_flag", "contacts_band"]
header(d, 1, cols)
src = raw[["age", "job", "marital", "education", "balance", "housing", "loan", "contact", "month", "campaign", "poutcome", "y"]]
for r, row in enumerate(src.itertuples(index=False), start=2):
    d.cell(row=r, column=1, value=r - 1)
    for c, v in enumerate(row, start=2):
        d.cell(row=r, column=c, value=v)
    d.cell(row=r, column=14, value=f'=PROPER(SUBSTITUTE(SUBSTITUTE(TRIM(C{r}),"-"," "),".",""))')
    d.cell(row=r, column=15, value=f"=LOOKUP(B{r},Lookups!$A$4:$A$9,Lookups!$C$4:$C$9)")
    d.cell(row=r, column=16, value=f"=LOOKUP(F{r},Lookups!$A$13:$A$18,Lookups!$C$13:$C$18)")
    d.cell(row=r, column=17, value=f'=IF(M{r}="yes",1,0)')
    d.cell(row=r, column=18, value=f'=(G{r}="yes")+(H{r}="yes")+(M{r}="yes")')
    d.cell(row=r, column=19, value=f"=IF(R{r}=0,1,0)")
    d.cell(row=r, column=20, value=f"=IF(F{r}<=0,1,0)")
    d.cell(row=r, column=21, value=f"=LOOKUP(K{r},Lookups!$A$22:$A$25,Lookups!$B$22:$B$25)")
d.freeze_panes = "A2"
widths(d, [11, 6, 14, 10, 11, 9, 8, 7, 10, 7, 9, 10, 5, 14, 10, 20, 10, 10, 10, 12, 10])
tab = Table(displayName="tblCustomers", ref=f"A1:U{LAST}")
tab.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=False)
d.add_table(tab)

# ============================================================ KPIs
k = wb.create_sheet("KPIs")
k["A1"] = "Executive KPIs"; k["A1"].font = title_font
header(k, 3, ["Measure", "Value", "How it is calculated"])
kp = [
    ("Total customers", f"=COUNT({rng('A')})", INT, "Count of customer_id"),
    ("Total balance (EUR)", f"=SUM({rng('F')})", EUR, "Sum of average yearly balance, negatives included"),
    ("Average balance (EUR)", "=B5/B4", EUR, "Total balance divided by customers"),
    ("Median balance (EUR)", f"=MEDIAN({rng('F')})", EUR, "Middle customer. Lower than the average because a few large balances pull the mean up"),
    ("Term deposit sign ups", f"=SUM({rng('Q')})", INT, "Customers with y = yes"),
    ("Term deposit conversion", "=B8/B4", PCT, "Sign ups divided by customers contacted"),
    ("Zero or negative balance, % of customers", f"=SUM({rng('T')})/B4", PCT, "Inactivity proxy 1"),
    ("Overdrawn (negative balance), % of customers", f'=COUNTIF({rng("F")},"<0")/B4', PCT, "Subset of proxy 1"),
    ("No product held, % of customers", f"=SUM({rng('S')})/B4", PCT, "Inactivity proxy 2: no housing loan, no personal loan, no term deposit"),
    ("Holds two or more products, % of customers", f'=COUNTIF({rng("R")},">=2")/B4', PCT, "Cross sell depth"),
    ("Customers with a previous campaign contact, %", f'=1-COUNTIF({rng("L")},"unknown")/B4', PCT, "poutcome is not unknown"),
]
for i, (m, f, fmt, how) in enumerate(kp, start=4):
    put(k, f"A{i}", m, bold); put(k, f"B{i}", f, base, fmt); put(k, f"C{i}", how, note_font)
widths(k, [48, 16, 90])

# ============================================================ Segments
s = wb.create_sheet("Segments")
s["A1"] = "Segment performance"; s["A1"].font = title_font
s["A2"] = ("Conversion index = segment conversion / bank conversion. Balance index = segment average / bank average. "
           "Missed sign ups = (bank conversion minus segment conversion) x customers, shown only where the segment is below the bank rate.")
s["A2"].font = note_font
header(s, 4, ["Dimension", "Segment", "Customers", "Customer share", "Total balance (EUR)", "Deposit share",
              "Average balance (EUR)", "Term deposit sign ups", "Conversion", "Conversion index",
              "Balance index", "Missed sign ups", "Zero or negative balance %", "No product %"])
clean = pd.read_csv(ROOT / "data" / "processed" / "bank_customers_clean.csv")
blocks = [
    ("Age group", "O", ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]),
    ("Job", "N", list(clean.groupby("job").balance.sum().sort_values(ascending=False).index)),
    ("Marital status", "D", ["married", "single", "divorced"]),
    ("Education", "E", ["tertiary", "secondary", "primary", "unknown"]),
    ("Balance band", "P", sorted(clean.balance_band.unique())),
]
row = 5
seg_rows = {}
for dim, col, labels in blocks:
    r0, r1 = row, row + len(labels) - 1
    for lab in labels:
        put(s, f"A{row}", dim, base); put(s, f"B{row}", lab, base)
        put(s, f"C{row}", f"=COUNTIFS({rng(col)},$B{row})", base, INT)
        put(s, f"D{row}", f"=C{row}/SUM($C${r0}:$C${r1})", base, PCT)
        put(s, f"E{row}", f"=SUMIFS({rng('F')},{rng(col)},$B{row})", base, EUR)
        put(s, f"F{row}", f"=E{row}/SUM($E${r0}:$E${r1})", base, PCT)
        put(s, f"G{row}", f"=IF(C{row}=0,0,E{row}/C{row})", base, EUR)
        put(s, f"H{row}", f"=SUMIFS({rng('Q')},{rng(col)},$B{row})", base, INT)
        put(s, f"I{row}", f"=IF(C{row}=0,0,H{row}/C{row})", base, PCT)
        put(s, f"J{row}", f"=I{row}/KPIs!$B$9", green, DEC2)
        put(s, f"K{row}", f"=G{row}/KPIs!$B$6", green, DEC2)
        put(s, f"L{row}", f"=IF(I{row}<KPIs!$B$9,(KPIs!$B$9-I{row})*C{row},0)", green, INT)
        put(s, f"M{row}", f"=SUMIFS({rng('T')},{rng(col)},$B{row})/C{row}", base, PCT)
        put(s, f"N{row}", f"=SUMIFS({rng('S')},{rng(col)},$B{row})/C{row}", base, PCT)
        seg_rows[(dim, lab)] = row
        row += 1
    row += 1
s.freeze_panes = "C5"
widths(s, [16, 22, 11, 11, 16, 11, 14, 14, 11, 11, 11, 12, 14, 11])

# ============================================================ Channel_Month
cm = wb.create_sheet("Channel_Month")
cm["A1"] = "Campaign performance: channel, month, contact intensity"; cm["A1"].font = title_font
cm["A2"] = "The file has no year, so months are pooled across the campaign period. Read this as seasonality, not a trend."
cm["A2"].font = note_font


def table(start, title, col, labels, display=None):
    cm.cell(row=start, column=1, value=title).font = bold
    header(cm, start + 1, ["Value", "Customers contacted", "Share of contacts", "Sign ups", "Share of sign ups", "Conversion", "Conversion index"])
    r0, r1 = start + 2, start + 1 + len(labels)
    for i, lab in enumerate(labels):
        r = r0 + i
        put(cm, f"A{r}", lab, base)
        put(cm, f"B{r}", f"=COUNTIFS({rng(col)},$A{r})", base, INT)
        put(cm, f"C{r}", f"=B{r}/SUM($B${r0}:$B${r1})", base, PCT)
        put(cm, f"D{r}", f"=SUMIFS({rng('Q')},{rng(col)},$A{r})", base, INT)
        put(cm, f"E{r}", f"=D{r}/SUM($D${r0}:$D${r1})", base, PCT)
        put(cm, f"F{r}", f"=IF(B{r}=0,0,D{r}/B{r})", base, PCT)
        put(cm, f"G{r}", f"=F{r}/KPIs!$B$9", green, DEC2)
    return r1 + 2


nxt = table(4, "By contact channel", "I", ["cellular", "telephone", "unknown"])
month_start = nxt
nxt = table(nxt, "By month", "J", ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])
nxt = table(nxt, "By contacts made in this campaign", "U", ["1", "2-3", "4-6", "7+"])
nxt = table(nxt, "By outcome of the previous campaign", "L", ["success", "failure", "other", "unknown"])
widths(cm, [20, 18, 15, 12, 15, 12, 15])

# ============================================================ Products
p = wb.create_sheet("Products")
p["A1"] = "Product adoption"; p["A1"].font = title_font
header(p, 3, ["Product", "Holders", "Adoption", "Conversion of holders"])
prods = [("Housing loan", "G"), ("Personal loan", "H"), ("Term deposit", "M")]
for i, (nm, col) in enumerate(prods, start=4):
    put(p, f"A{i}", nm, bold)
    put(p, f"B{i}", f'=COUNTIF({rng(col)},"yes")', base, INT)
    put(p, f"C{i}", f"=B{i}/KPIs!$B$4", green, PCT)
    if nm == "Term deposit":
        put(p, f"D{i}", "n/a (is the outcome)", note_font)
    else:
        put(p, f"D{i}", f'=IF(B{i}=0,0,SUMIFS({rng("Q")},{rng(col)},"yes")/B{i})', base, PCT)
p["A9"] = "Products held per customer"; p["A9"].font = bold
header(p, 10, ["Products held", "Customers", "Share", "Average balance (EUR)"])
for i, n_ in enumerate(range(0, 4), start=11):
    put(p, f"A{i}", n_, base)
    put(p, f"B{i}", f"=COUNTIFS({rng('R')},$A{i})", base, INT)
    put(p, f"C{i}", f"=B{i}/KPIs!$B$4", green, PCT)
    put(p, f"D{i}", f"=IF(B{i}=0,0,SUMIFS({rng('F')},{rng('R')},$A{i})/B{i})", base, EUR)
p["A16"] = ("Savings, current accounts, fixed deposits and cards are not in this file. Term deposit is the only deposit product observed "
            "and is the campaign outcome, so adoption here means campaign uptake.")
p["A16"].font = note_font
widths(p, [34, 14, 12, 22])

# ============================================================ Scenario
sc = wb.create_sheet("Scenario")
sc["A1"] = "Campaign uplift scenario"; sc["A1"].font = title_font
sc["A2"] = "Yellow cells are assumptions. They are not in the data. Replace them with the bank's own figures."
sc["A2"].font = note_font
put(sc, "A4", "Share of the conversion gap closed by a targeted campaign", bold)
put(sc, "B4", 0.5, blue, PCT, yellow)
put(sc, "A5", "Average term deposit size per sign up (EUR), illustrative placeholder", bold)
put(sc, "B5", 1000, blue, EUR, yellow)
header(sc, 7, ["Target segment", "Customers", "Current conversion", "Bank conversion", "Gap (points)",
               "Extra sign ups", "Illustrative extra deposits (EUR)", "Balance index"])
targets = [("Job", "Blue Collar"), ("Job", "Services"), ("Job", "Entrepreneur"),
           ("Age group", "45-54"), ("Education", "primary")]
for i, key in enumerate(targets, start=8):
    r = seg_rows[key]
    put(sc, f"A{i}", f"{key[0]}: {key[1]}", base)
    put(sc, f"B{i}", f"=Segments!C{r}", green, INT)
    put(sc, f"C{i}", f"=Segments!I{r}", green, PCT)
    put(sc, f"D{i}", "=KPIs!$B$9", green, PCT)
    put(sc, f"E{i}", f"=MAX(D{i}-C{i},0)*100", base, "0.0")
    put(sc, f"F{i}", f"=B{i}*MAX(D{i}-C{i},0)*$B$4", base, INT)
    put(sc, f"G{i}", f"=F{i}*$B$5", base, EUR)
    put(sc, f"H{i}", f"=Segments!K{r}", green, DEC2)
put(sc, "A13", "Total", bold)
put(sc, "F13", "=SUM(F8:F12)", bold, INT)
put(sc, "G13", "=SUM(G8:G12)", bold, EUR)
sc["A15"] = "Segments overlap (a customer can be blue collar and in 45-54), so the total is an upper bound, not an additive forecast."
sc["A15"].font = note_font
widths(sc, [58, 12, 18, 16, 13, 14, 28, 13])

# ============================================================ Validation
v = wb.create_sheet("Validation")
v["A1"] = "Excel versus Python and SQL"; v["A1"].font = title_font
header(v, 3, ["Check", "Excel", "Python reference", "Difference", "Status"])
ref = {
    "Customers": (N, "=KPIs!B4"),
    "Total balance (EUR)": (int(clean.balance.sum()), "=KPIs!B5"),
    "Term deposit sign ups": (int(clean.term_deposit_flag.sum()), "=KPIs!B8"),
    "Median balance (EUR)": (float(clean.balance.median()), "=KPIs!B7"),
    "Zero or negative balance customers": (int(clean.zero_or_negative_flag.sum()), "=KPIs!B10*KPIs!B4"),
    "No product customers": (int(clean.no_product_flag.sum()), "=KPIs!B12*KPIs!B4"),
    "Management total balance (EUR)": (int(clean[clean.job == "Management"].balance.sum()), f"=Segments!E{seg_rows[('Job', 'Management')]}"),
    "Blue collar sign ups": (int(clean[clean.job == "Blue Collar"].term_deposit_flag.sum()), f"=Segments!H{seg_rows[('Job', 'Blue Collar')]}"),
    "May contacts": (int((clean.month == "May").sum()), f"=Channel_Month!B{month_start + 2 + 4}"),
}
for i, (name, (pyv, xl)) in enumerate(ref.items(), start=4):
    put(v, f"A{i}", name, base)
    put(v, f"B{i}", xl, green, "#,##0.0")
    put(v, f"C{i}", pyv, blue, "#,##0.0")
    put(v, f"D{i}", f"=B{i}-C{i}", base, "#,##0.0;(#,##0.0);-")
    put(v, f"E{i}", f'=IF(ABS(D{i})<0.5,"PASS","CHECK")', bold)
v["A14"] = "Python reference values come from python/01_clean_validate_export.py output (data/processed/bank_customers_clean.csv)."
v["A14"].font = note_font
widths(v, [40, 16, 18, 14, 10])

out = ROOT / "excel" / "Bank_Customer_Analytics.xlsx"
out.parent.mkdir(exist_ok=True)
wb.save(out)
print("saved", out)
