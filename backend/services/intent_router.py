import re
from enum import Enum
from typing import Dict, Any, List, Tuple

from services.session_store import session_store
from services.analytics_engine import (
    calculate_summary,
    calculate_monthly_trends,
    calculate_category_breakdown,
    detect_unusual_transactions,
)


class BusinessQueryIntent(str, Enum):
    EXPENSE_INCREASE = "EXPENSE_INCREASE"
    CATEGORY_BREAKDOWN = "CATEGORY_BREAKDOWN"
    UNUSUAL_TRANSACTIONS = "UNUSUAL_TRANSACTIONS"
    CASH_FLOW_PROFIT = "CASH_FLOW_PROFIT"
    GENERAL = "GENERAL"


def detect_intent(query: str) -> BusinessQueryIntent:
    """
    Classifies the user's natural language business query into a focused analytical intent.
    """
    q = query.lower()

    # Intent 1: Expense Increase / Month-over-Month change
    if any(k in q for k in [
        "increase", "higher", "rise", "rose", "grew", "growth",
        "more expensive", "spend more", "compared with", "compared to", "last month", "this month"
    ]):
        return BusinessQueryIntent.EXPENSE_INCREASE

    # Intent 2: Unusual Transactions / Anomalies
    if any(k in q for k in [
        "unusual", "anomaly", "anomalies", "suspicious", "weird", "strange",
        "outlier", "outliers", "spike", "investigate", "unexpected"
    ]):
        return BusinessQueryIntent.UNUSUAL_TRANSACTIONS

    # Intent 3: Categories / Breakdown
    if any(k in q for k in [
        "categor", "breakdown", "biggest", "top expense", "top spend",
        "where did", "where does", "where am i", "most money", "major spend",
        "spend the most", "spending the most", "spent the most", "highest spend"
    ]) or ("spend" in q and "most" in q):
        return BusinessQueryIntent.CATEGORY_BREAKDOWN

    # Intent 4: Cash Flow / Profitability
    if any(k in q for k in [
        "cash flow", "profit", "profitable", "net", "margin", "surplus",
        "deficit", "runway", "saving", "health"
    ]):
        return BusinessQueryIntent.CASH_FLOW_PROFIT

    return BusinessQueryIntent.GENERAL


def generate_structured_business_answer(
    session_id: str,
    query: str
) -> Dict[str, Any]:
    """
    Executes intent detection, retrieves relevant analytics, and generates
    the 4-part structured business response with 100% grounded numbers.
    """
    transactions = session_store.get_transactions(session_id)
    if not transactions:
        return {
            "query": query,
            "intent": BusinessQueryIntent.GENERAL.value,
            "answer": "No transactions are currently loaded for this session.",
            "key_data": [],
            "why_it_matters": "Financial analytics require an active uploaded ledger.",
            "what_to_check": ["Please upload a CSV or Excel file to begin."],
            "evidence": {},
        }

    intent = detect_intent(query)
    summary = calculate_summary(transactions)
    monthly = calculate_monthly_trends(transactions)
    categories = calculate_category_breakdown(transactions, txn_type="expense")
    anomalies = detect_unusual_transactions(transactions)

    latest_month = monthly[-1] if monthly else None
    prev_month = monthly[-2] if len(monthly) >= 2 else None

    if intent == BusinessQueryIntent.EXPENSE_INCREASE:
        if latest_month and prev_month:
            diff = latest_month.expenses - prev_month.expenses
            growth_pct = latest_month.expense_growth_pct or 0.0
            direction = "increased" if diff >= 0 else "decreased"
            top_cat = categories[0].category if categories else "General Expenditures"

            answer = (
                f"Expenses {direction} compared with the previous month. "
                f"Total disbursements for {latest_month.month} were ₹{latest_month.expenses:,.2f} "
                f"compared to ₹{prev_month.expenses:,.2f} in {prev_month.month}."
            )
            key_data = [
                f"{latest_month.month} expenses: ₹{latest_month.expenses:,.2f}",
                f"{prev_month.month} expenses: ₹{prev_month.expenses:,.2f}",
                f"Net Change: {'+' if diff > 0 else ''}₹{diff:,.2f} ({growth_pct:+.1f}%)",
                f"Primary expense driver: {top_cat}",
            ]
            why_it_matters = (
                "A surge in month-over-month expenses directly reduces your operating cash reserves "
                "unless counterbalanced by proportional revenue growth."
            )
            what_to_check = [
                f"Review the largest transactions under '{top_cat}' during {latest_month.month}",
                "Inspect any one-time hardware, equipment, or annual subscription renewals",
            ]
        else:
            answer = f"Total recorded expenses stand at ₹{summary.total_expenses:,.2f} across the uploaded period."
            key_data = [
                f"Total Expenses: ₹{summary.total_expenses:,.2f}",
                f"Number of expense items: {summary.expense_transaction_count}",
                f"Top Category: {summary.top_expense_category or 'N/A'}",
            ]
            why_it_matters = "Historical multi-month tracking enables accurate trend baselining."
            what_to_check = ["Upload a multi-month ledger to see month-over-month growth calculations."]

    elif intent == BusinessQueryIntent.UNUSUAL_TRANSACTIONS:
        if anomalies.total_anomalies > 0:
            top_anom = anomalies.anomalies[0]
            answer = (
                f"Found {anomalies.total_anomalies} unusual transaction(s) requiring review. "
                f"The most significant item is a payment for '{top_anom.description}' of ₹{top_anom.amount:,.2f}."
            )
            key_data = [
                f"{top_anom.date}: {top_anom.description} — ₹{top_anom.amount:,.2f} ({top_anom.category})",
                f"Statistical Reason: {top_anom.reason}",
                f"Total Flagged Items: {anomalies.total_anomalies}",
            ]
            why_it_matters = (
                "Statistical outliers often represent unexpected duplicate billings, equipment purchases, "
                "or misclassified entries that distort monthly budgeting."
            )
            what_to_check = [
                f"Confirm the invoice for '{top_anom.description}' on {top_anom.date}",
                "Ensure capital expenditures are separated from recurring operational costs",
            ]
        else:
            answer = "No unusual transactions or statistical outliers were detected in this dataset."
            key_data = [
                f"Total transactions analyzed: {summary.transaction_count}",
                f"Average transaction: ₹{summary.avg_transaction_amount:,.2f}",
                "All items remain within 1.5x IQR and standard category multiples",
            ]
            why_it_matters = "Consistent spending indicates stable operating cadence without sudden cash leaks."
            what_to_check = ["Continue periodic monitoring as new bank statements are exported."]

    elif intent == BusinessQueryIntent.CATEGORY_BREAKDOWN:
        top_3 = categories[:3]
        cat_names = ", ".join([f"{c.category} ({c.percentage}%)" for c in top_3])
        answer = f"Your biggest spending areas are {cat_names}."
        key_data = [
            f"{c.category}: ₹{c.amount:,.2f} ({c.percentage}% of total expenses, {c.transaction_count} txns)"
            for c in top_3
        ]
        why_it_matters = (
            "Focusing cost-optimization efforts on the top 20% of spending categories yields "
            "the largest impact on operating profitability."
        )
        what_to_check = [
            f"Review recurring contracts and vendor rates in '{top_3[0].category if top_3 else 'top categories'}'",
            "Evaluate whether volume discounts or annual billing plans are available",
        ]

    elif intent == BusinessQueryIntent.CASH_FLOW_PROFIT:
        is_surplus = summary.net_cash_flow >= 0
        status_word = "positive cash flow surplus" if is_surplus else "net cash deficit"
        answer = (
            f"Your business generated a {status_word} of ₹{summary.net_cash_flow:,.2f} "
            f"over the period ({summary.start_date} to {summary.end_date})."
        )
        key_data = [
            f"Total Income: ₹{summary.total_income:,.2f}",
            f"Total Expenses: ₹{summary.total_expenses:,.2f}",
            f"Net Cash Flow: ₹{summary.net_cash_flow:,.2f}",
            f"Cash Margin: {summary.savings_rate_pct:.1f}%",
        ]
        why_it_matters = (
            "A positive cash margin provides working capital to reinvest and creates a buffer "
            "against seasonal sales slowdowns."
        )
        what_to_check = [
            "Maintain at least 2-3 months of average operating expenses in liquid reserve",
            "Monitor receivables aging to ensure customer payments arrive on schedule",
        ]

    else:  # General
        answer = (
            f"Over the active period ({summary.start_date} to {summary.end_date}), the business recorded "
            f"₹{summary.total_income:,.2f} in revenue and ₹{summary.total_expenses:,.2f} in expenses, "
            f"resulting in net cash flow of ₹{summary.net_cash_flow:,.2f}."
        )
        key_data = [
            f"Total Transactions: {summary.transaction_count}",
            f"Net Cash Flow: ₹{summary.net_cash_flow:,.2f}",
            f"Top Category: {summary.top_expense_category or 'N/A'}",
        ]
        why_it_matters = "Having clear visibility into your overall cash movement is essential for sound business planning."
        what_to_check = [
            "Check monthly cash flow trends to identify seasonal patterns",
            "Review flagged unusual transactions for unexpected costs",
        ]

    return {
        "query": query,
        "intent": intent.value,
        "answer": answer,
        "key_data": key_data,
        "why_it_matters": why_it_matters,
        "what_to_check": what_to_check,
        "evidence": {
            "total_income": summary.total_income,
            "total_expenses": summary.total_expenses,
            "net_cash_flow": summary.net_cash_flow,
            "transaction_count": summary.transaction_count,
        },
    }
