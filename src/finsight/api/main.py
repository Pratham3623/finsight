from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from finsight.ai.analyst import FinSightAnalyst
from finsight.analytics.models import (
    CompanyMetric,
    CompanyRanking,
    IndustryBenchmark,
)
from finsight.analytics.service import (
    get_ai_company_context,
    get_ai_comparison_context,
    get_ai_portfolio_context,
    get_company_metrics,
    get_company_rankings,
    get_company_summary,
    get_industry_benchmarks,
)
from finsight.database.connection import get_connection


# ============================================================
# RESPONSE MODELS
# ============================================================


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


# ============================================================
# AI REQUEST / RESPONSE MODELS
# ============================================================


class AIAnalysisRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=4000,
    )
    company_id: int = Field(
        ge=1,
    )


class AIAnalysisResponse(BaseModel):
    company_id: int
    question: str
    answer: str


class AIPortfolioAnalysisRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=4000,
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
    )


class AIPortfolioAnalysisResponse(BaseModel):
    question: str
    answer: str


class AIComparisonRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=4000,
    )
    company_ids: list[int] = Field(
        min_length=2,
        max_length=10,
    )


class AIComparisonResponse(BaseModel):
    company_ids: list[int]
    question: str
    answer: str


# ============================================================
# APPLICATION
# ============================================================


app = FastAPI(
    title="FinSight API",
    description="Financial analytics API",
    version="1.0.0",
)


# ============================================================
# HEALTH
# ============================================================


@app.get(
    "/health",
    response_model=HealthResponse,
)
def health() -> HealthResponse:
    return HealthResponse(
        status="healthy",
    )


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

    return HealthResponse(
        status="ready",
    )


# ============================================================
# COMPANY RANKINGS
# ============================================================


@app.get(
    "/api/companies/rankings",
)
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
        return get_company_rankings(
            limit,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


# ============================================================
# INDUSTRY BENCHMARKS
# ============================================================


@app.get(
    "/api/industries/benchmarks",
    response_model=list[IndustryBenchmarkResponse],
)
def industry_benchmarks() -> list[IndustryBenchmark]:
    return get_industry_benchmarks()


# ============================================================
# COMPANY METRICS
# ============================================================


@app.get(
    "/api/companies/{company_id}/metrics",
    response_model=list[CompanyMetricResponse],
)
def company_metrics(
    company_id: int,
) -> list[CompanyMetric]:

    if company_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Company ID must be greater than zero.",
        )

    metrics = get_company_metrics(
        company_id,
    )

    if not metrics:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Company {company_id} "
                "was not found."
            ),
        )

    return metrics


# ============================================================
# COMPANY SUMMARY
# ============================================================


@app.get(
    "/api/companies/{company_id}",
    response_model=CompanySummaryResponse,
)
def company_summary(
    company_id: int,
) -> CompanySummaryResponse:

    if company_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Company ID must be greater than zero.",
        )

    try:
        summary = get_company_summary(
            company_id,
        )

        return CompanySummaryResponse(
            company_id=int(
                summary["company_id"]
            ),
            company_name=str(
                summary["company_name"]
            ),
            ticker=str(
                summary["ticker"]
            ),
            industry=str(
                summary["industry"]
            ),
            latest_period=summary[
                "latest_period"
            ],
            latest_revenue=float(
                summary["latest_revenue"]
            ),
            latest_net_income=float(
                summary["latest_net_income"]
            ),
            latest_net_profit_margin_pct=float(
                summary[
                    "latest_net_profit_margin_pct"
                ]
            ),
            latest_roa_pct=float(
                summary["latest_roa_pct"]
            ),
            latest_debt_to_assets_pct=float(
                summary[
                    "latest_debt_to_assets_pct"
                ]
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


# ============================================================
# AI — SINGLE COMPANY
# ============================================================


@app.post(
    "/api/ai/analyze",
    response_model=AIAnalysisResponse,
)
def ai_analyze(
    request: AIAnalysisRequest,
) -> AIAnalysisResponse:

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question must not be empty.",
        )

    try:
        context = get_ai_company_context(
            request.company_id,
        )

        analyst = FinSightAnalyst()

        answer = analyst.analyze(
            question=question,
            financial_context=context,
        )

        return AIAnalysisResponse(
            company_id=request.company_id,
            question=question,
            answer=answer,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


# ============================================================
# AI — PORTFOLIO
# ============================================================


@app.post(
    "/api/ai/portfolio",
    response_model=AIPortfolioAnalysisResponse,
)
def ai_portfolio_analyze(
    request: AIPortfolioAnalysisRequest,
) -> AIPortfolioAnalysisResponse:

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question must not be empty.",
        )

    try:
        context = get_ai_portfolio_context(
            request.limit,
        )

        analyst = FinSightAnalyst()

        answer = analyst.analyze(
            question=question,
            financial_context=context,
        )

        return AIPortfolioAnalysisResponse(
            question=question,
            answer=answer,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


# ============================================================
# AI — COMPANY COMPARISON
# ============================================================


@app.post(
    "/api/ai/compare",
    response_model=AIComparisonResponse,
)
def ai_compare(
    request: AIComparisonRequest,
) -> AIComparisonResponse:

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question must not be empty.",
        )

    unique_ids = list(
        dict.fromkeys(
            request.company_ids
        )
    )

    if len(unique_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail=(
                "At least two unique "
                "company IDs are required."
            ),
        )

    try:
        context = get_ai_comparison_context(
            unique_ids,
        )

        analyst = FinSightAnalyst()

        answer = analyst.analyze(
            question=question,
            financial_context=context,
        )

        return AIComparisonResponse(
            company_ids=unique_ids,
            question=question,
            answer=answer,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc
