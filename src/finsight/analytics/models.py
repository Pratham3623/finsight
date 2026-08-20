from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CompanyMetric:
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


@dataclass(frozen=True)
class IndustryBenchmark:
    industry_id: int
    industry_name: str
    avg_revenue: float
    avg_net_profit_margin_pct: float
    avg_operating_margin_pct: float
    avg_debt_to_assets_pct: float
    avg_roa_pct: float
    avg_operating_cash_flow_margin_pct: float
    company_count: int


@dataclass(frozen=True)
class CompanyRanking:
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

