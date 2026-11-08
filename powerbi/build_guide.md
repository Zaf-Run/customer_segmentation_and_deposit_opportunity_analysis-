# Power BI build guide

Power BI files (.pbix) can only be created in Power BI Desktop, so this folder gives you everything to build the report in about 90 minutes: the data model, DAX measures, a theme and a page by page layout. Save the finished file as `powerbi/Bank_Performance_Dashboard.pbix` and add screenshots to `images/`.

## 1. Load the data (Get Data > Text/CSV)

Load these five files from `data/processed/`:

1. `bank_customers_clean.csv` (rename the query `fact_customers`)
2. `dim_age_group.csv`
3. `dim_balance_band.csv`
4. `dim_month.csv`
5. `dim_job.csv`

Power Query checks: set `balance`, `age`, `campaign` to Whole Number. Set every `*_flag` column to Whole Number. Leave text columns as Text. Do not remove any rows.

## 2. Model (Model view)

| From (many) | To (one) | Cardinality | Filter direction |
|---|---|---|---|
| fact_customers[age_group] | dim_age_group[age_group] | Many to one | Single |
| fact_customers[balance_band] | dim_balance_band[balance_band] | Many to one | Single |
| fact_customers[month] | dim_month[month] | Many to one | Single |
| fact_customers[job] | dim_job[job] | Many to one | Single |

Sort by column: `dim_age_group[age_group]` by `sort_order`, `dim_balance_band[balance_band]` by `sort_order`, `dim_month[month]` by `month_num`.
Hide the key columns on the fact table that duplicate dimension columns, and always put dimension columns on visuals.

## 3. Measures

Create a blank table named `Measures` and paste every measure from `measures.dax`. Format percent measures as Percentage with one decimal. Format balance measures as Whole number with thousands separator.

Test the model before drawing anything. With no slicers selected, cards must show: Total Customers 45,211, Total Balance 61,589,682, Avg Balance 1,362, Median 448, Conversion 11.7%, Zero or Negative 16.1%, No Product 31.1%. These match the SQL, Python and Excel results.

## 4. Theme and canvas

View > Themes > Browse for themes > `theme.json`. Canvas 1280 x 720. Use a navy title strip on every page, the same slicer panel on the left, and a footer text box: "Source: bank telemarketing customer file, 45,211 customers. Balance is average yearly balance in EUR."

## 5. Pages

### Page 1: Executive Overview
* Seven cards: Total Customers, Total Balance, Avg Balance, Median Balance, Conversion Rate, Zero or Negative Balance %, No Product %.
* Clustered column: customers and Deposit Share by `balance_band` (shows that a small group holds most of the money).
* Bar: Conversion Rate by `contact` with Bank Conversion as a constant line.
* Text box using `Insight Concentration` and `Insight Conversion`.
* Slicers: age_group, job_group, contact.

### Page 2: Customer Segmentation
* Clustered bar: Customer Share and Deposit Share by `job` (sort by Deposit Share).
* Column: Avg Balance and Median Balance by `age_group`.
* Matrix: `job` rows, `age_group` columns, Avg Balance values, colour scale (white to navy).
* Scatter: X = Balance Index, Y = Conversion Index, Details = `job`, Size = Total Customers. Add constant lines at 1.0. Lower right quadrant is the campaign target zone.
* Slicers: marital, education.

### Page 3: Branch and Campaign Performance (branch proxy)
The file has no branch field, so this page measures the operational units that do exist: channel, month and contact intensity.
* Combo chart by `month`: columns Customer Share and Signup Share, line Conversion Rate. May stands out.
* Column: Conversion Rate by `contacts_band` (1, 2-3, 4-6, 7+).
* Column: Conversion Rate by `poutcome`.
* Table: `job`, `age_group`, Total Customers, Avg Balance, Conversion Rate, Missed Signups, Segment Status. Filter Total Customers >= 500, sort by Missed Signups. Add data bars to Missed Signups.
* Card: Unknown Channel Share.

### Page 4: Product and Deposit Analytics
* Bar: Housing Loan Adoption, Personal Loan Adoption, Term Deposit Adoption (three measures in one visual using a small disconnected table, or three cards).
* Column: customers by `product_count` with Avg Balance as a line.
* Column: Conversion Rate by `housing_loan` and `personal_loan` status.
* Bar: Deposit Share by `education` and by `marital`.
* Card: Top 10 Pct Balance Share.

## 6. Interactions and polish

1. Turn off cross filtering from the cards to other visuals.
2. Add a bookmark called Reset with a button on every page.
3. Add tooltips showing Customers, Avg Balance, Conversion Index.
4. Check each page at 100% zoom. Remove gridlines, keep one accent colour for the story (orange for the underperforming item).
5. Take one screenshot per page into `images/` and link them in the main README.

## 7. Final test list

1. Page 1 cards match the reference values above.
2. Select job = Blue Collar: Conversion Rate shows 7.3%, Missed Signups shows 430.
3. Select month = May: customers 13,766, conversion 6.7%.
4. Clear all slicers with the Reset bookmark.
