export interface HealthResponse {
  status: string;
}

export interface CompanyMetric {
  financial_id: number;
  company_id: number;
  company_name: string;
  ticker: string;
  industry_name: string;
  fiscal_year: number;
  fiscal_quarter: number;
  period_end_date: string;
  revenue: number;
  net_income: number;
  net_profit_margin_pct: number;
  operating_margin_pct: number;
  debt_to_assets_pct: number;
  debt_to_equity_pct: number;
  roa_pct: number;
  operating_cash_flow_margin_pct: number;
}

export interface CompanyRanking {
  company_id: number;
  company_name: string;
  ticker: string;
  industry_name: string;
  avg_revenue: number;
  avg_net_profit_margin_pct: number;
  avg_roa_pct: number;
  avg_revenue_growth_yoy_pct: number;
  roa_rank: number;
  revenue_rank: number;
}

export interface IndustryBenchmark {
  industry_id: number;
  industry_name: string;
  avg_revenue: number;
  avg_net_profit_margin_pct: number;
  avg_operating_margin_pct: number;
  avg_debt_to_assets_pct: number;
  avg_roa_pct: number;
  avg_operating_cash_flow_margin_pct: number;
  company_count: number;
}

export interface CompanySummary {
  company_id: number;
  company_name: string;
  ticker: string;
  industry: string;
  latest_period: string;
  latest_revenue: number;
  latest_net_income: number;
  latest_net_profit_margin_pct: number;
  latest_roa_pct: number;
  latest_debt_to_assets_pct: number;
  periods_available: number;
}

export interface AIAnalysisRequest {
  question: string;
  company_id: number;
}

export interface AIAnalysisResponse {
  company_id: number;
  question: string;
  answer: string;
}

export interface AIPortfolioAnalysisRequest {
  question: string;
  limit?: number;
}

export interface AIPortfolioAnalysisResponse {
  question: string;
  answer: string;
}

export interface AIComparisonRequest {
  question: string;
  company_ids: number[];
}

export interface AIComparisonResponse {
  company_ids: number[];
  question: string;
  answer: string;
}
