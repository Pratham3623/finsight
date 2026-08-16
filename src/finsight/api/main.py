from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

from finsight.analytics.models import (
    CompanyMetric,
    CompanyRanking,
    IndustryBenchmark,
)
from finsight.analytics.service import (
    get_company_metrics,
    get_company_rankings,
    get_company_summary,
    get_industry_benchmarks,
)
from finsight.database.connection import get_connection


class HealthResponse(BaseModel):
    status: str


class CompanyMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    financial_id: int
    company_id: int
    company_name: str
    ticker: str
    industry_name: str
    fiscal_year: int
    fiscal_quarter: int
    period_end_date: date
    revenue: float
    net_income: float
    net_profit_margin_pct: float
    operating_margin_pct: float
    debt_to_assets_pct: float
    debt_to_equity_pct: float
    roa_pct: float
    operating_cash_flow_margin_pct: float


class CompanyRankingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_id: int
    company_name: str
    ticker: str
    industry_name: str
    avg_revenue: float
    avg_net_profit_margin_pct: float
    avg_roa_pct: float
    avg_revenue_growth_yoy_pct: float
    roa_rank: int
    revenue_rank: int


class IndustryBenchmarkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    industry_id: int
    industry_name: str
    avg_revenue: float
    avg_net_profit_margin_pct: float
    avg_operating_margin_pct: float
    avg_debt_to_assets_pct: float
    avg_roa_pct: float
    avg_operating_cash_flow_margin_pct: float
    company_count: int


class CompanySummaryResponse(BaseModel):
    company_id: int
    company_name: str
    ticker: str
    industry: str
    latest_period: date
    latest_revenue: float
    latest_net_income: float
    latest_net_profit_margin_pct: float
    latest_roa_pct: float
    latest_debt_to_assets_pct: float
    periods_available: int


app = FastAPI(
    title="FinSight API",
    description="Financial analytics API",
    version="1.0.0",
)


@app.get(
    "/health",
    response_model=HealthResponse,
)
def health() -> HealthResponse:
    return HealthResponse(status="healthy")


@app.get(
    "/ready",
    response_model=HealthResponse,
)
def readiness() -> HealthResponse:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Database is not ready.",
        ) from exc

    return HealthResponse(status="ready")


@app.get("/api/companies/rankings")
def company_rankings(
    limit: int = 20,
) -> list[CompanyRanking]:
    if limit <= 0:
        raise HTTPException(
            status_code=400,
            detail="Limit must be greater than zero.",
        )

    if limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must not exceed 100.",
        )

    try:
        return get_company_rankings(limit)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.get(
    "/api/industries/benchmarks",
    response_model=list[IndustryBenchmarkResponse],
)
def industry_benchmarks() -> list[IndustryBenchmark]:
    return get_industry_benchmarks()


@app.get(
    "/api/companies/{company_id}/metrics",
    response_model=list[CompanyMetricResponse],
)
def company_metrics(
    company_id: int,
) -> list[CompanyMetric]:
    metrics = get_company_metrics(company_id)

    if not metrics:
        raise HTTPException(
            status_code=404,
            detail=f"Company {company_id} was not found.",
        )

    return metrics


@app.get(
    "/api/companies/{company_id}",
    response_model=CompanySummaryResponse,
)
def company_summary(
    company_id: int,
) -> CompanySummaryResponse:
    try:
        summary = get_company_summary(company_id)

        return CompanySummaryResponse(
            company_id=int(summary["company_id"]),
            company_name=str(summary["company_name"]),
            ticker=str(summary["ticker"]),
            industry=str(summary["industry"]),
            latest_period=summary["latest_period"],
            latest_revenue=float(summary["latest_revenue"]),
            latest_net_income=float(summary["latest_net_income"]),
            latest_net_profit_margin_pct=float(
                summary["latest_net_profit_margin_pct"]
            ),
            latest_roa_pct=float(
                summary["latest_roa_pct"]
            ),
            latest_debt_to_assets_pct=float(
                summary["latest_debt_to_assets_pct"]
            ),
            periods_available=int(
                summary["periods_available"]
            ),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc