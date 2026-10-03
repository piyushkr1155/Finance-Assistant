import {
  UploadResult,
  SummaryKPIs,
  MonthlyMetric,
  CategoryBreakdown,
  LargestTransaction,
  AnomalyReport,
  Transaction,
  SystemHealth,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

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
        API_BASE,
      0
    );
  }
}

export async function checkHealth(): Promise<SystemHealth> {
  return fetchJson<SystemHealth>(`${API_BASE}/api/health`);
}

export async function uploadFinancialFile(file: File): Promise<UploadResult> {
  const formData = new FormData();
  formData.append("file", file);

  return fetchJson<UploadResult>(`${API_BASE}/api/upload`, {
    method: "POST",
    body: formData,
  });
}

export async function fetchSummary(sessionId: string): Promise<SummaryKPIs> {
  return fetchJson<SummaryKPIs>(
    `${API_BASE}/api/analytics/summary?session_id=${encodeURIComponent(sessionId)}`
  );
}

export async function fetchMonthlyTrends(
  sessionId: string
): Promise<MonthlyMetric[]> {
  return fetchJson<MonthlyMetric[]>(
    `${API_BASE}/api/analytics/monthly?session_id=${encodeURIComponent(sessionId)}`
  );
}

export async function fetchCategoryBreakdown(
  sessionId: string,
  type: string = "expense"
): Promise<CategoryBreakdown[]> {
  return fetchJson<CategoryBreakdown[]>(
    `${API_BASE}/api/analytics/categories?session_id=${encodeURIComponent(
      sessionId
    )}&type=${encodeURIComponent(type)}`
  );
}

export async function fetchLargestTransactions(
  sessionId: string,
  limit: number = 8
): Promise<LargestTransaction[]> {
  return fetchJson<LargestTransaction[]>(
    `${API_BASE}/api/analytics/largest?session_id=${encodeURIComponent(
      sessionId
    )}&limit=${limit}`
  );
}

export async function fetchAnomalies(sessionId: string): Promise<AnomalyReport> {
  return fetchJson<AnomalyReport>(
    `${API_BASE}/api/analytics/anomalies?session_id=${encodeURIComponent(sessionId)}`
  );
}

export async function fetchTransactions(
  sessionId: string,
  limit: number = 50,
  offset: number = 0,
  search?: string
): Promise<{ total_count: number; transactions: Transaction[] }> {
  let url = `${API_BASE}/api/transactions?session_id=${encodeURIComponent(
    sessionId
  )}&limit=${limit}&offset=${offset}`;
  if (search) {
    url += `&search=${encodeURIComponent(search)}`;
  }
  return fetchJson<{ total_count: number; transactions: Transaction[] }>(url);
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
