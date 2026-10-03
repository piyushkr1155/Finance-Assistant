from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from services.session_store import session_store
from services.analytics_engine import (
    calculate_summary,
    calculate_monthly_trends,
    calculate_category_breakdown,
    get_largest_transactions,
    detect_unusual_transactions,
)
from models.analytics import (
    SummaryKPIs,
    MonthlyMetric,
    CategoryBreakdown,
    LargestTransaction,
    AnomalyReport,
)

router = APIRouter(tags=["Financial Analytics"])


def _get_session_txns(session_id: str):
    txns = session_store.get_transactions(session_id)
    if txns is None:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found. Please upload a transaction file first.",
        )
    return txns


@router.get("/api/analytics/summary", response_model=SummaryKPIs)
@router.get("/analytics/summary", response_model=SummaryKPIs)
def get_summary(session_id: str = Query(..., description="Active session ID")):
    """Get high-level deterministic financial summary (Total Income, Expenses, Net, Averages)."""
    txns = _get_session_txns(session_id)
    return calculate_summary(txns)


@router.get("/api/analytics/monthly", response_model=List[MonthlyMetric])
@router.get("/analytics/monthly", response_model=List[MonthlyMetric])
def get_monthly_trends(session_id: str = Query(..., description="Active session ID")):
    """Get month-by-month income, expense, net cash flow, and MoM growth rates."""
    txns = _get_session_txns(session_id)
    return calculate_monthly_trends(txns)


@router.get("/api/analytics/categories", response_model=List[CategoryBreakdown])
@router.get("/analytics/categories", response_model=List[CategoryBreakdown])
def get_categories(
    session_id: str = Query(..., description="Active session ID"),
    type: str = Query("expense", description="'expense' or 'income'"),
):
    """Get breakdown of expenses or income by category with percentages and transaction counts."""
    txns = _get_session_txns(session_id)
    return calculate_category_breakdown(txns, txn_type=type)


@router.get("/api/analytics/largest", response_model=List[LargestTransaction])
@router.get("/api/analytics/largest-expenses", response_model=List[LargestTransaction])
@router.get("/analytics/largest", response_model=List[LargestTransaction])
def get_largest(
    session_id: str = Query(..., description="Active session ID"),
    type: Optional[str] = Query(None, description="'expense' or 'income' or omit for all"),
    limit: int = Query(10, ge=1, le=50),
):
    """Get the largest transactions by monetary value."""
    txns = _get_session_txns(session_id)
    return get_largest_transactions(txns, txn_type=type, limit=limit)


@router.get("/api/analytics/anomalies", response_model=AnomalyReport)
@router.get("/analytics/anomalies", response_model=AnomalyReport)
def get_anomalies(session_id: str = Query(..., description="Active session ID")):
    """Get detected statistical outliers and unusual transactions with clear explanations."""
    txns = _get_session_txns(session_id)
    return detect_unusual_transactions(txns)
