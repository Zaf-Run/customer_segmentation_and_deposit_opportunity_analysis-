# Findings and recommendations

All figures come from 45,211 customers. SQL, Python and Excel give identical results (see data/processed/sql_vs_pandas_reconciliation.csv, 59 of 59 checks pass, and the Validation sheet in the workbook). Balance is average yearly balance in EUR. Statistical tests are in data/processed/statistical_tests.csv (all differences below have p < 0.0001).

## Answers to the business questions

| # | Question | Answer |
|---|---|---|
| 1 | Which segments contribute most to deposits? | Management 27.1% of balances (21% of customers). Ages 35 to 44 hold 30.2%, then 25 to 34 at 26.4%. Tertiary educated customers hold 38.0% from 29.4% of customers. The top 10% of customers hold 56% of positive balances and the top 20% hold 74%. |
| 2 | Which channels and periods acquire most customers? | Cellular brings 4,369 of 5,289 sign ups (83%) at 14.9% conversion. May brings the most sign ups (925) but converts at only 6.7%. Branch acquisition cannot be answered, there is no branch field. |
| 3 | Which products have the highest adoption? | Housing loan 55.6%, personal loan 16.0%, term deposit 11.7%. Credit default flag 1.8%. 31.1% hold none of the three, 55.0% hold one, 13.9% hold two or three. |
| 4 | What percentage are inactive? | No transaction data, so two proxies: 16.1% have a zero or negative balance (8.3% overdrawn) and 31.1% hold no product. 4.5% fall in both groups. |
| 5 | Which segments have the highest average balance? | Age 65+ at 2,791 (median 1,411), age 55 to 64 at 1,926, retired at 1,984, management at 1,764, tertiary at 1,758. Lowest: services at 997 and ages 18 to 24 at 916. |
| 6 | Which segments underperform relative to their customer base? | Blue collar: 21.5% of customers, 7.3% conversion (index 0.62), about 430 missed sign ups. Then married (429), ages 35 to 44 (296), secondary education (264), ages 45 to 54 (242), primary education (210). |

## What stands out

1. Money is concentrated. Half the balances sit with one customer in ten, and 16% of customers have nothing or owe money.
2. Entrepreneurs and ages 45 to 54 combine above average balances (index 1.12 and 1.06) with below average conversion (index 0.71 and 0.79). This is the clearest deposit campaign target.
3. Ages 65 and over and retired customers convert at 42.1% and 22.8% with the highest balances, yet make up only 1.8% and 5.0% of the base. They are under contacted.
4. 28.8% of contacts have no recorded channel and convert at 4.1%, against 14.9% on cellular.
5. May takes 30.4% of contacts but only 17.5% of sign ups (6.7% conversion). March, September, October and December convert at 44% to 52% on just 4.4% of contacts.
6. Conversion falls as contact count rises: 14.6% at one contact, 11.2% at two or three, 8.3% at four to six, 5.3% at seven or more.
7. Customers who said yes in a previous campaign say yes again at 64.7% (1,511 customers) against 9.9% for everyone else.
8. Housing loan holders convert at 7.7% against 16.7% for those without a housing loan.

## Recommendations

| Priority | Action | Evidence | Success measure |
|---|---|---|---|
| 1 | Run a fixed deposit campaign for entrepreneurs and ages 45 to 54 with above average balances and below average sign up rates | Balance index above 1, conversion index below 0.8 | Close half the gap: about 25 extra sign ups among entrepreneurs and 120 among ages 45 to 54 (Scenario sheet) |
| 2 | Contact ages 65 and over, retired customers and students first | Conversion 42%, 23%, 29% | Sign ups per 100 calls |
| 3 | Re-contact customers with a successful previous campaign before cold leads | 64.7% conversion | Conversion of the warm list |
| 4 | Record the channel on every contact and move volume from unknown to cellular | 4.1% against 14.9% | Share of contacts with a channel above 95% |
| 5 | Test moving part of May volume into February, March, April and September to October | May 6.7% against 9% to 52% in other months | A/B test with matched lists, because small months may be targeted lists |
| 6 | Cap attempts at three per customer and test the cap | Conversion drops after three contacts | Sign ups per call hour |
| 7 | Build a reactivation and cross sell list from customers with zero or negative balance and no product | 4.5% of customers, 2,000 or so people | Share moving to a positive balance or a second product |

The first recommendation mirrors the brief's example: find groups with high customer value indicators but weak product uptake and aim a deposit campaign at them. A branch version of the same logic needs branch data.
