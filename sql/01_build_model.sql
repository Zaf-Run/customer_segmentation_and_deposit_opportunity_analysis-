-- 01_build_model.sql
-- Builds two dimension tables and the cleaned customers table from staging.
-- Uses range joins to attach age groups and balance bands.
-- Written in portable SQL (MySQL 8 and SQLite 3.25+).

DROP TABLE IF EXISTS dim_age_group;
CREATE TABLE dim_age_group (
    age_group  VARCHAR(10),
    age_min    INT,
    age_max    INT
);
INSERT INTO dim_age_group VALUES
 ('18-24', 18, 24), ('25-34', 25, 34), ('35-44', 35, 44),
 ('45-54', 45, 54), ('55-64', 55, 64), ('65+', 65, 120);

DROP TABLE IF EXISTS dim_balance_band;
CREATE TABLE dim_balance_band (
    balance_band VARCHAR(25),
    balance_min  INT,
    balance_max  INT
);
INSERT INTO dim_balance_band VALUES
 ('1 Overdrawn',          -100000,      -1),
 ('2 Zero',                     0,       0),
 ('3 Low (1-500)',              1,     500),
 ('4 Medium (501-1500)',      501,    1500),
 ('5 High (1501-5000)',      1501,    5000),
 ('6 Very high (5000+)',     5001, 1000000);

DROP TABLE IF EXISTS customers;
CREATE TABLE customers AS
SELECT
    s.row_id                                              AS customer_id,
    s.age,
    a.age_group,
    REPLACE(REPLACE(LOWER(TRIM(s.job)), '-', ' '), '.', '') AS job,
    LOWER(TRIM(s.marital))                                AS marital,
    LOWER(TRIM(s.education))                              AS education,
    s.balance,
    CASE WHEN s.balance < 0 THEN 0 ELSE s.balance END     AS balance_positive,
    b.balance_band,
    CASE WHEN s.credit_default = 'yes' THEN 1 ELSE 0 END  AS credit_default_flag,
    CASE WHEN s.housing = 'yes' THEN 1 ELSE 0 END         AS housing_loan_flag,
    CASE WHEN s.loan = 'yes' THEN 1 ELSE 0 END            AS personal_loan_flag,
    CASE WHEN s.y = 'yes' THEN 1 ELSE 0 END               AS term_deposit_flag,
    LOWER(TRIM(s.contact))                                AS contact,
    s.day_of_month,
    LOWER(TRIM(s.month_name))                             AS month_name,
    CASE LOWER(TRIM(s.month_name))
        WHEN 'jan' THEN 1 WHEN 'feb' THEN 2 WHEN 'mar' THEN 3 WHEN 'apr' THEN 4
        WHEN 'may' THEN 5 WHEN 'jun' THEN 6 WHEN 'jul' THEN 7 WHEN 'aug' THEN 8
        WHEN 'sep' THEN 9 WHEN 'oct' THEN 10 WHEN 'nov' THEN 11 WHEN 'dec' THEN 12
    END                                                   AS month_num,
    s.campaign,
    CASE WHEN s.campaign = 1 THEN '1'
         WHEN s.campaign <= 3 THEN '2-3'
         WHEN s.campaign <= 6 THEN '4-6'
         ELSE '7+' END                                    AS contacts_band,
    s.pdays,
    s.previous,
    CASE WHEN s.pdays = -1 THEN 0 ELSE 1 END              AS prior_contacted_flag,
    LOWER(TRIM(s.poutcome))                               AS poutcome,
    (CASE WHEN s.housing = 'yes' THEN 1 ELSE 0 END
     + CASE WHEN s.loan = 'yes' THEN 1 ELSE 0 END
     + CASE WHEN s.y = 'yes' THEN 1 ELSE 0 END)           AS product_count,
    CASE WHEN s.housing = 'no' AND s.loan = 'no' AND s.y = 'no'
         THEN 1 ELSE 0 END                                AS no_product_flag,
    CASE WHEN s.balance < 0 THEN 1 ELSE 0 END             AS overdrawn_flag,
    CASE WHEN s.balance <= 0 THEN 1 ELSE 0 END            AS zero_or_negative_flag
FROM stg_bank_raw s
JOIN dim_age_group    a ON s.age     BETWEEN a.age_min     AND a.age_max
JOIN dim_balance_band b ON s.balance BETWEEN b.balance_min AND b.balance_max;

-- Join check: every raw row must land in exactly one age group and one balance band
SELECT (SELECT COUNT(*) FROM stg_bank_raw) AS raw_rows,
       (SELECT COUNT(*) FROM customers)    AS customer_rows;

-- One long view so every segment question can be answered with one query shape
DROP VIEW IF EXISTS v_segments;
CREATE VIEW v_segments AS
SELECT customer_id, 'Age group' AS dimension, age_group AS segment,
       balance, balance_positive, term_deposit_flag, zero_or_negative_flag, no_product_flag FROM customers
UNION ALL
SELECT customer_id, 'Job', job,
       balance, balance_positive, term_deposit_flag, zero_or_negative_flag, no_product_flag FROM customers
UNION ALL
SELECT customer_id, 'Marital status', marital,
       balance, balance_positive, term_deposit_flag, zero_or_negative_flag, no_product_flag FROM customers
UNION ALL
SELECT customer_id, 'Education', education,
       balance, balance_positive, term_deposit_flag, zero_or_negative_flag, no_product_flag FROM customers;
