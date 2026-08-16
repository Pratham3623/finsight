from finsight.data_generation.financial_profiles import (
    DEFAULT_PROFILE,
    get_financial_profile,
)


def test_known_industry_profile():
    profile = get_financial_profile("Technology")

    assert profile.annual_growth_min == 0.08
    assert profile.annual_growth_max == 0.22


def test_unknown_industry_uses_default_profile():
    profile = get_financial_profile("Unknown Industry")

    assert profile == DEFAULT_PROFILE


def test_profile_ranges_are_valid():
    profile = get_financial_profile("Technology")

    assert profile.revenue_min < profile.revenue_max
    assert profile.annual_growth_min < profile.annual_growth_max
    assert profile.operating_expense_ratio_min < profile.operating_expense_ratio_max
    assert profile.tax_rate_min < profile.tax_rate_max
    assert profile.debt_ratio_min < profile.debt_ratio_max
    assert profile.asset_intensity_min < profile.asset_intensity_max


def test_all_supported_industries_have_profiles():
    from finsight.data_generation.financial_profiles import FINANCIAL_PROFILES
    from finsight.data_generation.reference_data import generate_industries

    industries = generate_industries()

    for industry in industries:
        assert industry.industry_name in FINANCIAL_PROFILES
