/* =====================================================================
   FINSIGHT — PHASE 9: SNOWFLAKE WAREHOUSE
   06_verification.sql

   PURPOSE
   -------
   End-to-end verification across RAW, STAGING, CORE and MART.

   Healthy checks should return zero bad rows or matching values.
   ===================================================================== */

USE DATABASE FINSIGHT;


-- =====================================================================
-- 1. ROW COUNTS ACROSS ALL LAYERS
-- =====================================================================

SELECT
    'RAW.INDUSTRIES' AS object_name,
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
FROM RAW.FINANCIALS

UNION ALL

SELECT
    'STAGING.STG_INDUSTRIES',
    COUNT(*)
FROM STAGING.STG_INDUSTRIES

UNION ALL

SELECT
    'STAGING.STG_COMPANIES',
    COUNT(*)
FROM STAGING.STG_COMPANIES

UNION ALL

SELECT
    'STAGING.STG_FINANCIALS',
    COUNT(*)
FROM STAGING.STG_FINANCIALS

UNION ALL

SELECT
    'CORE.DIM_INDUSTRY',
    COUNT(*)
FROM CORE.DIM_INDUSTRY

UNION ALL

SELECT
    'CORE.DIM_COMPANY',
    COUNT(*)
FROM CORE.DIM_COMPANY

UNION ALL

SELECT
    'CORE.DIM_DATE',
    COUNT(*)
FROM CORE.DIM_DATE

UNION ALL

SELECT
    'CORE.FACT_FINANCIALS',
    COUNT(*)
FROM CORE.FACT_FINANCIALS

UNION ALL

SELECT
    'MART.COMPANY_PERFORMANCE',
    COUNT(*)
FROM MART.COMPANY_PERFORMANCE

UNION ALL

SELECT
    'MART.INDUSTRY_PERFORMANCE',
    COUNT(*)
FROM MART.INDUSTRY_PERFORMANCE

UNION ALL

SELECT
    'MART.COMPANY_RANKINGS',
    COUNT(*)
FROM MART.COMPANY_RANKINGS

ORDER BY object_name;


-- =====================================================================
-- 2. NATURAL KEY UNIQUENESS
-- =====================================================================

SELECT
    'duplicate industry_id in STG_INDUSTRIES' AS check_name,
    COUNT(*) AS bad_rows
FROM (
    SELECT industry_id
    FROM STAGING.STG_INDUSTRIES
    GROUP BY industry_id
    HAVING COUNT(*) > 1
)

UNION ALL

SELECT
    'duplicate company_id in STG_COMPANIES',
    COUNT(*)
FROM (
    SELECT company_id
    FROM STAGING.STG_COMPANIES
    GROUP BY company_id
    HAVING COUNT(*) > 1
)

UNION ALL

SELECT
    'duplicate financial_id in STG_FINANCIALS',
    COUNT(*)
FROM (
    SELECT financial_id
    FROM STAGING.STG_FINANCIALS
    GROUP BY financial_id
    HAVING COUNT(*) > 1
)

UNION ALL

SELECT
    'duplicate financial_id in FACT_FINANCIALS',
    COUNT(*)
FROM (
    SELECT financial_id
    FROM CORE.FACT_FINANCIALS
    GROUP BY financial_id
    HAVING COUNT(*) > 1
);


-- =====================================================================
-- 3. REFERENTIAL INTEGRITY
-- =====================================================================

SELECT
    'fact rows with no matching company' AS check_name,
    COUNT(*) AS bad_rows
FROM CORE.FACT_FINANCIALS f
LEFT JOIN CORE.DIM_COMPANY c
    ON f.company_key = c.company_key
WHERE c.company_key IS NULL

UNION ALL

SELECT
    'fact rows with no matching date',
    COUNT(*)
FROM CORE.FACT_FINANCIALS f
LEFT JOIN CORE.DIM_DATE d
    ON f.date_key = d.date_key
WHERE d.date_key IS NULL

UNION ALL

SELECT
    'companies with no matching industry',
    COUNT(*)
FROM CORE.DIM_COMPANY c
LEFT JOIN CORE.DIM_INDUSTRY i
    ON c.industry_key = i.industry_key
WHERE c.industry_key IS NOT NULL
  AND i.industry_key IS NULL;


-- =====================================================================
-- 4. RAW -> STAGING -> CORE ROW COUNT DRIFT
-- =====================================================================

SELECT
    (SELECT COUNT(*) FROM RAW.FINANCIALS)
        AS raw_financials_rows,

    (SELECT COUNT(*) FROM STAGING.STG_FINANCIALS)
        AS staging_financials_rows,

    (SELECT COUNT(*) FROM CORE.FACT_FINANCIALS)
        AS core_fact_rows,

    (
        SELECT COUNT(*)
        FROM RAW.FINANCIALS
    )
    -
    (
        SELECT COUNT(*)
        FROM STAGING.STG_FINANCIALS
    )
        AS raw_to_staging_delta,

    (
        SELECT COUNT(*)
        FROM STAGING.STG_FINANCIALS
    )
    -
    (
        SELECT COUNT(*)
        FROM CORE.FACT_FINANCIALS
    )
        AS staging_to_core_delta;


-- =====================================================================
-- 5. REQUIRED FACT COLUMN NULL CHECKS
-- =====================================================================

SELECT
    SUM(IFF(financial_id IS NULL, 1, 0))
        AS null_financial_id,

    SUM(IFF(company_key IS NULL, 1, 0))
        AS null_company_key,

    SUM(IFF(date_key IS NULL, 1, 0))
        AS null_date_key,

    SUM(IFF(fiscal_year IS NULL, 1, 0))
        AS null_fiscal_year,

    SUM(IFF(fiscal_quarter IS NULL, 1, 0))
        AS null_fiscal_quarter,

    SUM(IFF(revenue IS NULL, 1, 0))
        AS null_revenue,

    SUM(IFF(net_income IS NULL, 1, 0))
        AS null_net_income,

    SUM(IFF(total_assets IS NULL, 1, 0))
        AS null_total_assets,

    SUM(IFF(revenue_growth_yoy_pct IS NULL, 1, 0))
        AS null_yoy_growth_expected_for_first_period

FROM CORE.FACT_FINANCIALS;


-- =====================================================================
-- 6. METRIC SANITY CHECK
-- =====================================================================

SELECT
    financial_id,

    revenue,
    net_income,

    net_profit_margin_pct AS stored_margin,

    ROUND(
        100 * net_income / NULLIF(revenue, 0),
        4
    ) AS recomputed_margin,

    (
        net_profit_margin_pct =
        ROUND(
            100 * net_income / NULLIF(revenue, 0),
            4
        )
    ) AS matches

FROM CORE.FACT_FINANCIALS

LIMIT 5;


-- =====================================================================
-- 7. MART VS CORE REVENUE RECONCILIATION
-- =====================================================================

SELECT
    (
        SELECT SUM(revenue)
        FROM CORE.FACT_FINANCIALS
    ) AS core_total_revenue,

    (
        SELECT SUM(revenue)
        FROM MART.COMPANY_PERFORMANCE
    ) AS mart_total_revenue,

    (
        SELECT SUM(revenue)
        FROM CORE.FACT_FINANCIALS
    )
    =
    (
        SELECT SUM(revenue)
        FROM MART.COMPANY_PERFORMANCE
    ) AS totals_match;


-- =====================================================================
-- 8. RANKING SANITY CHECK
-- =====================================================================
-- A company ranked #1 by ROA should have the maximum ROA in its
-- fiscal year / fiscal quarter partition.

SELECT
    r.fiscal_year,
    r.fiscal_quarter,
    r.company_name,
    r.roa_pct

FROM MART.COMPANY_RANKINGS r

WHERE r.roa_rank_overall = 1

QUALIFY
    r.roa_pct <
    MAX(r.roa_pct) OVER (
        PARTITION BY
            r.fiscal_year,
            r.fiscal_quarter
    );

-- Expected result: 0 rows.


-- =====================================================================
-- 9. FINAL WAREHOUSE OBJECT CHECK
-- =====================================================================

SELECT
    'CORE' AS layer,
    COUNT(*) AS object_count
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'CORE'

UNION ALL

SELECT
    'MART',
    COUNT(*)
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'MART'

UNION ALL

SELECT
    'STAGING',
    COUNT(*)
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'STAGING'

UNION ALL

SELECT
    'RAW',
    COUNT(*)
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'RAW';