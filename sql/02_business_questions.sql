-- 02_business_questions.sql
-- One query per business question. Balance is the average yearly balance in EUR
-- and is used as the deposit proxy (see docs/limitations.md).

-- Q1. Which customer segments contribute the most to total deposits?
SELECT dimension, segment,
       COUNT(*)                                                       AS customers,
       SUM(balance)                                                   AS total_balance,
       ROUND(100.0 * SUM(balance) / SUM(SUM(balance)) OVER (PARTITION BY dimension), 1) AS deposit_share_pct,
       ROUND(100.0 * COUNT(*)     / SUM(COUNT(*))     OVER (PARTITION BY dimension), 1) AS customer_share_pct,
       RANK() OVER (PARTITION BY dimension ORDER BY SUM(balance) DESC) AS deposit_rank
FROM v_segments
GROUP BY dimension, segment
ORDER BY dimension, deposit_rank;

-- Q2. Which channels and months have the highest customer acquisition (term deposit sign ups)?
SELECT 'Channel' AS cut, contact AS value,
       COUNT(*) AS customers_contacted,
       SUM(term_deposit_flag) AS new_term_deposits,
       ROUND(100.0 * SUM(term_deposit_flag) / COUNT(*), 1) AS conversion_pct
FROM customers GROUP BY contact
UNION ALL
SELECT 'Month', month_name,
       COUNT(*), SUM(term_deposit_flag),
       ROUND(100.0 * SUM(term_deposit_flag) / COUNT(*), 1)
FROM customers GROUP BY month_name
ORDER BY cut, new_term_deposits DESC;

-- Q3. Which banking products have the highest adoption?
SELECT 'Housing loan' AS product, SUM(housing_loan_flag) AS holders,
       ROUND(100.0 * SUM(housing_loan_flag) / COUNT(*), 1) AS adoption_pct FROM customers
UNION ALL
SELECT 'Personal loan', SUM(personal_loan_flag), ROUND(100.0 * SUM(personal_loan_flag) / COUNT(*), 1) FROM customers
UNION ALL
SELECT 'Term deposit', SUM(term_deposit_flag), ROUND(100.0 * SUM(term_deposit_flag) / COUNT(*), 1) FROM customers
UNION ALL
SELECT 'Credit default (risk flag)', SUM(credit_default_flag), ROUND(100.0 * SUM(credit_default_flag) / COUNT(*), 1) FROM customers
ORDER BY adoption_pct DESC;

-- Q3b. Products held per customer
SELECT product_count,
       COUNT(*) AS customers,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS customer_share_pct,
       ROUND(AVG(balance), 0) AS avg_balance
FROM customers GROUP BY product_count ORDER BY product_count;

-- Q4. What percentage of customers are inactive? (two proxies, no transaction history exists)
SELECT COUNT(*) AS customers,
       ROUND(100.0 * AVG(zero_or_negative_flag), 1) AS pct_zero_or_negative_balance,
       ROUND(100.0 * AVG(overdrawn_flag), 1)        AS pct_overdrawn,
       ROUND(100.0 * AVG(no_product_flag), 1)       AS pct_no_product,
       ROUND(100.0 * AVG(CASE WHEN zero_or_negative_flag = 1 AND no_product_flag = 1 THEN 1.0 ELSE 0.0 END), 1) AS pct_both_proxies
FROM customers;

-- Q5. Which segments have the highest average balance? (median added because balances are skewed)
WITH ranked AS (
    SELECT dimension, segment, balance,
           ROW_NUMBER() OVER (PARTITION BY dimension, segment ORDER BY balance) AS rn,
           COUNT(*)     OVER (PARTITION BY dimension, segment)                  AS cnt
    FROM v_segments
),
medians AS (
    SELECT dimension, segment, AVG(balance) AS median_balance
    FROM ranked
    WHERE 2 * rn IN (cnt, cnt + 1, cnt + 2)        -- picks the middle row, or the two middle rows
    GROUP BY dimension, segment
)
SELECT v.dimension, v.segment, COUNT(*) AS customers,
       ROUND(AVG(v.balance), 0) AS avg_balance,
       m.median_balance,
       RANK() OVER (PARTITION BY v.dimension ORDER BY AVG(v.balance) DESC) AS avg_balance_rank
FROM v_segments v
JOIN medians m ON m.dimension = v.dimension AND m.segment = v.segment
GROUP BY v.dimension, v.segment, m.median_balance
ORDER BY v.dimension, avg_balance_rank;

-- Q6. Which segments underperform relative to their customer base?
-- Missed sign ups = (overall conversion minus segment conversion) x segment customers.
WITH overall AS (
    SELECT AVG(term_deposit_flag) AS rate, AVG(balance) AS avg_bal FROM customers
),
seg AS (
    SELECT dimension, segment, COUNT(*) AS n,
           AVG(term_deposit_flag) AS rate, AVG(balance) AS avg_bal
    FROM v_segments GROUP BY dimension, segment
)
SELECT s.dimension, s.segment, s.n AS customers,
       ROUND(100.0 * s.rate, 1)            AS conversion_pct,
       ROUND(s.rate / o.rate, 2)           AS conversion_index,
       ROUND(s.avg_bal / o.avg_bal, 2)     AS balance_index,
       ROUND((o.rate - s.rate) * s.n, 0)   AS missed_signups
FROM seg s CROSS JOIN overall o
WHERE s.n >= 1000 AND s.rate < o.rate
ORDER BY missed_signups DESC;

-- Q6b. Combined segments: job x age group with a high balance but low conversion
WITH overall AS (
    SELECT AVG(term_deposit_flag) AS rate, AVG(balance) AS avg_bal FROM customers
)
SELECT c.job, c.age_group, COUNT(*) AS customers,
       ROUND(AVG(c.balance), 0) AS avg_balance,
       ROUND(100.0 * AVG(c.term_deposit_flag), 1) AS conversion_pct,
       ROUND((o.rate - AVG(c.term_deposit_flag)) * COUNT(*), 0) AS missed_signups
FROM customers c CROSS JOIN overall o
GROUP BY c.job, c.age_group, o.rate, o.avg_bal
HAVING COUNT(*) >= 500 AND AVG(c.balance) > o.avg_bal AND AVG(c.term_deposit_flag) < o.rate
ORDER BY missed_signups DESC;
