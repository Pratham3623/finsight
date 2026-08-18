/* =====================================================================
   FINSIGHT — PHASE 9: SNOWFLAKE WAREHOUSE
   03_staging.sql

   PURPOSE
   -------
   Transforms RAW text data into properly typed, trimmed and
   de-duplicated STAGING tables.

   STAGING responsibilities:
     - Type conversion
     - Whitespace normalization
     - Basic structural filtering
     - Deduplication

   Business/derived metrics belong in CORE/MART, not STAGING.

   DEDUPLICATION
   -------------
   Keep the most recently loaded record for each natural key.

   IDEMPOTENCY
   -----------
   CREATE OR REPLACE TABLE ... AS SELECT fully rebuilds STAGING from
   the current RAW contents.
   ===================================================================== */

USE DATABASE FINSIGHT;
USE SCHEMA STAGING;


-- =====================================================================
-- 1. STAGING INDUSTRIES
-- =====================================================================

CREATE OR REPLACE TABLE STAGING.STG_INDUSTRIES AS
SELECT
    TRY_CAST(industry_id AS NUMBER(10,0)) AS industry_id,
    TRIM(industry_name) AS industry_name,
    _load_ts,
    _source_file
FROM RAW.INDUSTRIES
WHERE TRY_CAST(industry_id AS NUMBER(10,0)) IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY TRY_CAST(industry_id AS NUMBER(10,0))
    ORDER BY _load_ts DESC
) = 1;


-- =====================================================================
-- 2. STAGING COMPANIES
-- =====================================================================

CREATE OR REPLACE TABLE STAGING.STG_COMPANIES AS
SELECT
    TRY_CAST(company_id AS NUMBER(10,0)) AS company_id,
    TRIM(company_name) AS company_name,
    UPPER(TRIM(ticker)) AS ticker,
    TRY_CAST(industry_id AS NUMBER(10,0)) AS industry_id,
    TRIM(industry_name) AS industry_name,
    _load_ts,
    _source_file
FROM RAW.COMPANIES
WHERE TRY_CAST(company_id AS NUMBER(10,0)) IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY TRY_CAST(company_id AS NUMBER(10,0))
    ORDER BY _load_ts DESC
) = 1;


-- =====================================================================
-- 3. STAGING FINANCIALS
-- =====================================================================

CREATE OR REPLACE TABLE STAGING.STG_FINANCIALS AS
SELECT
    TRY_CAST(financial_id AS NUMBER(18,0)) AS financial_id,
    TRY_CAST(company_id AS NUMBER(10,0)) AS company_id,
    TRY_CAST(fiscal_year AS NUMBER(4,0)) AS fiscal_year,
    TRY_CAST(fiscal_quarter AS NUMBER(1,0)) AS fiscal_quarter,
    TRY_TO_DATE(period_end_date) AS period_end_date,

    TRY_CAST(revenue AS NUMBER(20,4)) AS revenue,
    TRY_CAST(operating_expenses AS NUMBER(20,4)) AS operating_expenses,
    TRY_CAST(net_income AS NUMBER(20,4)) AS net_income,

    TRY_CAST(total_assets AS NUMBER(20,4)) AS total_assets,
    TRY_CAST(total_liabilities AS NUMBER(20,4)) AS total_liabilities,
    TRY_CAST(total_debt AS NUMBER(20,4)) AS total_debt,

    TRY_CAST(operating_cash_flow AS NUMBER(20,4)) AS operating_cash_flow,
    TRY_CAST(investing_cash_flow AS NUMBER(20,4)) AS investing_cash_flow,
    TRY_CAST(financing_cash_flow AS NUMBER(20,4)) AS financing_cash_flow,

    _load_ts,
    _source_file
FROM RAW.FINANCIALS
WHERE TRY_CAST(financial_id AS NUMBER(18,0)) IS NOT NULL
  AND TRY_CAST(company_id AS NUMBER(10,0)) IS NOT NULL
  AND TRY_TO_DATE(period_end_date) IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY TRY_CAST(financial_id AS NUMBER(18,0))
    ORDER BY _load_ts DESC
) = 1;


-- =====================================================================
-- 4. ROW-COUNT VERIFICATION
-- =====================================================================

SELECT
    'STG_INDUSTRIES' AS table_name,
    COUNT(*) AS row_count
FROM STAGING.STG_INDUSTRIES

UNION ALL

SELECT
    'STG_COMPANIES',
    COUNT(*)
FROM STAGING.STG_COMPANIES

UNION ALL

SELECT
    'STG_FINANCIALS',
    COUNT(*)
FROM STAGING.STG_FINANCIALS;


-- =====================================================================
-- 5. RAW -> STAGING ROW-LOSS CHECK
-- =====================================================================

SELECT
    'INDUSTRIES rows lost' AS check_name,
    (
        SELECT COUNT(*)
        FROM RAW.INDUSTRIES
    )
    -
    (
        SELECT COUNT(*)
        FROM STAGING.STG_INDUSTRIES
    ) AS delta

UNION ALL

SELECT
    'COMPANIES rows lost',
    (
        SELECT COUNT(*)
        FROM RAW.COMPANIES
    )
    -
    (
        SELECT COUNT(*)
        FROM STAGING.STG_COMPANIES
    )

UNION ALL

SELECT
    'FINANCIALS rows lost',
    (
        SELECT COUNT(*)
        FROM RAW.FINANCIALS
    )
    -
    (
        SELECT COUNT(*)
        FROM STAGING.STG_FINANCIALS
    );


-- =====================================================================
-- 6. REFERENTIAL CHECK
-- =====================================================================
-- Every staged company should reference an existing staged industry.

SELECT
    c.company_id,
    c.company_name,
    c.industry_id
FROM STAGING.STG_COMPANIES c
LEFT JOIN STAGING.STG_INDUSTRIES i
    ON c.industry_id = i.industry_id
WHERE i.industry_id IS NULL;