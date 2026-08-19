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
        "latest_revenue": float(latest.revenue),
        "latest_net_income": float(latest.net_income),
        "latest_net_profit_margin_pct": float(
            latest.net_profit_margin_pct
        ),
        "latest_roa_pct": float(latest.roa_pct),
        "latest_debt_to_assets_pct": float(
            latest.debt_to_assets_pct
        ),
        "periods_available": len(metrics),
    }


def _to_float(value: Any) -> float:
    return float(value)


def _calculate_change(
    first_value: Any,
    last_value: Any,
) -> float | None:
    if first_value is None or last_value is None:
        return None

    return round(
        _to_float(last_value) - _to_float(first_value),
        2,
    )


def _calculate_percentage_change(
    first_value: Any,
    last_value: Any,
) -> float | None:
    if first_value is None or last_value is None:
        return None

    first = _to_float(first_value)
    last = _to_float(last_value)

    if first == 0:
        return None

    return round(
        ((last - first) / abs(first)) * 100,
        2,
    )


def _calculate_cagr(
    first_value: Any,
    last_value: Any,
    periods: int,
) -> float | None:
    if first_value is None or last_value is None:
        return None

    if periods <= 0:
        return None

    first = _to_float(first_value)
    last = _to_float(last_value)

    if first <= 0 or last <= 0:
        return None

    return round(
        (
            (last / first)
            ** (1.0 / float(periods))
            - 1.0
        )
        * 100.0,
        2,
    )


def _classify_revenue(
    percentage_change: float | None,
) -> dict[str, Any]:
    if percentage_change is None:
        return {
            "classification": "insufficient_data",
            "reason": "Revenue change could not be calculated.",
        }

    if percentage_change >= 20:
        return {
            "classification": "strong",
            "reason": "Revenue increased by at least 20%.",
        }

    if percentage_change >= 5:
        return {
            "classification": "positive",
            "reason": "Revenue increased by at least 5%.",
        }

    if percentage_change > -5:
        return {
            "classification": "stable",
            "reason": "Revenue remained within a 5% range.",
        }

    return {
        "classification": "weak",
        "reason": "Revenue declined by more than 5%.",
    }


def _classify_profitability(
    net_profit_margin_pct: float | None,
    roa_pct: float | None,
    roa_change: float | None,
) -> dict[str, Any]:
    if (
        net_profit_margin_pct is None
        or roa_pct is None
    ):
        return {
            "classification": "insufficient_data",
            "reason": "Profitability data is incomplete.",
        }

    if (
        net_profit_margin_pct >= 10
        and roa_pct >= 5
        and (roa_change is None or roa_change >= 0)
    ):
        return {
            "classification": "strong",
            "reason": (
                "Profit margin and ROA are healthy with "
                "no deterioration in ROA."
            ),
        }

    if (
        net_profit_margin_pct >= 5
        and roa_pct >= 3
    ):
        if roa_change is not None and roa_change < -2:
            return {
                "classification": "watch",
                "reason": (
                    "Profitability remains positive but "
                    "ROA has deteriorated."
                ),
            }

        return {
            "classification": "positive",
            "reason": (
                "Profit margin and ROA remain positive."
            ),
        }

    return {
        "classification": "weak",
        "reason": (
            "Profitability metrics are relatively weak."
        ),
    }


def _classify_debt(
    debt_to_assets_pct: float | None,
    debt_change: float | None,
) -> dict[str, Any]:
    if debt_to_assets_pct is None:
        return {
            "classification": "insufficient_data",
            "reason": "Debt-to-assets data is unavailable.",
        }

    if debt_to_assets_pct >= 60:
        classification = "high"
    elif debt_to_assets_pct >= 40:
        classification = "moderate"
    else:
        classification = "low"

    if debt_change is not None:
        if debt_change <= -5:
            direction = "improving"
        elif debt_change >= 5:
            direction = "deteriorating"
        else:
            direction = "stable"
    else:
        direction = "unknown"

    return {
        "classification": classification,
        "direction": direction,
        "reason": (
            f"Debt-to-assets is {debt_to_assets_pct:.2f}% "
            f"and the long-term direction is {direction}."
        ),
    }


def _build_strengths_and_risks(
    classifications: dict[str, Any],
) -> dict[str, Any]:
    strengths: list[dict[str, str]] = []
    risks: list[dict[str, str]] = []

    revenue_class = classifications["revenue"][
        "classification"
    ]

    if revenue_class in {"strong", "positive"}:
        strengths.append(
            {
                "area": "revenue",
                "classification": revenue_class,
                "reason": classifications["revenue"][
                    "reason"
                ],
            }
        )

    profitability_class = classifications[
        "profitability"
    ]["classification"]

    if profitability_class in {"strong", "positive"}:
        strengths.append(
            {
                "area": "profitability",
                "classification": profitability_class,
                "reason": classifications["profitability"][
                    "reason"
                ],
            }
        )

    debt_class = classifications["debt"][
        "classification"
    ]

    debt_direction = classifications["debt"].get(
        "direction"
    )

    if debt_direction == "improving":
        strengths.append(
            {
                "area": "debt",
                "classification": "improving",
                "reason": classifications["debt"][
                    "reason"
                ],
            }
        )

    if profitability_class in {"watch", "weak"}:
        risks.append(
            {
                "area": "profitability",
                "classification": profitability_class,
                "reason": classifications["profitability"][
                    "reason"
                ],
            }
        )

    if revenue_class == "weak":
        risks.append(
            {
                "area": "revenue",
                "classification": "weak",
                "reason": classifications["revenue"][
                    "reason"
                ],
            }
        )

    if debt_class == "high":
        risks.append(
            {
                "area": "debt",
                "classification": "high",
                "reason": classifications["debt"][
                    "reason"
                ],
            }
        )

    if debt_direction == "deteriorating":
        risks.append(
            {
                "area": "debt",
                "classification": "deteriorating",
                "reason": classifications["debt"][
                    "reason"
                ],
            }
        )

    return {
        "strengths": strengths,
        "risks": risks,
    }


def _build_trend(
    metrics: list[CompanyMetric],
) -> dict[str, Any]:
    if not metrics:
        return {}

    first = metrics[0]
    latest = metrics[-1]

    period_count = len(metrics) - 1

    return {
        "periods_analyzed": len(metrics),
        "first_period": {
            "fiscal_year": first.fiscal_year,
            "fiscal_quarter": first.fiscal_quarter,
        },
        "latest_period": {
            "fiscal_year": latest.fiscal_year,
            "fiscal_quarter": latest.fiscal_quarter,
        },
        "revenue": {
            "first_value": _to_float(first.revenue),
            "latest_value": _to_float(latest.revenue),
            "absolute_change": _calculate_change(
                first.revenue,
                latest.revenue,
            ),
            "percentage_change": (
                _calculate_percentage_change(
                    first.revenue,
                    latest.revenue,
                )
            ),
            "cagr_pct": _calculate_cagr(
                first.revenue,
                latest.revenue,
                period_count,
            ),
        },
        "net_income": {
            "first_value": _to_float(first.net_income),
            "latest_value": _to_float(latest.net_income),
            "absolute_change": _calculate_change(
                first.net_income,
                latest.net_income,
            ),
            "percentage_change": (
                _calculate_percentage_change(
                    first.net_income,
                    latest.net_income,
                )
            ),
        },
        "roa": {
            "first_value_pct": _to_float(first.roa_pct),
            "latest_value_pct": _to_float(latest.roa_pct),
            "change_percentage_points": _calculate_change(
                first.roa_pct,
                latest.roa_pct,
            ),
        },
        "debt_to_assets": {
            "first_value_pct": _to_float(
                first.debt_to_assets_pct
            ),
            "latest_value_pct": _to_float(
                latest.debt_to_assets_pct
            ),
            "change_percentage_points": _calculate_change(
                first.debt_to_assets_pct,
                latest.debt_to_assets_pct,
            ),
        },
        "net_profit_margin": {
            "first_value_pct": _to_float(
                first.net_profit_margin_pct
            ),
            "latest_value_pct": _to_float(
                latest.net_profit_margin_pct
            ),
            "change_percentage_points": _calculate_change(
                first.net_profit_margin_pct,
                latest.net_profit_margin_pct,
            ),
        },
    }


def _build_risk_indicators(
    metrics: list[CompanyMetric],
) -> dict[str, Any]:
    latest = metrics[-1]

    return {
        "debt_to_assets_pct": _to_float(
            latest.debt_to_assets_pct
        ),
        "debt_to_equity_pct": _to_float(
            latest.debt_to_equity_pct
        ),
        "roa_pct": _to_float(latest.roa_pct),
        "net_profit_margin_pct": _to_float(
            latest.net_profit_margin_pct
        ),
        "operating_cash_flow_margin_pct": _to_float(
            latest.operating_cash_flow_margin_pct
        ),
    }


def _build_classifications(
    metrics: list[CompanyMetric],
    trends: dict[str, Any],
) -> dict[str, Any]:
    latest = metrics[-1]

    classifications = {
        "revenue": _classify_revenue(
            trends["revenue"]["percentage_change"]
        ),
        "profitability": _classify_profitability(
            _to_float(latest.net_profit_margin_pct),
            _to_float(latest.roa_pct),
            trends["roa"]["change_percentage_points"],
        ),
        "debt": _classify_debt(
            _to_float(latest.debt_to_assets_pct),
            trends["debt_to_assets"][
                "change_percentage_points"
            ],
        ),
    }

    classifications["overall"] = (
        _build_strengths_and_risks(
            classifications
        )
    )

    return classifications


def get_ai_company_context(
    company_id: int,
) -> dict[str, Any]:
    metrics = get_company_metrics(company_id)

    if not metrics:
        raise ValueError(
            f"Company {company_id} was not found."
        )

    latest = metrics[-1]

    trends = _build_trend(metrics)

    classifications = _build_classifications(
        metrics,
        trends,
    )

    return {
        "company": {
            "company_id": latest.company_id,
            "company_name": latest.company_name,
            "ticker": latest.ticker,
            "industry": latest.industry_name,
        },
        "latest_period": {
            "fiscal_year": latest.fiscal_year,
            "fiscal_quarter": latest.fiscal_quarter,
            "period_end_date": latest.period_end_date,
        },
        "latest_metrics": {
            "revenue": _to_float(latest.revenue),
            "net_income": _to_float(latest.net_income),
            "net_profit_margin_pct": _to_float(
                latest.net_profit_margin_pct
            ),
            "operating_margin_pct": _to_float(
                latest.operating_margin_pct
            ),
            "debt_to_assets_pct": _to_float(
                latest.debt_to_assets_pct
            ),
            "debt_to_equity_pct": _to_float(
                latest.debt_to_equity_pct
            ),
            "roa_pct": _to_float(latest.roa_pct),
            "operating_cash_flow_margin_pct": _to_float(
                latest.operating_cash_flow_margin_pct
            ),
        },
        "deterministic_analysis": {
            "trends": trends,
            "risk_indicators": _build_risk_indicators(
                metrics
            ),
            "classifications": classifications,
        },
        "historical_periods": [
            {
                "fiscal_year": metric.fiscal_year,
                "fiscal_quarter": metric.fiscal_quarter,
                "revenue": _to_float(metric.revenue),
                "net_income": _to_float(metric.net_income),
                "net_profit_margin_pct": _to_float(
                    metric.net_profit_margin_pct
                ),
                "roa_pct": _to_float(metric.roa_pct),
                "debt_to_assets_pct": _to_float(
                    metric.debt_to_assets_pct
                ),
            }
            for metric in metrics
        ],
    }


# ============================================================
# PHASE 11.4 — PORTFOLIO / COMPARATIVE ANALYTICS
# ============================================================


def get_ai_portfolio_context(
    limit: int = 20,
) -> dict[str, Any]:
    """
    Build a grounded portfolio-level context for AI.

    This deliberately uses the existing deterministic
    company_rankings and industry_benchmarks views.
    """

    if limit <= 0:
        raise ValueError(
            "Limit must be greater than zero."
        )

    if limit > 100:
        raise ValueError(
            "Limit must not exceed 100."
        )

    rankings = get_company_rankings(limit)

    industries = get_industry_benchmarks()

    return {
        "portfolio": {
            "companies_in_context": len(rankings),
            "industries_in_context": len(industries),
        },
        "company_rankings": [
            {
                "company_id": company.company_id,
                "company_name": company.company_name,
                "ticker": company.ticker,
                "industry_name": company.industry_name,
                "avg_revenue": _to_float(
                    company.avg_revenue
                ),
                "avg_net_profit_margin_pct": _to_float(
                    company.avg_net_profit_margin_pct
                ),
                "avg_roa_pct": _to_float(
                    company.avg_roa_pct
                ),
                "avg_revenue_growth_yoy_pct": _to_float(
                    company.avg_revenue_growth_yoy_pct
                ),
                "roa_rank": company.roa_rank,
                "revenue_rank": company.revenue_rank,
            }
            for company in rankings
        ],
        "industry_benchmarks": [
            {
                "industry_id": industry.industry_id,
                "industry_name": industry.industry_name,
                "avg_revenue": _to_float(
                    industry.avg_revenue
                ),
                "avg_net_profit_margin_pct": _to_float(
                    industry.avg_net_profit_margin_pct
                ),
                "avg_operating_margin_pct": _to_float(
                    industry.avg_operating_margin_pct
                ),
                "avg_debt_to_assets_pct": _to_float(
                    industry.avg_debt_to_assets_pct
                ),
                "avg_roa_pct": _to_float(
                    industry.avg_roa_pct
                ),
                "avg_operating_cash_flow_margin_pct": (
                    _to_float(
                        industry.avg_operating_cash_flow_margin_pct
                    )
                ),
                "company_count": industry.company_count,
            }
            for industry in industries
        ],
    }


def get_ai_comparison_context(
    company_ids: list[int],
) -> dict[str, Any]:
    """
    Build deterministic comparison context for multiple
    companies.

    Each company gets its latest metrics and historical
    deterministic analysis.
    """

    if not company_ids:
        raise ValueError(
            "At least one company ID is required."
        )

    unique_ids = list(dict.fromkeys(company_ids))

    if len(unique_ids) > 10:
        raise ValueError(
            "A maximum of 10 companies can be compared."
        )

    companies: list[dict[str, Any]] = []

    for company_id in unique_ids:
        context = get_ai_company_context(company_id)

        companies.append(context)

    return {
        "comparison": {
            "company_count": len(companies),
            "company_ids": unique_ids,
        },
        "companies": companies,
    }
