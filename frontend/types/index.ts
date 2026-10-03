export type TransactionType = "income" | "expense";

export interface Transaction {
  id: string;
  date: string;
  description: string;
  amount: number;
  type: TransactionType;
  category: string;
  raw_amount?: string;
}

export interface SummaryKPIs {
  total_income: number;
  total_expenses: number;
  net_cash_flow: number;
  savings_rate_pct: number;
  transaction_count: number;
  income_transaction_count: number;
  expense_transaction_count: number;
  avg_transaction_amount: number;
  avg_income: number;
  avg_expense: number;
  start_date: string | null;
  end_date: string | null;
  top_expense_category: string | null;
  top_income_category: string | null;
}

export interface MonthlyMetric {
  month: string;
  income: number;
  expenses: number;
  net: number;
  transaction_count: number;
  income_growth_pct: number | null;
  expense_growth_pct: number | null;
}

export interface CategoryBreakdown {
  category: string;
  amount: number;
  percentage: number;
  transaction_count: number;
  avg_per_transaction: number;
}

export interface LargestTransaction {
  id: string;
  date: string;
  description: string;
  amount: number;
  type: string;
  category: string;
}

export interface UnusualTransaction {
  id: string;
  date: string;
  description: string;
  amount: number;
  type: string;
  category: string;
  reason: string;
  z_score?: number | null;
  ratio_to_category_avg?: number | null;
  severity: "high" | "medium";
}

export interface AnomalyReport {
  total_anomalies: number;
  anomalies: UnusualTransaction[];
  summary: string;
}

export interface InvalidRowDetail {
  row_index: number;
  reason: string;
  data: Record<string, any>;
}

export interface UploadResult {
  session_id: string;
  filename: string;
  file_type: string;
  total_rows_read: number;
  valid_transactions_count: number;
  invalid_rows_count: number;
  columns_detected: string[];
  column_mapping_used: Record<string, string | null>;
  is_auto_mapped: boolean;
  missing_required_fields: string[];
  invalid_rows_sample: InvalidRowDetail[];
  sample_transactions: Transaction[];
  warnings: string[];
}

export interface SystemHealth {
  status: string;
  service: string;
  ollama_base_url: string;
  ollama_available?: boolean;
  active_model?: string;
  available_models?: string[];
}

export interface AIGenerateResponse {
  success: boolean;
  model_used?: string | null;
  response: string;
  is_fallback: boolean;
  context_used?: any;
}

export interface AskBusinessResponse {
  query: string;
  intent: string;
  answer: string;
  key_data: string[];
  why_it_matters: string;
  what_to_check: string[];
  evidence?: Record<string, any>;
}

export interface ExplainAnomalyResponse {
  anomaly_id: string;
  description: string;
  amount: number;
  category: string;
  statistical_reason: string;
  ai_explanation: string;
  recommended_action: string;
  model_used: string;
  is_fallback: boolean;
}
