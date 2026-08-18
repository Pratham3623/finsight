/* =====================================================================
   FINSIGHT — PHASE 9: SNOWFLAKE WAREHOUSE
   04_core.sql

   PURPOSE
   -------
   Builds the conformed CORE star schema:

     CORE.DIM_INDUSTRY
     CORE.DIM_COMPANY
     CORE.DIM_DATE
     CORE.FACT_FINANCIALS

   FACT GRAIN
   ----------
   One source financial reporting record per financial_id.

   financial_id is retained as the natural/source identifier and is
   unique in the fact table.

   Derived financial metrics are calculated once in CORE so downstream
   MART and BI consumers use one consistent definition.

   ===================================================================== */

USE DATABASE FINSIGHT;
USE SCHEMA CORE;


-- =====================================================================
-- 1. SURROGATE KEY SEQUENCES
-- =====================================================================

CREATE OR REPLACE SEQUENCE CORE.SEQ_INDUSTRY_KEY
    START = 1
    INCREMENT = 1;

CREATE OR REPLACE SEQUENCE CORE.SEQ_COMPANY_KEY
    START = 1
    INCREMENT = 1;

CREATE OR REPLACE SEQUENCE CORE.SEQ_FACT_KEY
    START = 1
    INCREMENT = 1;


-- =====================================================================
-- 2. DIMENSION: INDUSTRY
-- =====================================================================

CREATE OR REPLACE TABLE CORE.DIM_INDUSTRY (
    industry_key    NUMBER(10,0) NOT NULL,
    industry_id     NUMBER(10,0) NOT NULL,
    industry_name   VARCHAR(200) NOT NULL,
    created_at      TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),

    CONSTRAINT PK_DIM_INDUSTRY
        PRIMARY KEY (industry_key),

    CONSTRAINT UK_DIM_INDUSTRY_BK
        UNIQUE (industry_id)
)
COMMENT = 'Industry dimension using surrogate and natural keys.';


INSERT INTO CORE.DIM_INDUSTRY (
    industry_key,
    industry_id,
    industry_name
)
SELECT
    CORE.SEQ_INDUSTRY_KEY.NEXTVAL,
    industry_id,
    industry_name
FROM STAGING.STG_INDUSTRIES
WHERE industry_id IS NOT NULL
  AND industry_name IS NOT NULL;


-- =====================================================================
-- 3. DIMENSION: COMPANY
-- =====================================================================

CREATE OR REPLACE TABLE CORE.DIM_COMPANY (
    company_key     NUMBER(10,0) NOT NULL,
    company_id      NUMBER(10,0) NOT NULL,
    company_name    VARCHAR(300) NOT NULL,
    ticker          VARCHAR(20),
    industry_key    NUMBER(10,0),
    created_at      TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),

    CONSTRAINT PK_DIM_COMPANY
        PRIMARY KEY (company_key),

    CONSTRAINT UK_DIM_COMPANY_BK
        UNIQUE (company_id),

    CONSTRAINT FK_DIM_COMPANY_INDUSTRY
        FOREIGN KEY (industry_key)
        REFERENCES CORE.DIM_INDUSTRY (industry_key)
)
COMMENT = 'Company dimension linked to the industry dimension.';


INSERT INTO CORE.DIM_COMPANY (
    company_key,
    company_id,
    company_name,
    ticker,
    industry_key
)
SELECT
    CORE.SEQ_COMPANY_KEY.NEXTVAL,
    sc.company_id,
    sc.company_name,
    sc.ticker,
    di.industry_key
FROM STAGING.STG_COMPANIES sc
LEFT JOIN CORE.DIM_INDUSTRY di
    ON sc.industry_id = di.industry_id
WHERE sc.company_id IS NOT NULL
  AND sc.company_name IS NOT NULL;


-- =====================================================================
-- 4. DIMENSION: DATE
-- =====================================================================

CREATE OR REPLACE TABLE CORE.DIM_DATE (
    date_key        NUMBER(8,0) NOT NULL,
    full_date       DATE NOT NULL,
    year            NUMBER(4,0) NOT NULL,
    quarter         NUMBER(1,0) NOT NULL,
    month           NUMBER(2,0) NOT NULL,
    month_name      VARCHAR(20) NOT NULL,
    day_of_month    NUMBER(2,0) NOT NULL,
    day_of_week     NUMBER(1,0) NOT NULL,
    day_name        VARCHAR(20) NOT NULL,
    is_quarter_end  BOOLEAN NOT NULL,
    is_year_end     BOOLEAN NOT NULL,

    CONSTRAINT PK_DIM_DATE
        PRIMARY KEY (date_key)
)
COMMENT = 'Date dimension covering all financial period end dates.';


INSERT INTO CORE.DIM_DATE (
    date_key,
    full_date,
    year,
    quarter,
    month,
    month_name,
    day_of_month,
    day_of_week,
    day_name,
    is_quarter_end,
    is_year_end
)
SELECT
    TO_NUMBER(TO_CHAR(d, 'YYYYMMDD')) AS date_key,
    d AS full_date,
    YEAR(d) AS year,
    QUARTER(d) AS quarter,
    MONTH(d) AS month,
    MONTHNAME(d) AS month_name,
    DAY(d) AS day_of_month,
    DAYOFWEEK(d) AS day_of_week,
    DAYNAME(d) AS day_name,
    d = LAST_DAY(d, 'QUARTER') AS is_quarter_end,
    d = LAST_DAY(d, 'YEAR') AS is_year_end
FROM (
    SELECT DISTINCT
        period_end_date AS d
    FROM STAGING.STG_FINANCIALS
    WHERE period_end_date IS NOT NULL
) dates;


-- =====================================================================
-- 5. FACT: FINANCIALS
-- =====================================================================

CREATE OR REPLACE TABLE CORE.FACT_FINANCIALS (
    fact_key                        NUMBER(18,0) NOT NULL,
    financial_id                    NUMBER(18,0) NOT NULL,

    company_key                     NUMBER(10,0) NOT NULL,
    date_key                        NUMBER(8,0) NOT NULL,

    fiscal_year                     NUMBER(4,0) NOT NULL,
    fiscal_quarter                  NUMBER(1,0) NOT NULL,

    revenue                         NUMBER(20,4),
    operating_expenses              NUMBER(20,4),
    net_income                      NUMBER(20,4),

    total_assets                    NUMBER(20,4),
    total_liabilities               NUMBER(20,4),
    total_debt                      NUMBER(20,4),

    operating_cash_flow             NUMBER(20,4),
    investing_cash_flow             NUMBER(20,4),
    financing_cash_flow             NUMBER(20,4),

    net_profit_margin_pct           NUMBER(9,4),
    operating_margin_pct            NUMBER(9,4),
    debt_to_assets_pct              NUMBER(9,4),
    debt_to_equity_pct              NUMBER(9,4),
    roa_pct                         NUMBER(9,4),
    operating_cash_flow_margin_pct  NUMBER(9,4),
    revenue_growth_yoy_pct          NUMBER(9,4),

    created_at                      TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),

    CONSTRAINT PK_FACT_FINANCIALS
        PRIMARY KEY (fact_key),

    CONSTRAINT UK_FACT_FINANCIALS_BK
        UNIQUE (financial_id),

    CONSTRAINT FK_FACT_COMPANY
        FOREIGN KEY (company_key)
        REFERENCES CORE.DIM_COMPANY (company_key),

    CONSTRAINT FK_FACT_DATE
        FOREIGN KEY (date_key)
        REFERENCES CORE.DIM_DATE (date_key)
)
COMMENT = 'Financial fact table. One row per source financial_id.';


-- =====================================================================
-- 6. LOAD FACT + CALCULATE METRICS
-- =====================================================================

INSERT INTO CORE.FACT_FINANCIALS (
    fact_key,
    financial_id,
    company_key,
    date_key,
    fiscal_year,
    fiscal_quarter,

    revenue,
    operating_expenses,
    net_income,
    total_assets,
    total_liabilities,
    total_debt,

    operating_cash_flow,
    investing_cash_flow,
    financing_cash_flow,

    net_profit_margin_pct,
    operating_margin_pct,
    debt_to_assets_pct,
    debt_to_equity_pct,
    roa_pct,
    operating_cash_flow_margin_pct,
    revenue_growth_yoy_pct
)

WITH base AS (
    SELECT
        sf.financial_id,
        dc.company_key,

        TO_NUMBER(
            TO_CHAR(sf.period_end_date, 'YYYYMMDD')
        ) AS date_key,

        sf.fiscal_year,
        sf.fiscal_quarter,

        sf.revenue,
        sf.operating_expenses,
        sf.net_income,
        sf.total_assets,
        sf.total_liabilities,
        sf.total_debt,

        sf.operating_cash_flow,
        sf.investing_cash_flow,
        sf.financing_cash_flow

    FROM STAGING.STG_FINANCIALS sf

    INNER JOIN CORE.DIM_COMPANY dc
        ON sf.company_id = dc.company_id
),

with_growth AS (
    SELECT
        b.*,

        LAG(b.revenue) OVER (
            PARTITION BY
                b.company_key,
                b.fiscal_quarter
            ORDER BY
                b.fiscal_year
        ) AS prior_year_same_q_revenue

    FROM base b
)

SELECT
    CORE.SEQ_FACT_KEY.NEXTVAL AS fact_key,

    financial_id,
    company_key,
    date_key,
    fiscal_year,
    fiscal_quarter,

    revenue,
    operating_expenses,
    net_income,
    total_assets,
    total_liabilities,
    total_debt,

    operating_cash_flow,
    investing_cash_flow,
    financing_cash_flow,

    ROUND(
        100 * net_income / NULLIF(revenue, 0),
        4
    ) AS net_profit_margin_pct,

    ROUND(
        100 * (revenue - operating_expenses)
        / NULLIF(revenue, 0),
        4
    ) AS operating_margin_pct,

    ROUND(
        100 * total_debt
        / NULLIF(total_assets, 0),
        4
    ) AS debt_to_assets_pct,

    ROUND(
        100 * total_debt
        / NULLIF(total_assets - total_liabilities, 0),
        4
    ) AS debt_to_equity_pct,

    ROUND(
        100 * net_income
        / NULLIF(total_assets, 0),
        4
    ) AS roa_pct,

    ROUND(
        100 * operating_cash_flow
        / NULLIF(revenue, 0),
        4
    ) AS operating_cash_flow_margin_pct,

    ROUND(
        100 * (
            revenue - prior_year_same_q_revenue
        )
        / NULLIF(prior_year_same_q_revenue, 0),
        4
    ) AS revenue_growth_yoy_pct

FROM with_growth;


-- =====================================================================
-- 7. CLUSTERING
-- =====================================================================

ALTER TABLE CORE.FACT_FINANCIALS
CLUSTER BY (company_key, fiscal_year);


-- =====================================================================
-- 8. CORE VERIFICATION
-- =====================================================================

SELECT
    'DIM_INDUSTRY' AS table_name,
    COUNT(*) AS row_count
FROM CORE.DIM_INDUSTRY

UNION ALL

SELECT
    'DIM_COMPANY',
    COUNT(*)
FROM CORE.DIM_COMPANY

UNION ALL

SELECT
    'DIM_DATE',
    COUNT(*)
FROM CORE.DIM_DATE

UNION ALL

SELECT
    'FACT_FINANCIALS',
    COUNT(*)
FROM CORE.FACT_FINANCIALS;


-- =====================================================================
-- 9. REFERENTIAL INTEGRITY
-- =====================================================================

SELECT
    COUNT(*) AS orphan_fact_rows_missing_company
FROM CORE.FACT_FINANCIALS f
LEFT JOIN CORE.DIM_COMPANY c
    ON f.company_key = c.company_key
WHERE c.company_key IS NULL;


SELECT
    COUNT(*) AS orphan_fact_rows_missing_date
FROM CORE.FACT_FINANCIALS f
LEFT JOIN CORE.DIM_DATE d
    ON f.date_key = d.date_key
WHERE d.date_key IS NULL;


-- =====================================================================
-- 10. DERIVED METRIC SANITY CHECK
-- =====================================================================

SELECT
    financial_id,
    net_profit_margin_pct,
    operating_margin_pct,
    roa_pct
FROM CORE.FACT_FINANCIALS
WHERE ABS(net_profit_margin_pct) > 200
   OR ABS(operating_margin_pct) > 200
   OR ABS(roa_pct) > 200;