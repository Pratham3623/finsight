-- =========================================================
-- FinSight — Snowflake RAW Layer
-- =========================================================

USE DATABASE FINSIGHT;
USE SCHEMA RAW;

-- ---------------------------------------------------------
-- Industries
-- ---------------------------------------------------------

CREATE OR REPLACE TABLE RAW.INDUSTRIES (
    INDUSTRY_ID INTEGER,
    INDUSTRY_NAME VARCHAR
);

-- ---------------------------------------------------------
-- Companies
-- ---------------------------------------------------------

CREATE OR REPLACE TABLE RAW.COMPANIES (
    COMPANY_ID INTEGER,
    COMPANY_NAME VARCHAR,
    TICKER VARCHAR,
    INDUSTRY_ID INTEGER,
    INDUSTRY_NAME VARCHAR
);

-- ---------------------------------------------------------
-- Financials
-- ---------------------------------------------------------

CREATE OR REPLACE TABLE RAW.FINANCIALS (
    FINANCIAL_ID INTEGER,
    COMPANY_ID INTEGER,
    FISCAL_YEAR INTEGER,
    FISCAL_QUARTER INTEGER,
    PERIOD_END_DATE DATE,

    REVENUE NUMBER(20, 2),
    OPERATING_EXPENSES NUMBER(20, 2),
    NET_INCOME NUMBER(20, 2),

    TOTAL_ASSETS NUMBER(20, 2),
    TOTAL_LIABILITIES NUMBER(20, 2),
    TOTAL_DEBT NUMBER(20, 2),

    OPERATING_CASH_FLOW NUMBER(20, 2),
    INVESTING_CASH_FLOW NUMBER(20, 2),
    FINANCING_CASH_FLOW NUMBER(20, 2)
);

-- ---------------------------------------------------------
-- Verification
-- ---------------------------------------------------------

SHOW TABLES IN SCHEMA FINSIGHT.RAW;