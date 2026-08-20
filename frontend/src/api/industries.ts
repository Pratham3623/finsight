import { apiGet } from "./client";

export interface IndustryBenchmark {
  industry_id: number;
  industry_name: string;
  avg_revenue: number | null;
  avg_net_profit_margin_pct: number | null;
  avg_operating_margin_pct: number | null;
  avg_debt_to_assets_pct: number | null;
  avg_roa_pct: number | null;
  avg_operating_cash_flow_margin_pct: number | null;
  company_count: number;
}

export async function getIndustryBenchmarks(): Promise<
  IndustryBenchmark[]
> {
  return apiGet<IndustryBenchmark[]>(
    "/api/industries/benchmarks",
  );
}
