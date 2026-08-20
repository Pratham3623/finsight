import { apiRequest } from "./client";

import type { HealthResponse } from "../types/api";

export async function getHealth(): Promise<HealthResponse> {
  return apiRequest<HealthResponse>("/health");
}

export async function getReadiness(): Promise<HealthResponse> {
  return apiRequest<HealthResponse>("/ready");
}
