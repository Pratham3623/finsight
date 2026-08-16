from dataclasses import dataclass


@dataclass(frozen=True)
class FinancialProfile:
    revenue_min: float
    revenue_max: float
    annual_growth_min: float
    annual_growth_max: float
    operating_expense_ratio_min: float
    operating_expense_ratio_max: float
    tax_rate_min: float
    tax_rate_max: float
    debt_ratio_min: float
    debt_ratio_max: float
    asset_intensity_min: float
    asset_intensity_max: float


DEFAULT_PROFILE = FinancialProfile(
    revenue_min=100_000_000,
    revenue_max=10_000_000_000,
    annual_growth_min=0.03,
    annual_growth_max=0.10,
    operating_expense_ratio_min=0.65,
    operating_expense_ratio_max=0.85,
    tax_rate_min=0.18,
    tax_rate_max=0.28,
    debt_ratio_min=0.10,
    debt_ratio_max=0.40,
    asset_intensity_min=0.80,
    asset_intensity_max=1.50,
)


FINANCIAL_PROFILES: dict[str, FinancialProfile] = {
    "Technology": FinancialProfile(
        revenue_min=200_000_000,
        revenue_max=15_000_000_000,
        annual_growth_min=0.08,
        annual_growth_max=0.22,
        operating_expense_ratio_min=0.55,
        operating_expense_ratio_max=0.78,
        tax_rate_min=0.15,
        tax_rate_max=0.27,
        debt_ratio_min=0.05,
        debt_ratio_max=0.30,
        asset_intensity_min=0.40,
        asset_intensity_max=1.00,
    ),
    "Financial Services": FinancialProfile(
        revenue_min=300_000_000,
        revenue_max=20_000_000_000,
        annual_growth_min=0.04,
        annual_growth_max=0.12,
        operating_expense_ratio_min=0.45,
        operating_expense_ratio_max=0.75,
        tax_rate_min=0.18,
        tax_rate_max=0.30,
        debt_ratio_min=0.30,
        debt_ratio_max=0.70,
        asset_intensity_min=4.00,
        asset_intensity_max=10.00,
    ),
    "Healthcare": FinancialProfile(
        revenue_min=150_000_000,
        revenue_max=12_000_000_000,
        annual_growth_min=0.05,
        annual_growth_max=0.14,
        operating_expense_ratio_min=0.60,
        operating_expense_ratio_max=0.82,
        tax_rate_min=0.17,
        tax_rate_max=0.28,
        debt_ratio_min=0.10,
        debt_ratio_max=0.45,
        asset_intensity_min=0.80,
        asset_intensity_max=2.00,
    ),
    "Energy": FinancialProfile(
        revenue_min=500_000_000,
        revenue_max=25_000_000_000,
        annual_growth_min=0.02,
        annual_growth_max=0.10,
        operating_expense_ratio_min=0.60,
        operating_expense_ratio_max=0.88,
        tax_rate_min=0.20,
        tax_rate_max=0.32,
        debt_ratio_min=0.25,
        debt_ratio_max=0.65,
        asset_intensity_min=1.50,
        asset_intensity_max=4.00,
    ),
    "Utilities": FinancialProfile(
        revenue_min=400_000_000,
        revenue_max=15_000_000_000,
        annual_growth_min=0.02,
        annual_growth_max=0.07,
        operating_expense_ratio_min=0.65,
        operating_expense_ratio_max=0.88,
        tax_rate_min=0.20,
        tax_rate_max=0.30,
        debt_ratio_min=0.35,
        debt_ratio_max=0.70,
        asset_intensity_min=2.00,
        asset_intensity_max=5.00,
    ),
    "Consumer Goods": FinancialProfile(
        revenue_min=250_000_000,
        revenue_max=12_000_000_000,
        annual_growth_min=0.03,
        annual_growth_max=0.10,
        operating_expense_ratio_min=0.70,
        operating_expense_ratio_max=0.90,
        tax_rate_min=0.18,
        tax_rate_max=0.30,
        debt_ratio_min=0.15,
        debt_ratio_max=0.45,
        asset_intensity_min=0.80,
        asset_intensity_max=2.00,
    ),
    "Industrials": FinancialProfile(
        revenue_min=300_000_000,
        revenue_max=18_000_000_000,
        annual_growth_min=0.03,
        annual_growth_max=0.09,
        operating_expense_ratio_min=0.68,
        operating_expense_ratio_max=0.87,
        tax_rate_min=0.18,
        tax_rate_max=0.30,
        debt_ratio_min=0.20,
        debt_ratio_max=0.55,
        asset_intensity_min=1.50,
        asset_intensity_max=3.50,
    ),
}


def get_financial_profile(industry_name: str) -> FinancialProfile:
    """Return the financial profile for an industry."""
    return FINANCIAL_PROFILES.get(industry_name, DEFAULT_PROFILE)
