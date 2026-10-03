import json
from typing import Dict, Any, List, Optional
from services.session_store import session_store
from services.analytics_engine import (
    calculate_summary,
    calculate_monthly_trends,
    calculate_category_breakdown,
    detect_unusual_transactions,
)
from models.transaction import NormalizedTransaction


def build_financial_context(
    session_id: str,
    focus_topic: Optional[str] = None
) -> Dict[str, Any]:
    """
    Constructs a deterministic, compact JSON context of verified financial numbers.
    Never passes raw unorganized files to the LLM.
    """
    transactions = session_store.get_transactions(session_id)
    if not transactions:
        return {}

    summary = calculate_summary(transactions)
    monthly = calculate_monthly_trends(transactions)
    expense_categories = calculate_category_breakdown(transactions, txn_type="expense")
    income_categories = calculate_category_breakdown(transactions, txn_type="income")
    anomalies_report = detect_unusual_transactions(transactions)

    # Latest month & previous month comparison
    latest_month = monthly[-1] if monthly else None
    prev_month = monthly[-2] if len(monthly) >= 2 else None

    # Top expense categories (top 5)
    top_expenses = [
        {
            "category": c.category,
            "amount": c.amount,
            "percentage": c.percentage,
            "transaction_count": c.transaction_count,
        }
        for c in expense_categories[:5]
    ]

    # Top income categories
    top_incomes = [
        {
            "category": c.category,
            "amount": c.amount,
            "percentage": c.percentage,
        }
        for c in income_categories[:3]
    ]

    # Unusual items
    flagged_anomalies = [
        {
            "date": a.date,
            "description": a.description,
            "amount": a.amount,
            "category": a.category,
            "reason": a.reason,
            "severity": a.severity,
        }
        for a in anomalies_report.anomalies[:5]
    ]

    context: Dict[str, Any] = {
        "period": f"{summary.start_date} to {summary.end_date}",
        "kpis": {
            "total_income": summary.total_income,
            "total_expenses": summary.total_expenses,
            "net_cash_flow": summary.net_cash_flow,
            "savings_rate_pct": summary.savings_rate_pct,
            "total_transactions": summary.transaction_count,
            "avg_transaction_amount": summary.avg_transaction_amount,
        },
        "monthly_summary": [
            {
                "month": m.month,
                "income": m.income,
                "expenses": m.expenses,
                "net": m.net,
                "expense_growth_pct": m.expense_growth_pct,
                "income_growth_pct": m.income_growth_pct,
            }
            for m in monthly
        ],
        "latest_month_performance": {
            "month": latest_month.month if latest_month else None,
            "income": latest_month.income if latest_month else None,
            "expenses": latest_month.expenses if latest_month else None,
            "net": latest_month.net if latest_month else None,
            "expense_growth_mom_pct": latest_month.expense_growth_pct if latest_month else None,
            "income_growth_mom_pct": latest_month.income_growth_pct if latest_month else None,
        } if latest_month else None,
        "previous_month_baseline": {
            "month": prev_month.month if prev_month else None,
            "income": prev_month.income if prev_month else None,
            "expenses": prev_month.expenses if prev_month else None,
            "net": prev_month.net if prev_month else None,
        } if prev_month else None,
        "top_expense_categories": top_expenses,
        "top_income_categories": top_incomes,
        "unusual_transactions": flagged_anomalies,
    }

    if focus_topic:
        context["focus_topic"] = focus_topic

    return context


def context_to_numbers_set(context: Dict[str, Any]) -> set[float]:
    """
    Extracts all numerical values present in the context for hallucination validation.
    """
    numbers = set()

    def _extract(obj):
        if isinstance(obj, (int, float)) and not isinstance(obj, bool):
            numbers.add(round(float(obj), 2))
            numbers.add(round(float(obj), 0))
        elif isinstance(obj, dict):
            for v in obj.values():
                _extract(v)
        elif isinstance(obj, list):
            for item in obj:
                _extract(item)

    _extract(context)
    return numbers
