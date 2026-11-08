-- 04_data_quality_checks.sql
-- Run after 01_build_model.sql. Every check should return the expected value.

SELECT 'row count (expect 45211)'              AS chk, COUNT(*) AS result FROM customers
UNION ALL SELECT 'null balances (expect 0)',          COUNT(*) FROM customers WHERE balance IS NULL
UNION ALL SELECT 'null age group (expect 0)',         COUNT(*) FROM customers WHERE age_group IS NULL
UNION ALL SELECT 'null balance band (expect 0)',      COUNT(*) FROM customers WHERE balance_band IS NULL
UNION ALL SELECT 'duplicate customer ids (expect 0)', COUNT(*) - COUNT(DISTINCT customer_id) FROM customers
UNION ALL SELECT 'age outside 18 to 100 (expect 0)',  COUNT(*) FROM customers WHERE age NOT BETWEEN 18 AND 100
UNION ALL SELECT 'month not mapped (expect 0)',       COUNT(*) FROM customers WHERE month_num IS NULL
UNION ALL SELECT 'pdays/previous mismatch (expect 0)',COUNT(*) FROM customers
                 WHERE (pdays = -1 AND previous > 0) OR (pdays <> -1 AND previous = 0)
UNION ALL SELECT 'unknown job rows',                  COUNT(*) FROM customers WHERE job = 'unknown'
UNION ALL SELECT 'unknown contact channel rows',      COUNT(*) FROM customers WHERE contact = 'unknown';
