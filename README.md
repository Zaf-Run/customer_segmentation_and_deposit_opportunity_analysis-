# Bank Customer and Deposit Analytics

Customer segmentation, deposit and product analytics for a retail bank. Built with MySQL, Excel, Python and Power BI. Aimed at entry level analyst roles in banking, fintech and payments.

## Business scenario

A commercial bank wants to know which customer segments hold the most deposits, which products and channels perform, and where customer engagement can improve. This project analyses 45,211 customers and turns the results into campaign recommendations.

## Important note on scope

The supplied file is a bank telemarketing dataset. It has no branch, transaction, income or year fields. I did not invent them. The project answers what the data supports, uses clearly labelled proxies where needed, and lists the gaps in `docs/limitations.md`.

| Brief asked | What this project does |
|---|---|
| Branch performance | Not answerable. Page 3 covers channel, month and contact intensity instead |
| Income segments | Job and balance bands |
| Active versus inactive | Proxies: zero or negative balance (16.1%), no product held (31.1%) |
| Savings, current, fixed deposit, card adoption | Housing loan, personal loan, term deposit |
| Deposits | Average yearly balance (EUR) |

## Headline findings

1. The top 10% of customers hold 56% of positive balances.
2. Management holds 27% of balances from 21% of customers. Blue collar holds 17% from 21.5% and converts at 7.3% against a bank rate of 11.7%.
3. Entrepreneurs and ages 45 to 54 have above average balances and below average term deposit uptake. They are the main campaign target.
4. 28.8% of contacts have no recorded channel and convert at 4.1%. Cellular converts at 14.9%.
5. May carries 30.4% of contacts but 17.5% of sign ups.
6. Customers who accepted a previous offer accept again at 64.7%.

Full tables and seven recommendations: `docs/findings_and_recommendations.md`.

![Deposit share by job](images/01_deposit_share_by_job.png)
![Month contacts versus sign ups](images/02_month_contacts_vs_signups.png)
![Opportunity quadrant](images/05_opportunity_quadrant.png)

## Repository structure

| Folder | Contents |
|---|---|
| data/raw | Original bank-full.csv |
| data/processed | Clean table, dimension tables for Power BI, validation report, SQL results, statistical tests, segment summary |
| sql | 00 load (MySQL), 01 model build, 02 business questions, 03 window functions, 04 data quality checks |
| python | 01 clean and validate, 02 run SQL and reconcile, 03 tests and charts, 04 build Excel |
| excel | Bank_Customer_Analytics.xlsx with live formulas |
| powerbi | DAX measures, theme and step by step build guide for the four page dashboard |
| docs | Findings, limitations, data dictionary, CV bullets |
| images | Charts used above |

## How to reproduce

Python path (no database needed):

1. `pip install -r requirements.txt`
2. `python python/01_clean_validate_export.py`
3. `python python/02_run_sql_and_reconcile.py` runs all SQL on SQLite and checks it against pandas
4. `python python/03_stats_and_charts.py`
5. `python python/04_build_excel.py` then open the file in Excel (formulas calculate on open)

MySQL path: run `sql/00_load_mysql.sql` to `sql/04_data_quality_checks.sql` in order in MySQL 8.

Power BI: follow `powerbi/build_guide.md`.

## Methods and validation

1. 17 data checks (nulls, duplicates, ranges, code consistency, unknown values, outliers).
2. SQL uses CTEs, range joins, NTILE, RANK, LAG, running totals and a portable median.
3. 59 SQL values reconciled to independent pandas calculations: 59 pass, 0 fail.
4. Excel has 362,293 formulas, zero errors, and a Validation sheet that matches Python on 9 checks.
5. Two proportion z tests and Wilson intervals on the main conversion gaps. Bootstrap intervals on average balance by job.

## Tools

MySQL 8, Excel, Python (pandas, numpy, scipy, matplotlib, openpyxl), Power BI.

## Data source

The file matches the public UCI Bank Marketing dataset from a Portuguese bank: S. Moro, P. Cortez, P. Rita (2014), A data driven approach to predict the success of bank telemarketing, Decision Support Systems.
