from fastapi import FastAPI, HTTPException

from finsight.analytics.service import (
    get_company_metrics,
    get_company_rankings,
    get_company_summary,
    get_industry_benchmarks,
)


app = FastAPI(
    title="FinSight API",
    description="Financial analytics API",
    version="1.0.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


# Static routes MUST come before /{company_id}
@app.get("/api/companies/rankings")
def company_rankings(limit: int = 20):
    try:
        return get_company_rankings(limit)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.get("/api/industries/benchmarks")
def industry_benchmarks():
    return get_industry_benchmarks()


@app.get("/api/companies/{company_id}/metrics")
def company_metrics(company_id: int):
    metrics = get_company_metrics(company_id)

    if not metrics:
        raise HTTPException(
            status_code=404,
            detail=f"Company {company_id} was not found.",
        )

    return metrics


@app.get("/api/companies/{company_id}")
def company_summary(company_id: int):
    try:
        return get_company_summary(company_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc