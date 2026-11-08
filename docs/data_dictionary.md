# Data dictionary (data/processed/bank_customers_clean.csv)

| Column | Meaning |
|---|---|
| customer_id | Row number created here (no key in the source) |
| age, age_group | Age in years and band (18-24, 25-34, 35-44, 45-54, 55-64, 65+) |
| job, marital, education | Customer attributes. Unknown kept as a category |
| credit_default, credit_default_flag | Has credit in default (risk flag) |
| balance | Average yearly balance in EUR, used as deposit proxy |
| balance_positive | Balance floored at zero, used for concentration charts |
| balance_band | Overdrawn, Zero, Low (1-500), Medium (501-1500), High (1501-5000), Very high (5000+) |
| housing_loan, personal_loan | Holds the product (yes or no) and matching _flag columns |
| term_deposit, term_deposit_flag | Campaign outcome. Yes means the customer signed up |
| contact | Channel of last contact: Cellular, Telephone, Unknown |
| day, month, month_num | Day of month and month of last contact. No year |
| duration | Last call length in seconds. Not used in analysis |
| campaign, contacts_band | Contacts made in this campaign and its band (1, 2-3, 4-6, 7+) |
| pdays, previous, prior_contacted_flag | Days since previous campaign contact (-1 = none), earlier contacts, flag |
| poutcome | Result of the previous campaign |
| product_count | Housing loan + personal loan + term deposit (0 to 3) |
| no_product_flag | Holds none of the three products. Inactivity proxy 2 |
| overdrawn_flag, zero_or_negative_flag | Balance below zero, balance at or below zero. Inactivity proxy 1 |
| balance_outlier_flag | Beyond 1.5 x IQR. Kept in the data |
