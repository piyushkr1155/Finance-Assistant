import {
  UploadResult,
  SummaryKPIs,
  MonthlyMetric,
  CategoryBreakdown,
  LargestTransaction,
  AnomalyReport,
  Transaction,
  SystemHealth,
  AIGenerateResponse,
  AskBusinessResponse,
  ExplainAnomalyResponse,
} from "@/types";
import { API_URL, API_BASE } from "./config";

export { API_URL, API_BASE };

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  try {
    const res = await fetch(url, options);
    if (!res.ok) {
      let errorMsg = `Server error (${res.status})`;
      try {
        const errData = await res.json();
        errorMsg = errData.detail || errData.error || errorMsg;
      } catch {
        // non-json response
      }
      throw new ApiError(errorMsg, res.status);
    }
    return await res.json();
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(
      "Unable to connect to LocalLedger backend. Please ensure the backend is running at " +
        API_URL,
      0
    );
  }
}

export async function checkHealth(): Promise<SystemHealth> {
  return fetchJson<SystemHealth>(`${API_URL}/api/health`);
}

export async function uploadFinancialFile(file: File): Promise<UploadResult> {
  const formData = new FormData();
  formData.append("file", file);

  return fetchJson<UploadResult>(`${API_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });
}

export async function fetchSummary(sessionId: string): Promise<SummaryKPIs> {
  return fetchJson<SummaryKPIs>(
    `${API_URL}/api/analytics/summary?session_id=${encodeURIComponent(sessionId)}`
  );
}

export async function fetchMonthlyTrends(
  sessionId: string
): Promise<MonthlyMetric[]> {
  return fetchJson<MonthlyMetric[]>(
    `${API_URL}/api/analytics/monthly?session_id=${encodeURIComponent(sessionId)}`
  );
}

export async function fetchCategoryBreakdown(
  sessionId: string,
  type: string = "expense"
): Promise<CategoryBreakdown[]> {
  return fetchJson<CategoryBreakdown[]>(
    `${API_URL}/api/analytics/categories?session_id=${encodeURIComponent(
      sessionId
    )}&type=${encodeURIComponent(type)}`
  );
}

export async function fetchLargestTransactions(
  sessionId: string,
  limit: number = 8,
  type?: string
): Promise<LargestTransaction[]> {
  let url = `${API_URL}/api/analytics/largest?session_id=${encodeURIComponent(
    sessionId
  )}&limit=${limit}`;
  if (type) {
    url += `&type=${encodeURIComponent(type)}`;
  }
  return fetchJson<LargestTransaction[]>(url);
}

export async function fetchAnomalies(sessionId: string): Promise<AnomalyReport> {
  return fetchJson<AnomalyReport>(
    `${API_URL}/api/analytics/anomalies?session_id=${encodeURIComponent(sessionId)}`
  );
}

export async function fetchTransactions(
  sessionId: string,
  limit: number = 50,
  offset: number = 0,
  search?: string
): Promise<{ total_count: number; transactions: Transaction[] }> {
  let url = `${API_URL}/api/transactions?session_id=${encodeURIComponent(
    sessionId
  )}&limit=${limit}&offset=${offset}`;
  if (search) {
    url += `&search=${encodeURIComponent(search)}`;
  }
  return fetchJson<{ total_count: number; transactions: Transaction[] }>(url);
}

export async function generateAIInsights(
  sessionId: string,
  model?: string
): Promise<AIGenerateResponse> {
  return fetchJson<AIGenerateResponse>(`${API_URL}/api/ai/insights`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, model }),
  });
}

export async function askBusiness(
  sessionId: string,
  query: string
): Promise<AskBusinessResponse> {
  return fetchJson<AskBusinessResponse>(`${API_URL}/api/ai/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, query }),
  });
}

export async function explainAnomaly(
  sessionId: string,
  anomalyId: string
): Promise<ExplainAnomalyResponse> {
  return fetchJson<ExplainAnomalyResponse>(`${API_URL}/api/ai/explain-anomaly`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, anomaly_id: anomalyId }),
  });
}

export async function purgeSession(sessionId: string): Promise<{ status: string; session_id: string }> {
  return fetchJson<{ status: string; session_id: string }>(
    `${API_URL}/api/session?session_id=${encodeURIComponent(sessionId)}`,
    {
      method: "DELETE",
    }
  );
}

export function formatCurrency(
  val: number | null | undefined,
  currency: string = "₹"
): string {
  if (val === null || val === undefined || isNaN(val)) return `${currency}0.00`;
  const formatted = Math.abs(val).toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  return val < 0 ? `-${currency}${formatted}` : `${currency}${formatted}`;
}

export function formatPercentage(val: number | null | undefined): string {
  if (val === null || val === undefined || isNaN(val)) return "0.0%";
  const sign = val > 0 ? "+" : "";
  return `${sign}${val.toFixed(1)}%`;
}
