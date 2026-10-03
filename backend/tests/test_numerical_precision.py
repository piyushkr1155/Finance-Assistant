import time
from datetime import date, timedelta
import pytest

from models.transaction import NormalizedTransaction, TransactionType
from services.analytics_engine import (
    calculate_summary,
    calculate_monthly_trends,
    calculate_category_breakdown,
    get_largest_transactions,
    detect_unusual_transactions,
)
from services.anomaly_detector import (
    detect_unusual_transactions_comprehensive,
)


# 1. Manual Numerical Precision Test
def test_manual_numerical_precision():
    """
    Verify exact mathematical formulas against manually calculated known figures:
    - Total Income: 45000.50 + 12500.25 = 57500.75
    - Total Expenses: 1200.00 + 450.50 + 8500.25 = 10150.75
    - Net Cash Flow: 57500.75 - 10150.75 = 47350.00
    - Savings Rate: (47350.00 / 57500.75) * 100 = 82.35%
    """
    txns = [
        NormalizedTransaction(
            id="p1", date=date(2026, 6, 1), description="Consulting Retainer",
            amount=45000.50, type=TransactionType.INCOME, category="Consulting"
        ),
        NormalizedTransaction(
            id="p2", date=date(2026, 6, 15), description="Digital Product Sales",
            amount=12500.25, type=TransactionType.INCOME, category="Sales"
        ),
        NormalizedTransaction(
            id="p3", date=date(2026, 6, 2), description="Cloud Server",
            amount=1200.00, type=TransactionType.EXPENSE, category="Infrastructure"
        ),
        NormalizedTransaction(
            id="p4", date=date(2026, 6, 10), description="Domain Renewal",
            amount=450.50, type=TransactionType.EXPENSE, category="Infrastructure"
        ),
        NormalizedTransaction(
            id="p5", date=date(2026, 6, 20), description="Office Workstations",
            amount=8500.25, type=TransactionType.EXPENSE, category="Equipment"
        ),
    ]

    summary = calculate_summary(txns)

    assert summary.total_income == 57500.75
    assert summary.total_expenses == 10150.75
    assert summary.net_cash_flow == 47350.00
    assert summary.savings_rate_pct == 82.35
    assert summary.transaction_count == 5
    assert summary.income_transaction_count == 2
    assert summary.expense_transaction_count == 3


# 2. Month-over-Month Growth Mathematical Verification
def test_mom_growth_rate_precision():
    """
    Month 1 (May): Income = 10000, Expense = 4000
    Month 2 (June): Income = 15000, Expense = 6000
    Month 3 (July): Income = 12000, Expense = 3000
    - June Income Growth: (15000 - 10000) / 10000 * 100 = +50.0%
    - June Expense Growth: (6000 - 4000) / 4000 * 100 = +50.0%
    - July Income Growth: (12000 - 15000) / 15000 * 100 = -20.0%
    - July Expense Growth: (3000 - 6000) / 6000 * 100 = -50.0%
    """
    txns = [
        NormalizedTransaction(id="m1", date=date(2026, 5, 5), description="Inc May", amount=10000.0, type=TransactionType.INCOME, category="Sales"),
        NormalizedTransaction(id="m2", date=date(2026, 5, 10), description="Exp May", amount=4000.0, type=TransactionType.EXPENSE, category="Ops"),
        NormalizedTransaction(id="m3", date=date(2026, 6, 5), description="Inc Jun", amount=15000.0, type=TransactionType.INCOME, category="Sales"),
        NormalizedTransaction(id="m4", date=date(2026, 6, 10), description="Exp Jun", amount=6000.0, type=TransactionType.EXPENSE, category="Ops"),
        NormalizedTransaction(id="m5", date=date(2026, 7, 5), description="Inc Jul", amount=12000.0, type=TransactionType.INCOME, category="Sales"),
        NormalizedTransaction(id="m6", date=date(2026, 7, 10), description="Exp Jul", amount=3000.0, type=TransactionType.EXPENSE, category="Ops"),
    ]

    trends = calculate_monthly_trends(txns)
    assert len(trends) == 3

    may, jun, jul = trends[0], trends[1], trends[2]
    assert may.income_growth_pct is None
    assert may.expense_growth_pct is None

    assert jun.income_growth_pct == 50.0
    assert jun.expense_growth_pct == 50.0

    assert jul.income_growth_pct == -20.0
    assert jul.expense_growth_pct == -50.0


# 3. Category Breakdown Percentages Sum to Exactly 100%
def test_category_percentages_sum():
    txns = [
        NormalizedTransaction(id="c1", date=date(2026, 8, 1), description="Rent", amount=3333.33, type=TransactionType.EXPENSE, category="Rent"),
        NormalizedTransaction(id="c2", date=date(2026, 8, 2), description="Ads", amount=3333.33, type=TransactionType.EXPENSE, category="Marketing"),
        NormalizedTransaction(id="c3", date=date(2026, 8, 3), description="Payroll", amount=3333.34, type=TransactionType.EXPENSE, category="Payroll"),
    ]
    breakdown = calculate_category_breakdown(txns, txn_type="expense")
    total_pct = sum(item.percentage for item in breakdown)
    assert pytest.approx(total_pct, 0.05) == 100.0


# 4. Edge Case: Single Transaction Dataset
def test_single_transaction_edge_case():
    single_txn = [
        NormalizedTransaction(
            id="solo", date=date(2026, 8, 10), description="Solo Sale",
            amount=5000.0, type=TransactionType.INCOME, category="Sales"
        )
    ]
    summary = calculate_summary(single_txn)
    assert summary.total_income == 5000.0
    assert summary.total_expenses == 0.0
    assert summary.net_cash_flow == 5000.0
    assert summary.savings_rate_pct == 100.0
    assert summary.transaction_count == 1

    trends = calculate_monthly_trends(single_txn)
    assert len(trends) == 1
    assert trends[0].income_growth_pct is None

    anomalies = detect_unusual_transactions_comprehensive(single_txn)
    assert anomalies.total_anomalies == 0


# 5. Edge Case: All Income (Zero Expenses)
def test_all_income_zero_expenses():
    txns = [
        NormalizedTransaction(id="i1", date=date(2026, 8, 1), description="Payment 1", amount=20000.0, type=TransactionType.INCOME, category="Sales"),
        NormalizedTransaction(id="i2", date=date(2026, 8, 2), description="Payment 2", amount=30000.0, type=TransactionType.INCOME, category="Sales"),
    ]
    summary = calculate_summary(txns)
    assert summary.total_income == 50000.0
    assert summary.total_expenses == 0.0
    assert summary.net_cash_flow == 50000.0
    assert summary.savings_rate_pct == 100.0
    assert summary.expense_transaction_count == 0

    exp_cats = calculate_category_breakdown(txns, txn_type="expense")
    assert len(exp_cats) == 0


# 6. Edge Case: All Expenses (Zero Income)
def test_all_expenses_zero_income():
    txns = [
        NormalizedTransaction(id="e1", date=date(2026, 8, 1), description="Office Rent", amount=15000.0, type=TransactionType.EXPENSE, category="Rent"),
        NormalizedTransaction(id="e2", date=date(2026, 8, 2), description="Supplies", amount=5000.0, type=TransactionType.EXPENSE, category="Supplies"),
    ]
    summary = calculate_summary(txns)
    assert summary.total_income == 0.0
    assert summary.total_expenses == 20000.0
    assert summary.net_cash_flow == -20000.0
    # Zero income: savings rate should be 0.0 without division by zero crash
    assert summary.savings_rate_pct == 0.0
    assert summary.income_transaction_count == 0


# 7. Boundary Amounts: Fractional Cents and Large Enterprise Totals
def test_boundary_amounts():
    txns = [
        NormalizedTransaction(id="b1", date=date(2026, 8, 1), description="Micro Transaction", amount=0.01, type=TransactionType.EXPENSE, category="Misc"),
        NormalizedTransaction(id="b2", date=date(2026, 8, 2), description="Enterprise Contract", amount=50000000.00, type=TransactionType.INCOME, category="Sales"),
    ]
    summary = calculate_summary(txns)
    assert summary.total_expenses == 0.01
    assert summary.total_income == 50000000.00
    assert summary.net_cash_flow == 49999999.99


# 8. Performance Benchmark: 1,500+ Transactions Calculated in Under 250ms
def test_large_dataset_performance():
    """Ensure engine scales efficiently for small-to-medium business ledgers."""
    start_date = date(2025, 1, 1)
    txns = []
    categories = ["Payroll", "Rent", "Marketing", "Inventory", "Software", "Logistics", "Utilities"]

    for i in range(1500):
        t_date = start_date + timedelta(days=(i % 365))
        is_income = (i % 5 == 0)
        amount = 5000.0 + (i * 10.0) if is_income else 200.0 + (i * 2.5)
        cat = "Sales" if is_income else categories[i % len(categories)]
        txns.append(
            NormalizedTransaction(
                id=f"bench_{i}",
                date=t_date,
                description=f"Transaction #{i}",
                amount=round(amount, 2),
                type=TransactionType.INCOME if is_income else TransactionType.EXPENSE,
                category=cat,
            )
        )

    t0 = time.perf_counter()
    summary = calculate_summary(txns)
    trends = calculate_monthly_trends(txns)
    categories_breakdown = calculate_category_breakdown(txns, "expense")
    largest = get_largest_transactions(txns, limit=10)
    anomalies = detect_unusual_transactions_comprehensive(txns)
    duration_ms = (time.perf_counter() - t0) * 1000

    assert summary.transaction_count == 1500
    assert len(trends) >= 12
    assert len(categories_breakdown) == len(categories)
    assert len(largest) == 10
    # Must compute deterministic analytics in under 250ms
    assert duration_ms < 250.0, f"Calculation took too long: {duration_ms:.2f}ms"
