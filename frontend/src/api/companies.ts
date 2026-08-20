import { apiGet } from "./client";

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

export interface CompanyMetric {
  company_id: number;
  period_end_date: string;
  revenue: number;
  operating_expenses: number;
  net_income: number;
  total_assets: number;
  total_liabilities: number;
  total_debt: number;
  operating_cash_flow: number;
  investing_cash_flow: number;
  financing_cash_flow: number;
  net_profit_margin_pct: number;
  operating_margin_pct: number;
  debt_to_assets_pct: number;
  debt_to_equity_pct: number;
  roa_pct: number;
  operating_cash_flow_margin_pct: number;
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

export async function getCompanyRankings(
  limit = 20,
): Promise<CompanyRanking[]> {
  const data = await apiGet<CompanyRanking[]>(
    `/api/rankings?limit=${limit}`,
  );

  return data.slice(0, limit);
}

export async function getCompanyMetrics(
  companyId: number,
): Promise<CompanyMetric[]> {
  return apiGet<CompanyMetric[]>(
    `/api/companies/${companyId}/metrics`,
  );
}

export async function getCompanySummary(
  companyId: number,
): Promise<CompanySummary> {
  return apiGet<CompanySummary>(
    `/api/companies/${companyId}/summary`,
  );
}
