from finsight.data_generation.reference_data import (
    generate_companies,
    generate_industries,
)


def test_generate_industries():
    industries = generate_industries()

    assert len(industries) == 20
    assert industries[0].industry_id == 1
    assert industries[0].industry_name == "Technology"


def test_generate_companies():
    industries = generate_industries()

    companies = generate_companies(
        count=100,
        industries=industries,
        seed=42,
    )

    assert len(companies) == 100
    assert len({company.company_id for company in companies}) == 100
    assert all(company.industry_id <= 20 for company in companies)


def test_company_generation_is_deterministic():
    industries = generate_industries()

    first = generate_companies(
        count=10,
        industries=industries,
        seed=42,
    )

    second = generate_companies(
        count=10,
        industries=industries,
        seed=42,
    )

    assert first == second
