-- 03_window_functions.sql
-- Pareto analysis, running totals, ranking inside segments, and month over month change.

-- W1. Deposit concentration: balance share by customer decile (decile 1 = richest 10%)
WITH deciles AS (
    SELECT balance, NTILE(10) OVER (ORDER BY balance DESC) AS decile FROM customers
)
SELECT decile,
       COUNT(*)                                   AS customers,
       SUM(balance)                               AS total_balance,
       ROUND(100.0 * SUM(balance) / SUM(SUM(balance)) OVER (), 1) AS share_pct,
       ROUND(100.0 * SUM(SUM(balance)) OVER (ORDER BY decile) / SUM(SUM(balance)) OVER (), 1) AS cumulative_share_pct
FROM deciles GROUP BY decile ORDER BY decile;

-- W2. Top 3 jobs inside each age group by total balance
WITH job_age AS (
    SELECT age_group, job, COUNT(*) AS customers, SUM(balance) AS total_balance,
           RANK() OVER (PARTITION BY age_group ORDER BY SUM(balance) DESC) AS rnk
    FROM customers GROUP BY age_group, job
)
SELECT * FROM job_age WHERE rnk <= 3 ORDER BY age_group, rnk;

-- W3. Monthly contact volume and conversion with change versus the previous calendar month
-- The file has no year, so months are pooled across the campaign period (seasonality view, not a trend).
WITH monthly AS (
    SELECT month_num, month_name, COUNT(*) AS contacts, SUM(term_deposit_flag) AS signups,
           100.0 * SUM(term_deposit_flag) / COUNT(*) AS conversion_pct
    FROM customers GROUP BY month_num, month_name
)
SELECT month_num, month_name, contacts, signups,
       ROUND(conversion_pct, 1) AS conversion_pct,
       ROUND(conversion_pct - LAG(conversion_pct) OVER (ORDER BY month_num), 1) AS change_vs_prev_month_pts,
       ROUND(100.0 * contacts / SUM(contacts) OVER (), 1) AS share_of_contacts_pct,
       ROUND(100.0 * signups  / SUM(signups)  OVER (), 1) AS share_of_signups_pct
FROM monthly ORDER BY month_num;

-- W4. Rank balance bands by conversion and show the running share of customers
SELECT balance_band,
       COUNT(*) AS customers,
       ROUND(100.0 * AVG(term_deposit_flag), 1) AS conversion_pct,
       RANK() OVER (ORDER BY AVG(term_deposit_flag) DESC) AS conversion_rank,
       ROUND(100.0 * SUM(COUNT(*)) OVER (ORDER BY balance_band) / SUM(COUNT(*)) OVER (), 1) AS cumulative_customer_pct
FROM customers GROUP BY balance_band ORDER BY balance_band;

-- W5. Previous campaign outcome versus current conversion, with balance rank inside outcome
SELECT poutcome, COUNT(*) AS customers,
       ROUND(100.0 * AVG(term_deposit_flag), 1) AS conversion_pct,
       ROUND(AVG(balance), 0) AS avg_balance,
       DENSE_RANK() OVER (ORDER BY AVG(term_deposit_flag) DESC) AS conversion_rank
FROM customers GROUP BY poutcome ORDER BY conversion_rank;
