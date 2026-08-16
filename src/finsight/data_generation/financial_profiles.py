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
        200_000_000, 15_000_000_000,
        0.08, 0.22,
        0.55, 0.78,
        0.15, 0.27,
        0.05, 0.30,
        0.40, 1.00,
    ),
    "Financial Services": FinancialProfile(
        300_000_000, 20_000_000_000,
        0.04, 0.12,
        0.45, 0.75,
        0.18, 0.30,
        0.30, 0.70,
        4.00, 10.00,
    ),
    "Healthcare": FinancialProfile(
        150_000_000, 12_000_000_000,
        0.05, 0.14,
        0.60, 0.82,
        0.17, 0.28,
        0.10, 0.45,
        0.80, 2.00,
    ),
    "Energy": FinancialProfile(
        500_000_000, 25_000_000_000,
        0.02, 0.10,
        0.60, 0.88,
        0.20, 0.32,
        0.25, 0.65,
        1.50, 4.00,
    ),
    "Consumer Goods": FinancialProfile(
        250_000_000, 12_000_000_000,
        0.03, 0.10,
        0.70, 0.90,
        0.18, 0.30,
        0.15, 0.45,
        0.80, 2.00,
    ),
    "Industrials": FinancialProfile(
        300_000_000, 18_000_000_000,
        0.03, 0.09,
        0.68, 0.87,
        0.18, 0.30,
        0.20, 0.55,
        1.50, 3.50,
    ),
    "Telecommunications": FinancialProfile(
        500_000_000, 20_000_000_000,
        0.02, 0.08,
        0.65, 0.85,
        0.18, 0.30,
        0.30, 0.65,
        1.50, 4.00,
    ),
    "Utilities": FinancialProfile(
        400_000_000, 15_000_000_000,
        0.02, 0.07,
        0.65, 0.88,
        0.20, 0.30,
        0.35, 0.70,
        2.00, 5.00,
    ),
    "Real Estate": FinancialProfile(
        200_000_000, 10_000_000_000,
        0.02, 0.09,
        0.35, 0.65,
        0.18, 0.30,
        0.40, 0.75,
        3.00, 8.00,
    ),
    "Materials": FinancialProfile(
        300_000_000, 15_000_000_000,
        0.02, 0.09,
        0.65, 0.86,
        0.20, 0.32,
        0.25, 0.60,
        1.50, 3.50,
    ),
    "Automotive": FinancialProfile(
        1_000_000_000, 30_000_000_000,
        0.03, 0.10,
        0.80, 0.94,
        0.18, 0.30,
        0.25, 0.65,
        2.00, 4.50,
    ),
    "Pharmaceuticals": FinancialProfile(
        500_000_000, 20_000_000_000,
        0.05, 0.15,
        0.45, 0.70,
        0.15, 0.28,
        0.10, 0.40,
        0.80, 2.00,
    ),
    "Semiconductors": FinancialProfile(
        300_000_000, 25_000_000_000,
        0.08, 0.25,
        0.50, 0.75,
        0.15, 0.27,
        0.10, 0.40,
        1.00, 3.00,
    ),
    "Media": FinancialProfile(
        150_000_000, 8_000_000_000,
        0.03, 0.12,
        0.55, 0.80,
        0.17, 0.29,
        0.10, 0.40,
        0.60, 1.50,
    ),
    "Transportation": FinancialProfile(
        500_000_000, 20_000_000_000,
        0.03, 0.10,
        0.65, 0.88,
        0.18, 0.30,
        0.30, 0.65,
        2.00, 5.00,
    ),
    "Insurance": FinancialProfile(
        500_000_000, 25_000_000_000,
        0.04, 0.11,
        0.40, 0.70,
        0.18, 0.30,
        0.35, 0.70,
        4.00, 10.00,
    ),
    "Retail": FinancialProfile(
        500_000_000, 25_000_000_000,
        0.03, 0.10,
        0.75, 0.94,
        0.18, 0.30,
        0.20, 0.55,
        1.00, 2.50,
    ),
    "Aerospace": FinancialProfile(
        300_000_000, 20_000_000_000,
        0.04, 0.12,
        0.65, 0.85,
        0.18, 0.30,
        0.15, 0.45,
        1.50, 4.00,
    ),
    "Chemicals": FinancialProfile(
        300_000_000, 18_000_000_000,
        0.03, 0.10,
        0.65, 0.87,
        0.18, 0.30,
        0.20, 0.55,
        1.50, 3.50,
    ),
    "Renewable Energy": FinancialProfile(
        200_000_000, 15_000_000_000,
        0.08, 0.20,
        0.60, 0.85,
        0.18, 0.30,
        0.30, 0.70,
        2.00, 5.00,
    ),
}


def get_financial_profile(industry_name: str) -> FinancialProfile:
    """Return the financial profile for an industry."""
    return FINANCIAL_PROFILES.get(industry_name, DEFAULT_PROFILE)
