# CV bullets, GitHub summary and interview talking points

## CV bullets (pick three)

* Analysed 45,211 bank customers with MySQL, Excel and Python to find which segments drive deposits and term deposit uptake. Showed that the top 10% of customers hold 56% of positive balances.
* Wrote SQL with CTEs, range joins and window functions (NTILE, RANK, LAG, running totals). Reconciled 59 SQL results against independent pandas calculations with zero differences.
* Found that May carried 30% of campaign contacts but 17.5% of sign ups, and that contacts with no recorded channel converted at 4.1% against 14.9% on cellular. Tested with two proportion z tests.
* Built a formula driven Excel workbook (360,000 formulas, zero errors) and a four page Power BI dashboard with 25 DAX measures. Recommended a deposit campaign for high balance, low conversion segments.

## GitHub repository description

Customer segmentation, deposit and product analytics for a retail bank using MySQL, Excel, Python and Power BI. Includes reproducible SQL, validation checks, statistical tests and business recommendations.

## Interview talking points

1. Why did you change the brief? The file had no branch, transaction or income fields. I kept to what the data supports, documented the gaps and used proxies that I label as proxies.
2. How do you define inactive? Two proxies, zero or negative balance and no product held. A real definition needs transaction dates and would replace both.
3. Why report the median? Balances are skewed. The mean is 1,362 and the median is 448.
4. How do you know the findings are not noise? Two proportion z tests and Wilson intervals on every headline gap. Segment sizes are shown next to every rate.
5. What would you not claim? That fewer calls cause better conversion or that May is a bad month. Both are associations from a campaign the bank chose how to run.
6. How did you check the SQL? I ran it on SQLite and compared 59 values with pandas. MySQL 8 syntax is kept portable.
7. What would you do with branch data? The same logic: deposits per branch, customers per branch, and an index of deposits per customer against the bank average to flag underperformers.
