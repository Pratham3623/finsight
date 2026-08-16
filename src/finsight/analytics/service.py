from typing import Any

from finsight.analytics.models import (
    CompanyMetric,
    CompanyRanking,
    IndustryBenchmark,
)
from finsight.database.loader import get_connection


def get_company_metrics(
    company_id: int,
) -> list[CompanyMetric]:
    sql = """
        SELECT
            financial_id,
            company_id,
            company_name,
            ticker,
            industry_name,
            fiscal_year,
            fiscal_quarter,
            period_end_date,
            revenue,
            net_income,
            net_profit_margin_pct,
            operating_margin_pct,
            debt_to_assets_pct,
            debt_to_equity_pct,
            roa_pct,
            operating_cash_flow_margin_pct
        FROM financial_metrics
        WHERE company_id = %s
        ORDER BY period_end_date;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, (company_id,))
            rows = cursor.fetchall()

    return [CompanyMetric(*row) for row in rows]


def get_industry_benchmarks() -> list[IndustryBenchmark]:
    sql = """
        SELECT
            industry_id,
            industry_name,
            avg_revenue,
            avg_net_profit_margin_pct,
            avg_operating_margin_pct,
            avg_debt_to_assets_pct,
            avg_roa_pct,
            avg_operating_cash_flow_margin_pct,
            company_count
        FROM industry_benchmarks
        ORDER BY avg_roa_pct DESC;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()

    return [IndustryBenchmark(*row) for row in rows]


def get_company_rankings(
    limit: int = 20,
) -> list[CompanyRanking]:
    if limit <= 0:
        raise ValueError("Limit must be greater than zero.")

    sql = """
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
            revenue_rank
        FROM company_rankings
        ORDER BY roa_rank
        LIMIT %s;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, (limit,))
            rows = cursor.fetchall()

    return [CompanyRanking(*row) for row in rows]


def get_company_summary(
    company_id: int,
) -> dict[str, Any]:
    metrics = get_company_metrics(company_id)

    if not metrics:
        raise ValueError(
            f"Company {company_id} was not found."
        )

    latest = metrics[-1]

    return {
        "company_id": latest.company_id,
        "company_name": latest.company_name,
        "ticker": latest.ticker,
        "industry": latest.industry_name,
        "latest_period": latest.period_end_date,
        "latest_revenue": latest.revenue,
        "latest_net_income": latest.net_income,
        "latest_net_profit_margin_pct": (
            latest.net_profit_margin_pct
        ),
        "latest_roa_pct": latest.roa_pct,
        "latest_debt_to_assets_pct": (
            latest.debt_to_assets_pct
        ),
        "periods_available": len(metrics),
    }