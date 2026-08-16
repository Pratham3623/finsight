from dataclasses import dataclass
from datetime import date
import random

from finsight.data_generation.financial_profiles import get_financial_profile
from finsight.data_generation.reference_data import Company


@dataclass(frozen=True)
class FinancialRecord:
    financial_id: int
    company_id: int
    fiscal_year: int
    fiscal_quarter: int
    period_end_date: date
    revenue: float
    operating_expenses: float
    net_income: float
    total_assets: float
    total_liabilities: float
    total_debt: float
    operating_cash_flow: float
    investing_cash_flow: float
    financing_cash_flow: float


def _quarter_end_date(year: int, quarter: int) -> date:
    month = quarter * 3
    day = 31 if month in (3, 12) else 30

    return date(year, month, day)


def generate_financials(
    companies: list[Company],
    start_year: int = 2021,
    periods: int = 20,
    seed: int = 42,
) -> list[FinancialRecord]:
    """Generate deterministic quarterly financial records."""
    if not companies:
        raise ValueError("At least one company is required.")

    if periods <= 0:
        raise ValueError("Number of periods must be greater than zero.")

    rng = random.Random(seed)

    records: list[FinancialRecord] = []
    financial_id = 1

    for company in companies:
        profile = get_financial_profile(company.industry_name)


        annual_growth = rng.uniform(
            profile.annual_growth_min,
            profile.annual_growth_max,
        )

        base_annual_revenue = rng.uniform(
            profile.revenue_min,
            profile.revenue_max,
        )

        asset_intensity = rng.uniform(
            profile.asset_intensity_min,
            profile.asset_intensity_max,
        )

        debt_ratio = rng.uniform(
            profile.debt_ratio_min,
            profile.debt_ratio_max,
        )

        for period_index in range(periods):
            year = start_year + period_index // 4
            quarter = (period_index % 4) + 1

            years_elapsed = period_index / 4

            growth_factor = (1 + annual_growth) ** years_elapsed

            seasonal_factor = _seasonal_factor(quarter)

            revenue = (
                base_annual_revenue
                * growth_factor
                * seasonal_factor
            )

            revenue *= rng.uniform(0.97, 1.03)

            expense_ratio = rng.uniform(
                profile.operating_expense_ratio_min,
                profile.operating_expense_ratio_max,
            )

            operating_expenses = revenue * expense_ratio

            operating_profit = revenue - operating_expenses

            interest_expense = revenue * rng.uniform(0.01, 0.04)

            pre_tax_income = operating_profit - interest_expense

            tax_rate = rng.uniform(
                profile.tax_rate_min,
                profile.tax_rate_max,
            )

            taxes = max(pre_tax_income, 0) * tax_rate

            net_income = pre_tax_income - taxes

            total_assets = revenue * asset_intensity

            total_debt = total_assets * debt_ratio

            total_liabilities = total_debt + (
                total_assets * rng.uniform(0.10, 0.30)
            )

            operating_cash_flow = net_income * rng.uniform(0.85, 1.20)

            investing_cash_flow = -(
                total_assets * rng.uniform(0.01, 0.05)
            )

            financing_cash_flow = rng.uniform(
                -total_debt * 0.05,
                total_debt * 0.05,
            )

            records.append(
                FinancialRecord(
                    financial_id=financial_id,
                    company_id=company.company_id,
                    fiscal_year=year,
                    fiscal_quarter=quarter,
                    period_end_date=_quarter_end_date(year, quarter),
                    revenue=round(revenue, 2),
                    operating_expenses=round(operating_expenses, 2),
                    net_income=round(net_income, 2),
                    total_assets=round(total_assets, 2),
                    total_liabilities=round(total_liabilities, 2),
                    total_debt=round(total_debt, 2),
                    operating_cash_flow=round(operating_cash_flow, 2),
                    investing_cash_flow=round(investing_cash_flow, 2),
                    financing_cash_flow=round(financing_cash_flow, 2),
                )
            )

            financial_id += 1

    return records


def _seasonal_factor(quarter: int) -> float:
    factors = {
        1: 0.96,
        2: 0.99,
        3: 1.01,
        4: 1.04,
    }

    return factors[quarter]




   
