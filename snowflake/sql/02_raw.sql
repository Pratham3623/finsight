/* =====================================================================
   FINSIGHT — PHASE 9: SNOWFLAKE WAREHOUSE
   02_raw.sql

   PURPOSE
   -------
   Defines the RAW landing layer for the three FinSight source datasets:

     data/raw/reference/industries.csv
     data/raw/reference/companies.csv
     data/processed/financials.csv

   RAW DESIGN
   ----------
   Source columns are intentionally stored as VARCHAR.

   RAW is a landing and audit layer. Type conversion and business
   validation happen later in STAGING.

   This allows malformed values such as:

       "N/A"
       "unknown"
       "bad-date"

   to land safely as text and be handled explicitly downstream.

   LOAD METADATA
   -------------
   _load_ts     = ingestion timestamp
   _source_file = source filename from Snowflake stage metadata

   ===================================================================== */

USE DATABASE FINSIGHT;
USE SCHEMA RAW;


-- =====================================================================
-- 1. RAW INDUSTRIES
-- =====================================================================

CREATE OR REPLACE TABLE RAW.INDUSTRIES (
    industry_id     VARCHAR,
    industry_name   VARCHAR,

    _load_ts        TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    _source_file    VARCHAR
)
COMMENT = 'Raw landing table for industries.csv.';


-- =====================================================================
-- 2. RAW COMPANIES
-- =====================================================================

CREATE OR REPLACE TABLE RAW.COMPANIES (
    company_id      VARCHAR,
    company_name    VARCHAR,
    ticker          VARCHAR,
    industry_id     VARCHAR,
    industry_name   VARCHAR,

    _load_ts        TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    _source_file    VARCHAR
)
COMMENT = 'Raw landing table for companies.csv.';


-- =====================================================================
-- 3. RAW FINANCIALS
-- =====================================================================

CREATE OR REPLACE TABLE RAW.FINANCIALS (
    financial_id            VARCHAR,
    company_id              VARCHAR,
    fiscal_year             VARCHAR,
    fiscal_quarter          VARCHAR,
    period_end_date         VARCHAR,

    revenue                 VARCHAR,
    operating_expenses      VARCHAR,
    net_income              VARCHAR,

    total_assets            VARCHAR,
    total_liabilities       VARCHAR,
    total_debt              VARCHAR,

    operating_cash_flow     VARCHAR,
    investing_cash_flow     VARCHAR,
    financing_cash_flow     VARCHAR,

    _load_ts                TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    _source_file            VARCHAR
)
COMMENT = 'Raw landing table for financials.csv.';


-- =====================================================================
-- 4. LOAD INDUSTRIES
-- =====================================================================

COPY INTO RAW.INDUSTRIES (
    industry_id,
    industry_name,
    _source_file
)
FROM (
    SELECT
        $1,
        $2,
        METADATA$FILENAME
    FROM @RAW.STG_INDUSTRIES
)
FILE_FORMAT = (
    FORMAT_NAME = RAW.FF_CSV_STANDARD
)
ON_ERROR = 'ABORT_STATEMENT';


-- =====================================================================
-- 5. LOAD COMPANIES
-- =====================================================================

COPY INTO RAW.COMPANIES (
    company_id,
    company_name,
    ticker,
    industry_id,
    industry_name,
    _source_file
)
FROM (
    SELECT
        $1,
        $2,
        $3,
        $4,
        $5,
        METADATA$FILENAME
    FROM @RAW.STG_COMPANIES
)
FILE_FORMAT = (
    FORMAT_NAME = RAW.FF_CSV_STANDARD
)
ON_ERROR = 'ABORT_STATEMENT';


-- =====================================================================
-- 6. LOAD FINANCIALS
-- =====================================================================

COPY INTO RAW.FINANCIALS (
    financial_id,
    company_id,
    fiscal_year,
    fiscal_quarter,
    period_end_date,
    revenue,
    operating_expenses,
    net_income,
    total_assets,
    total_liabilities,
    total_debt,
    operating_cash_flow,
    investing_cash_flow,
    financing_cash_flow,
    _source_file
)
FROM (
    SELECT
        $1,
        $2,
        $3,
        $4,
        $5,
        $6,
        $7,
        $8,
        $9,
        $10,
        $11,
        $12,
        $13,
        $14,
        METADATA$FILENAME
    FROM @RAW.STG_FINANCIALS
)
FILE_FORMAT = (
    FORMAT_NAME = RAW.FF_CSV_STANDARD
)
ON_ERROR = 'ABORT_STATEMENT';


-- =====================================================================
-- 7. RAW VERIFICATION
-- =====================================================================

SELECT
    'RAW.INDUSTRIES' AS table_name,
    COUNT(*) AS row_count
FROM RAW.INDUSTRIES

UNION ALL

SELECT
    'RAW.COMPANIES',
    COUNT(*)
FROM RAW.COMPANIES

UNION ALL

SELECT
    'RAW.FINANCIALS',
    COUNT(*)
FROM RAW.FINANCIALS;


-- =====================================================================
-- 8. SOURCE FILE VERIFICATION
-- =====================================================================

SELECT
    table_name,
    source_file,
    row_count
FROM (
    SELECT
        'RAW.INDUSTRIES' AS table_name,
        _source_file AS source_file,
        COUNT(*) AS row_count
    FROM RAW.INDUSTRIES
    GROUP BY _source_file

    UNION ALL

    SELECT
        'RAW.COMPANIES',
        _source_file,
        COUNT(*)
    FROM RAW.COMPANIES
    GROUP BY _source_file

    UNION ALL

    SELECT
        'RAW.FINANCIALS',
        _source_file,
        COUNT(*)
    FROM RAW.FINANCIALS
    GROUP BY _source_file
)
ORDER BY table_name, source_file;