from finsight.analytics.service import (
    get_company_metrics,
    get_company_rankings,
    get_company_summary,
    get_industry_benchmarks,
)


def test_company_metrics():
    metrics = get_company_metrics(1)

    assert len(metrics) > 0
    assert metrics[0].company_id == 1
    assert metrics[0].revenue > 0
    assert metrics[0].net_profit_margin_pct >= 0


def test_industry_benchmarks():
    benchmarks = get_industry_benchmarks()

    assert len(benchmarks) == 20

    for benchmark in benchmarks:
        assert benchmark.company_count > 0
        assert benchmark.avg_revenue > 0


def test_company_rankings():
    rankings = get_company_rankings(limit=10)

    assert len(rankings) == 10

    for ranking in rankings:
        assert ranking.roa_rank > 0
        assert ranking.avg_revenue > 0


def test_company_summary():
    summary = get_company_summary(1)

    assert summary["company_id"] == 1
    assert summary["ticker"]
    assert summary["latest_revenue"] > 0
    assert summary["periods_available"] > 0


def test_invalid_ranking_limit():
    try:
        get_company_rankings(limit=0)
    except ValueError as exc:
        assert "greater than zero" in str(exc)
    else:
        raise AssertionError("Expected ValueError")