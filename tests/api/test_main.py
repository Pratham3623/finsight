from fastapi.testclient import TestClient

from finsight.api.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_company_summary():
    response = client.get("/api/companies/1")

    assert response.status_code == 200

    data = response.json()

    assert data["company_id"] == 1
    assert data["ticker"]
    assert data["latest_revenue"] > 0


def test_company_metrics():
    response = client.get("/api/companies/1/metrics")

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0
    assert data[0]["company_id"] == 1


def test_company_rankings():
    response = client.get("/api/companies/rankings?limit=10")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 10


def test_industry_benchmarks():
    response = client.get("/api/industries/benchmarks")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 20


def test_company_not_found():
    response = client.get("/api/companies/999999")

    assert response.status_code == 404


def test_invalid_ranking_limit():
    response = client.get("/api/companies/rankings?limit=0")

    assert response.status_code == 400
def test_ai_analysis_rejects_zero_company_id():
    response = client.post(
        "/api/ai/analyze",
        json={
            "question": "What is the revenue?",
            "company_id": 0,
        },
    )

    assert response.status_code == 422


def test_ai_analysis_rejects_negative_company_id():
    response = client.post(
        "/api/ai/analyze",
        json={
            "question": "What is the revenue?",
            "company_id": -1,
        },
    )

    assert response.status_code == 422


def test_ai_analysis_rejects_empty_question():
    response = client.post(
        "/api/ai/analyze",
        json={
            "question": "   ",
            "company_id": 1,
        },
    )

    assert response.status_code == 422


def test_ai_analysis_rejects_question_over_max_length():
    response = client.post(
        "/api/ai/analyze",
        json={
            "question": "x" * 4001,
            "company_id": 1,
        },
    )

    assert response.status_code == 422


def test_ai_portfolio_rejects_invalid_limit():
    response = client.post(
        "/api/ai/portfolio",
        json={
            "question": "Analyze the portfolio.",
            "limit": 0,
        },
    )

    assert response.status_code == 422


def test_ai_portfolio_rejects_limit_above_maximum():
    response = client.post(
        "/api/ai/portfolio",
        json={
            "question": "Analyze the portfolio.",
            "limit": 101,
        },
    )

    assert response.status_code == 422


def test_ai_comparison_rejects_negative_company_id():
    response = client.post(
        "/api/ai/compare",
        json={
            "question": "Compare these companies.",
            "company_ids": [1, -2],
        },
    )

    assert response.status_code == 422


def test_ai_comparison_rejects_zero_company_id():
    response = client.post(
        "/api/ai/compare",
        json={
            "question": "Compare these companies.",
            "company_ids": [1, 0],
        },
    )

    assert response.status_code == 422


def test_ai_comparison_rejects_duplicate_company_ids():
    response = client.post(
        "/api/ai/compare",
        json={
            "question": "Compare these companies.",
            "company_ids": [1, 1],
        },
    )

    assert response.status_code == 422


def test_ai_comparison_rejects_too_many_company_ids():
    response = client.post(
        "/api/ai/compare",
        json={
            "question": "Compare these companies.",
            "company_ids": list(range(1, 12)),
        },
    )

    assert response.status_code == 422
