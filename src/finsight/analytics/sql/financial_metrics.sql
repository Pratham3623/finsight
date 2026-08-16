CREATE OR REPLACE VIEW financial_metrics AS
SELECT
    f.financial_id,
    f.company_id,
    c.company_name,
    c.ticker,
    c.industry_id,
    c.industry_name,
    f.fiscal_year,
    f.fiscal_quarter,
    f.period_end_date,

    f.revenue,
    f.operating_expenses,
    f.net_income,
    f.total_assets,
    f.total_liabilities,
    f.total_debt,
    f.operating_cash_flow,
    f.investing_cash_flow,
    f.financing_cash_flow,

    ROUND(
        (f.net_income / NULLIF(f.revenue, 0)) * 100,
        2
    ) AS net_profit_margin_pct,

    ROUND(
        (
            (f.revenue - f.operating_expenses)
            / NULLIF(f.revenue, 0)
        ) * 100,
        2
    ) AS operating_margin_pct,

    ROUND(
        (f.total_debt / NULLIF(f.total_assets, 0)) * 100,
        2
    ) AS debt_to_assets_pct,

    ROUND(
        (
            f.total_debt
            / NULLIF(
                f.total_assets - f.total_liabilities,
                0
            )
        ) * 100,
        2
    ) AS debt_to_equity_pct,

    ROUND(
        (f.net_income / NULLIF(f.total_assets, 0)) * 100,
        2
    ) AS roa_pct,

    ROUND(
        (f.operating_cash_flow / NULLIF(f.revenue, 0)) * 100,
        2
    ) AS operating_cash_flow_margin_pct

FROM financials f
JOIN companies c
    ON f.company_id = c.company_id;
CREATE OR REPLACE VIEW financial_growth AS
SELECT
    fm.*,

    ROUND(
        (
            fm.revenue
            / NULLIF(
                LAG(fm.revenue) OVER (
                    PARTITION BY fm.company_id
                    ORDER BY fm.period_end_date
                ),
                0
            ) - 1
        ) * 100,
        2
    ) AS revenue_growth_qoq_pct,

    ROUND(
        (
            fm.net_income
            / NULLIF(
                LAG(fm.net_income) OVER (
                    PARTITION BY fm.company_id
                    ORDER BY fm.period_end_date
                ),
                0
            ) - 1
        ) * 100,
        2
    ) AS net_income_growth_qoq_pct,

    ROUND(
        (
            fm.revenue
            / NULLIF(
                LAG(fm.revenue, 4) OVER (
                    PARTITION BY fm.company_id
                    ORDER BY fm.period_end_date
                ),
                0
            ) - 1
        ) * 100,
        2
    ) AS revenue_growth_yoy_pct

FROM financial_metrics fm;