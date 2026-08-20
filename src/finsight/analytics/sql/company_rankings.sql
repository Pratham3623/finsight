CREATE OR REPLACE VIEW company_rankings AS
WITH ranked AS (
    SELECT
        company_id,
        company_name,
        ticker,
        industry_name,

        ROUND(AVG(revenue), 2) AS avg_revenue,

        ROUND(
            AVG(net_profit_margin_pct),
            2
        ) AS avg_net_profit_margin_pct,

        ROUND(
            AVG(roa_pct),
            2
        ) AS avg_roa_pct,

        ROUND(
            AVG(revenue_growth_yoy_pct),
            2
        ) AS avg_revenue_growth_yoy_pct,

        RANK() OVER (
            ORDER BY AVG(roa_pct) DESC
        ) AS roa_rank,

        RANK() OVER (
            ORDER BY AVG(revenue) DESC
        ) AS revenue_rank

    FROM financial_growth

    GROUP BY
        company_id,
        company_name,
        ticker,
        industry_name
),

scored AS (
    SELECT
        *,
        ROUND(
            (
                (100.0 - roa_rank + 1.0)
                +
                (100.0 - revenue_rank + 1.0)
            ) / 2.0,
            2
        ) AS overall_score
    FROM ranked
)

SELECT
    company_id,
    company_name,
    ticker,
    industry_name,
    avg_revenue,
    avg_net_profit_margin_pct,
    avg_roa_pct,
    avg_revenue_growth_yoy_pct,
    roa_rank,
    revenue_rank,
    overall_score,

    RANK() OVER (
        ORDER BY overall_score DESC
    ) AS overall_rank

FROM scored;
