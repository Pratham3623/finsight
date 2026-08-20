from datetime import date

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field, field_validator

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


app = FastAPI(
    title="FinSight API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    overall_score: float
    overall_rank: int


class AIAnalysisResponse(BaseModel):
    company_id: int
    question: str
    answer: str


class AIPortfolioAnalysisResponse(BaseModel):
    question: str
    answer: str


class AIComparisonResponse(BaseModel):
    company_ids: list[int]
    question: str
    answer: str


# ============================================================
# REQUEST MODELS
# ============================================================


class AIAnalysisRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=4000,
    )

    company_id: int = Field(
        ...,
        gt=0,
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Question must not be empty."
            )

        return value


class AIPortfolioAnalysisRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=4000,
    )

    limit: int = Field(
        default=20,
        ge=1,
        le=100,
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Question must not be empty."
            )

        return value


class AIComparisonRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=4000,
    )

    company_ids: list[int] = Field(
        ...,
        min_length=2,
        max_length=10,
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Question must not be empty."
            )

        return value

    @field_validator("company_ids")
    @classmethod
    def validate_company_ids(
        cls,
        value: list[int],
    ) -> list[int]:
        if len(set(value)) != len(value):
            raise ValueError(
                "Company IDs must be unique."
            )

        if any(company_id <= 0 for company_id in value):
            raise ValueError(
                "Company IDs must be positive."
            )

        return value


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


# ============================================================
# READINESS
# ============================================================


@app.get(
    "/ready",
    response_model=HealthResponse,
)
def readiness() -> HealthResponse:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            cursor.fetchone()

        connection.close()

        return HealthResponse(
            status="ready",
        )

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Database not ready: {exc}",
        ) from exc


# ============================================================
# COMPANY METRICS
# ============================================================


@app.get(
    "/api/companies/{company_id}/metrics",
    response_model=list[CompanyMetricResponse],
)
def company_metrics(
    company_id: int,
) -> list[CompanyMetricResponse]:

    try:
        metrics = get_company_metrics(
            company_id,
        )

        return [
            CompanyMetricResponse.model_validate(metric)
            for metric in metrics
        ]

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


# ============================================================
# INDUSTRY BENCHMARKS
# ============================================================


@app.get(
    "/api/industries/benchmarks",
    response_model=list[IndustryBenchmarkResponse],
)
def industry_benchmarks() -> list[IndustryBenchmarkResponse]:

    try:
        benchmarks = get_industry_benchmarks()

        return [
            IndustryBenchmarkResponse.model_validate(
                benchmark
            )
            for benchmark in benchmarks
        ]

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


# ============================================================
# COMPANY SUMMARY
# ============================================================


@app.get(
    "/api/companies/{company_id}/summary",
    response_model=CompanySummaryResponse,
)
def company_summary(
    company_id: int,
) -> CompanySummaryResponse:

    try:
        summary = get_company_summary(
            company_id,
        )

        return CompanySummaryResponse(
            company_id=int(summary["company_id"]),
            company_name=str(summary["company_name"]),
            ticker=str(summary["ticker"]),
            industry=str(summary["industry"]),
            latest_period=summary["latest_period"],
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
# COMPANY RANKINGS
# ============================================================


@app.get(
    "/api/rankings",
    response_model=list[CompanyRankingResponse],
)
def company_rankings() -> list[CompanyRankingResponse]:

    try:
        rankings = get_company_rankings()

        return [
            CompanyRankingResponse.model_validate(
                ranking
            )
            for ranking in rankings
        ]

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

    try:
        context = get_ai_company_context(
            request.company_id,
        )

        analyst = FinSightAnalyst()

        answer = analyst.analyze(
            question=request.question,
            financial_context=context,
        )

        return AIAnalysisResponse(
            company_id=request.company_id,
            question=request.question,
            answer=answer,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "AI analysis runtime error: "
                f"{type(exc).__name__}: {exc}"
            ),
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

    try:
        context = get_ai_portfolio_context(
            request.limit,
        )

        analyst = FinSightAnalyst()

        answer = analyst.analyze(
            question=request.question,
            financial_context=context,
        )

        return AIPortfolioAnalysisResponse(
            question=request.question,
            answer=answer,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "AI portfolio runtime error: "
                f"{type(exc).__name__}: {exc}"
            ),
        ) from exc


# ============================================================
# AI — COMPARISON
# ============================================================


@app.post(
    "/api/ai/compare",
    response_model=AIComparisonResponse,
)
def ai_compare(
    request: AIComparisonRequest,
) -> AIComparisonResponse:

    try:
        context = get_ai_comparison_context(
            request.company_ids,
        )

        analyst = FinSightAnalyst()

        answer = analyst.analyze(
            question=request.question,
            financial_context=context,
        )

        return AIComparisonResponse(
            company_ids=request.company_ids,
            question=request.question,
            answer=answer,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "AI comparison runtime error: "
                f"{type(exc).__name__}: {exc}"
            ),
        ) from exc
