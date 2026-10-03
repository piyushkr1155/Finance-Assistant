from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class SummaryKPIs(BaseModel):
    total_income: float
    total_expenses: float
    net_cash_flow: float
    savings_rate_pct: float
    transaction_count: int
    income_transaction_count: int
    expense_transaction_count: int
    avg_transaction_amount: float
    avg_income: float
    avg_expense: float
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    top_expense_category: Optional[str] = None
    top_income_category: Optional[str] = None


class MonthlyMetric(BaseModel):
    month: str  # "YYYY-MM"
    income: float
    expenses: float
    net: float
    transaction_count: int
    income_growth_pct: Optional[float] = None
    expense_growth_pct: Optional[float] = None


class CategoryBreakdown(BaseModel):
    category: str
    amount: float
    percentage: float
    transaction_count: int
    avg_per_transaction: float


class LargestTransaction(BaseModel):
    id: str
    date: str
    description: str
    amount: float
    type: str
    category: str


class UnusualTransaction(BaseModel):
    id: str
    date: str
    description: str
    amount: float
    type: str
    category: str
    reason: str
    z_score: Optional[float] = None
    ratio_to_category_avg: Optional[float] = None
    severity: str  # "high" or "medium"


class AnomalyReport(BaseModel):
    total_anomalies: int
    anomalies: List[UnusualTransaction]
    summary: str
