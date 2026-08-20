import { apiRequest } from "./client";

import type {
  AIAnalysisRequest,
  AIAnalysisResponse,
  AIComparisonRequest,
  AIComparisonResponse,
  AIPortfolioAnalysisRequest,
  AIPortfolioAnalysisResponse,
} from "../types/api";

export async function analyzeCompany(
  request: AIAnalysisRequest,
): Promise<AIAnalysisResponse> {
  return apiRequest<AIAnalysisResponse>(
    "/api/ai/analyze",
    {
      method: "POST",
      body: JSON.stringify(request),
    },
  );
}

export async function analyzePortfolio(
  request: AIPortfolioAnalysisRequest,
): Promise<AIPortfolioAnalysisResponse> {
  return apiRequest<AIPortfolioAnalysisResponse>(
    "/api/ai/portfolio",
    {
      method: "POST",
      body: JSON.stringify(request),
    },
  );
}

export async function compareCompanies(
  request: AIComparisonRequest,
): Promise<AIComparisonResponse> {
  return apiRequest<AIComparisonResponse>(
    "/api/ai/compare",
    {
      method: "POST",
      body: JSON.stringify(request),
    },
  );
}
