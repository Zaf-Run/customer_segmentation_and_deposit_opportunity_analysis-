# Data limits and how they were handled

The brief assumed branch, transaction and product account data. The supplied file is a bank telemarketing customer file with 45,211 rows and 17 columns. It matches the public UCI Bank Marketing dataset from a Portuguese bank (Moro, Cortez and Rita, 2014, Decision Support Systems). Credit the source if you publish this project.

| Brief asked for | In the file? | What this project does instead |
|---|---|---|
| Branch deposits, customers per branch, branch acquisition | No branch field | Not answered. Page 3 uses channel, month and contact intensity as the operating view. No branch data was invented. |
| Income segments | No income | Balance bands and job as wealth proxies |
| Transaction frequency, active versus inactive | No transactions | Two proxies: balance of zero or below, and holding no product |
| Savings, current, fixed deposit, card adoption | Only housing loan, personal loan, term deposit, default flag | Adoption of those three products |
| Deposits | Average yearly balance in EUR | Balance used as deposit proxy |
| Activity trends over time | Month and day only, no year | Seasonality by month, not a trend |
| Customer acquisition | Term deposit sign up in a campaign | Sign up conversion treated as acquisition win |

## Other cautions

1. Customers are people who were contacted by a campaign, not the whole customer base.
2. Conversion differences are associations. Months, channels and call counts were chosen by the bank, so they are not clean experiments. Hard prospects are called more often, which can make heavy contact look worse than it is.
3. Small months (March, September, October, December) hold 4.4% of contacts, so their high conversion rates need testing before any decision.
4. Balances are skewed. The mean is 1,362 and the median 448, so medians are reported next to averages.
5. Balance outliers (10.5% beyond 1.5 times IQR) are kept and flagged, because large balances are real customers in a deposit analysis.
6. Unknown values (job 0.6%, education 4.1%, channel 28.8%, previous outcome 81.7%) are kept as their own category. Dropping them would bias the results.
7. The call duration column was not used. It is only known after the call ends, so it cannot guide a campaign.
8. customer_id is a row number created in this project. The file has no customer key.
