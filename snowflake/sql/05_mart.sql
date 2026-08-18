/* =====================================================================
   FINSIGHT — PHASE 9: SNOWFLAKE WAREHOUSE
   05_mart.sql

   PURPOSE
   -------
   Creates consumption-ready MART tables for BI, dashboards and
   analytical queries.

   MART TABLES
   -----------
   COMPANY_PERFORMANCE
       One row per company per fiscal quarter.

   INDUSTRY_PERFORMANCE
       One row per industry per fiscal quarter.

   COMPANY_RANKINGS
       Company rankings by ROA and revenue, both overall and
       within-industry.

   CORE remains the single source of truth for financial metric logic.
   MART intentionally denormalizes CORE for easier BI consumption.
   ===================================================================== */

USE DATABASE FINSIGHT;
USE SCHEMA MART;


-- =====================================================================
-- 1. COMPANY PERFORMANCE
-- =====================================================================

CREATE OR REPLACE TABLE MART.COMPANY_PERFORMANCE AS
SELECT
    f.fact_key,

    c.company_id,
    c.company_name,
    c.ticker,

    i.industry_id,
    i.industry_name,

    f.fiscal_year,
    f.fiscal_quarter,
    d.full_date AS period_end_date,

    f.revenue,
    f.operating_expenses,
    f.net_income,

    f.total_assets,
    f.total_liabilities,
    f.total_debt,

    f.operating_cash_flow,
    f.investing_cash_flow,
    f.financing_cash_flow,

    f.net_profit_margin_pct,
    f.operating_margin_pct,
    f.debt_to_assets_pct,
    f.debt_to_equity_pct,
    f.roa_pct,
    f.operating_cash_flow_margin_pct,
    f.revenue_growth_yoy_pct

FROM CORE.FACT_FINANCIALS f

JOIN CORE.DIM_COMPANY c
    ON f.company_key = c.company_key

JOIN CORE.DIM_DATE d
    ON f.date_key = d.date_key

LEFT JOIN CORE.DIM_INDUSTRY i
    ON c.industry_key = i.industry_key

COMMENT = 'BI-ready company financial performance by fiscal quarter.';


-- =====================================================================
-- 2. INDUSTRY PERFORMANCE
-- =====================================================================

CREATE OR REPLACE TABLE MART.INDUSTRY_PERFORMANCE AS
SELECT
    i.industry_id,
    i.industry_name,

    f.fiscal_year,
    f.fiscal_quarter,

    COUNT(DISTINCT c.company_id) AS company_count,

    SUM(f.revenue) AS total_revenue,
    SUM(f.operating_expenses) AS total_operating_expenses,
    SUM(f.net_income) AS total_net_income,

    SUM(f.total_assets) AS total_assets,
    SUM(f.total_liabilities) AS total_liabilities,
    SUM(f.total_debt) AS total_debt,

    SUM(f.operating_cash_flow) AS total_operating_cash_flow,

    ROUND(
        100 * SUM(f.net_income)
        / NULLIF(SUM(f.revenue), 0),
        4
    ) AS net_profit_margin_pct,

    ROUND(
        100 * (
            SUM(f.revenue) - SUM(f.operating_expenses)
        )
        / NULLIF(SUM(f.revenue), 0),
        4
    ) AS operating_margin_pct,

    ROUND(
        100 * SUM(f.total_debt)
        / NULLIF(SUM(f.total_assets), 0),
        4
    ) AS debt_to_assets_pct,

    ROUND(
        100 * SUM(f.total_debt)
        / NULLIF(
            SUM(f.total_assets) - SUM(f.total_liabilities),
            0
        ),
        4
    ) AS debt_to_equity_pct,

    ROUND(
        100 * SUM(f.net_income)
        / NULLIF(SUM(f.total_assets), 0),
        4
    ) AS roa_pct,

    ROUND(
        100 * SUM(f.operating_cash_flow)
        / NULLIF(SUM(f.revenue), 0),
        4
    ) AS operating_cash_flow_margin_pct,

    ROUND(
        AVG(f.revenue_growth_yoy_pct),
        4
    ) AS avg_revenue_growth_yoy_pct

FROM CORE.FACT_FINANCIALS f

JOIN CORE.DIM_COMPANY c
    ON f.company_key = c.company_key

JOIN CORE.DIM_INDUSTRY i
    ON c.industry_key = i.industry_key

GROUP BY
    i.industry_id,
    i.industry_name,
    f.fiscal_year,
    f.fiscal_quarter

COMMENT = 'Industry-level financial performance by fiscal quarter.';


-- =====================================================================
-- 3. COMPANY RANKINGS
-- =====================================================================

CREATE OR REPLACE TABLE MART.COMPANY_RANKINGS AS
SELECT
    c.company_id,
    c.company_name,
    c.ticker,

    i.industry_id,
    i.industry_name,

    f.fiscal_year,
    f.fiscal_quarter,

    f.revenue,
    f.roa_pct,

    RANK() OVER (
        PARTITION BY
            f.fiscal_year,
            f.fiscal_quarter
        ORDER BY
            f.roa_pct DESC NULLS LAST
    ) AS roa_rank_overall,

    RANK() OVER (
        PARTITION BY
            f.fiscal_year,
            f.fiscal_quarter,
            i.industry_id
        ORDER BY
            f.roa_pct DESC NULLS LAST
    ) AS roa_rank_in_industry,

    RANK() OVER (
        PARTITION BY
            f.fiscal_year,
            f.fiscal_quarter
        ORDER BY
            f.revenue DESC NULLS LAST
    ) AS revenue_rank_overall,

    RANK() OVER (
        PARTITION BY
            f.fiscal_year,
            f.fiscal_quarter,
            i.industry_id
        ORDER BY
            f.revenue DESC NULLS LAST
    ) AS revenue_rank_in_industry

FROM CORE.FACT_FINANCIALS f

JOIN CORE.DIM_COMPANY c
    ON f.company_key = c.company_key

LEFT JOIN CORE.DIM_INDUSTRY i
    ON c.industry_key = i.industry_key

COMMENT = 'Company rankings by ROA and revenue, overall and within industry.';


-- =====================================================================
-- 4. MART ROW-COUNT VERIFICATION
-- =====================================================================

SELECT
    'COMPANY_PERFORMANCE' AS table_name,
    COUNT(*) AS row_count
FROM MART.COMPANY_PERFORMANCE

UNION ALL

SELECT
    'INDUSTRY_PERFORMANCE',
    COUNT(*)
FROM MART.INDUSTRY_PERFORMANCE

UNION ALL

SELECT
    'COMPANY_RANKINGS',
    COUNT(*)
FROM MART.COMPANY_RANKINGS;


-- =====================================================================
-- 5. TOP 5 COMPANIES BY ROA — MOST RECENT PERIOD
-- =====================================================================

SELECT
    company_name,
    ticker,
    industry_name,
    fiscal_year,
    fiscal_quarter,
    roa_pct,
    roa_rank_overall

FROM MART.COMPANY_RANKINGS r

WHERE NOT EXISTS (
    SELECT 1
    FROM MART.COMPANY_RANKINGS newer
    WHERE
        newer.fiscal_year > r.fiscal_year
        OR (
            newer.fiscal_year = r.fiscal_year
            AND newer.fiscal_quarter > r.fiscal_quarter
        )
)

ORDER BY roa_rank_overall

LIMIT 5;