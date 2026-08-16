from finsight.data_generation.financial_data import generate_financials
from finsight.data_generation.reference_data import (
    generate_companies,
    generate_industries,
)


def test_generate_financials():
    industries = generate_industries()
    companies = generate_companies(
        count=5,
        industries=industries,
        seed=42,
    )

    records = generate_financials(
        companies=companies,
        start_year=2021,
        periods=20,
        seed=42,
    )

    assert len(records) == 100


def test_financial_grain_is_unique():
    industries = generate_industries()
    companies = generate_companies(
        count=5,
        industries=industries,
        seed=42,
    )

    records = generate_financials(
        companies=companies,
        periods=20,
        seed=42,
    )

    keys = [
        (
            record.company_id,
            record.fiscal_year,
            record.fiscal_quarter,
        )
        for record in records
    ]

    assert len(keys) == len(set(keys))


def test_financial_values_are_reasonable():
    industries = generate_industries()
    companies = generate_companies(
        count=5,
        industries=industries,
        seed=42,
    )

    records = generate_financials(
        companies=companies,
        periods=20,
        seed=42,
    )

    for record in records:
        assert record.revenue > 0
        assert record.operating_expenses > 0
        assert record.total_assets > 0
        assert record.total_liabilities >= 0
        assert record.total_debt >= 0


def test_financial_generation_is_deterministic():
    industries = generate_industries()
    companies = generate_companies(
        count=5,
        industries=industries,
        seed=42,
    )

    first = generate_financials(
        companies=companies,
        periods=20,
        seed=42,
    )

    second = generate_financials(
        companies=companies,
        periods=20,
        seed=42,
    )

    assert first == second

def test_financial_relationships_are_consistent():
    industries = generate_industries()
    companies = generate_companies(
        count=20,
        industries=industries,
        seed=42,
    )

    records = generate_financials(
        companies=companies,
        periods=20,
        seed=42,
    )

    for record in records:
        assert record.total_debt <= record.total_liabilities
        assert record.total_liabilities <= record.total_assets

        if record.net_income > 0:
            assert record.net_income <= record.revenue
