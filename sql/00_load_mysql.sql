-- 00_load_mysql.sql  (MySQL 8.0)
-- Creates the schema and loads the raw semicolon separated file into a staging table.
-- Tip: if LOAD DATA is blocked, use MySQL Workbench > Table Data Import Wizard instead
-- (choose ";" as separator) and map the columns in the order below.

CREATE DATABASE IF NOT EXISTS bank_analytics;
USE bank_analytics;

DROP TABLE IF EXISTS stg_bank_raw;
CREATE TABLE stg_bank_raw (
    row_id         INT AUTO_INCREMENT PRIMARY KEY,   -- keeps the original file order
    age            INT,
    job            VARCHAR(20),
    marital        VARCHAR(10),
    education      VARCHAR(10),
    credit_default VARCHAR(3),
    balance        INT,
    housing        VARCHAR(3),
    loan           VARCHAR(3),
    contact        VARCHAR(10),
    day_of_month   INT,
    month_name     VARCHAR(3),
    duration       INT,
    campaign       INT,
    pdays          INT,
    previous       INT,
    poutcome       VARCHAR(10),
    y              VARCHAR(3)
);

-- Enable once if needed:  SET GLOBAL local_infile = 1;   (and start the client with --local-infile=1)
LOAD DATA LOCAL INFILE 'data/raw/bank-full.csv'
INTO TABLE stg_bank_raw
FIELDS TERMINATED BY ';' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'            -- use '\r\n' if the file was saved on Windows
IGNORE 1 LINES
(age, job, marital, education, credit_default, balance, housing, loan,
 contact, day_of_month, month_name, duration, campaign, pdays, previous, poutcome, y);

-- Load check: expect 45211
SELECT COUNT(*) AS rows_loaded FROM stg_bank_raw;
