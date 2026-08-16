CREATE OR REPLACE VIEW industry_benchmarks AS
SELECT
    industry_id,
    industry_name,

    ROUND(AVG(revenue), 2) AS avg_revenue,

    ROUND(
        AVG(net_profit_margin_pct),
        2
    ) AS avg_net_profit_margin_pct,

    ROUND(
        AVG(operating_margin_pct),
        2
    ) AS avg_operating_margin_pct,

    ROUND(
        AVG(debt_to_assets_pct),
        2
    ) AS avg_debt_to_assets_pct,

    ROUND(
        AVG(roa_pct),
        2
    ) AS avg_roa_pct,

    ROUND(
        AVG(operating_cash_flow_margin_pct),
        2
    ) AS avg_operating_cash_flow_margin_pct,

    COUNT(DISTINCT company_id) AS company_count

FROM financial_metrics

GROUP BY
    industry_id,
    industry_name;