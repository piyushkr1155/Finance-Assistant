import io
import pytest
from datetime import date
from fastapi.testclient import TestClient

from main import app
from models.transaction import NormalizedTransaction, TransactionType
from services.analytics_engine import (
    calculate_summary,
    calculate_monthly_trends,
    calculate_category_breakdown,
    get_largest_transactions,
    detect_unusual_transactions,
)

client = TestClient(app)


@pytest.fixture
def sample_transactions():
    return [
        # July 2026
        NormalizedTransaction(
            id="t1",
            date=date(2026, 7, 5),
            description="Client Payment A",
            amount=100000.0,
            type=TransactionType.INCOME,
            category="Sales & Revenue",
        ),
        NormalizedTransaction(
            id="t2",
            date=date(2026, 7, 10),
            description="Office Rent July",
            amount=25000.0,
            type=TransactionType.EXPENSE,
            category="Rent & Facilities",
        ),
        NormalizedTransaction(
            id="t3",
            date=date(2026, 7, 15),
            description="Software Subs",
            amount=5000.0,
            type=TransactionType.EXPENSE,
            category="Software & Subscriptions",
        ),
        # August 2026
        NormalizedTransaction(
            id="t4",
            date=date(2026, 8, 2),
            description="Client Payment B",
            amount=150000.0,
            type=TransactionType.INCOME,
            category="Sales & Revenue",
        ),
        NormalizedTransaction(
            id="t5",
            date=date(2026, 8, 10),
            description="Office Rent Aug",
            amount=25000.0,
            type=TransactionType.EXPENSE,
            category="Rent & Facilities",
        ),
        NormalizedTransaction(
            id="t6",
            date=date(2026, 8, 12),
            description="Software Subs Aug",
            amount=6000.0,
            type=TransactionType.EXPENSE,
            category="Software & Subscriptions",
        ),
        NormalizedTransaction(
            id="t7",
            date=date(2026, 8, 14),
            description="Bulk Raw Material (Unusual)",
            amount=95000.0,
            type=TransactionType.EXPENSE,
            category="Software & Subscriptions",  # Intentionally placed in small-avg category
        ),
    ]


# 1. Test Deterministic Summary Calculations
def test_calculate_summary(sample_transactions):
    summary = calculate_summary(sample_transactions)

    expected_income = 100000.0 + 150000.0  # 250,000.0
    expected_expense = 25000.0 + 5000.0 + 25000.0 + 6000.0 + 95000.0  # 156,000.0
    expected_net = expected_income - expected_expense  # 94,000.0

    assert summary.total_income == expected_income
    assert summary.total_expenses == expected_expense
    assert summary.net_cash_flow == expected_net
    assert summary.transaction_count == 7
    assert summary.income_transaction_count == 2
    assert summary.expense_transaction_count == 5
    assert summary.top_expense_category == "Software & Subscriptions"
    assert summary.top_income_category == "Sales & Revenue"
    assert summary.start_date == "2026-07-05"
    assert summary.end_date == "2026-08-14"
    assert summary.savings_rate_pct == round((expected_net / expected_income) * 100, 2)


# 2. Test Deterministic Monthly Trends & Growth Rates
def test_calculate_monthly_trends(sample_transactions):
    monthly = calculate_monthly_trends(sample_transactions)

    assert len(monthly) == 2
    july = monthly[0]
    aug = monthly[1]

    assert july.month == "2026-07"
    assert july.income == 100000.0
    assert july.expenses == 30000.0  # 25k + 5k
    assert july.net == 70000.0
    assert july.income_growth_pct is None  # First month has no prev baseline
    assert july.expense_growth_pct is None

    assert aug.month == "2026-08"
    assert aug.income == 150000.0
    assert aug.expenses == 126000.0  # 25k + 6k + 95k
    assert aug.net == 24000.0
    # Income growth: (150000 - 100000) / 100000 * 100 = 50.0%
    assert aug.income_growth_pct == 50.0
    # Expense growth: (126000 - 30000) / 30000 * 100 = 320.0%
    assert aug.expense_growth_pct == 320.0


# 3. Test Deterministic Category Breakdown
def test_calculate_category_breakdown(sample_transactions):
    breakdown = calculate_category_breakdown(sample_transactions, txn_type="expense")

    assert len(breakdown) == 2
    # Software & Subscriptions: 5k + 6k + 95k = 106,000.0
    assert breakdown[0].category == "Software & Subscriptions"
    assert breakdown[0].amount == 106000.0
    assert breakdown[0].transaction_count == 3

    # Rent & Facilities: 25k + 25k = 50,000.0
    assert breakdown[1].category == "Rent & Facilities"
    assert breakdown[1].amount == 50000.0
    assert breakdown[1].transaction_count == 2

    # Verify percentages sum to 100%
    total_pct = sum(b.percentage for b in breakdown)
    assert pytest.approx(total_pct, 0.1) == 100.0


# 4. Test Largest Transactions
def test_get_largest_transactions(sample_transactions):
    largest = get_largest_transactions(sample_transactions, limit=3)
    assert len(largest) == 3
    assert largest[0].amount == 150000.0
    assert largest[1].amount == 100000.0
    assert largest[2].amount == 95000.0


# 5. Test Deterministic Outlier & Unusual Transaction Detection
def test_detect_unusual_transactions(sample_transactions):
    report = detect_unusual_transactions(sample_transactions)

    assert report.total_anomalies >= 1
    flagged = report.anomalies[0]
    assert flagged.amount == 95000.0
    assert (
        "typical category average" in flagged.reason.lower()
        or "exceeds typical" in flagged.reason.lower()
        or "higher than" in flagged.reason.lower()
    )
    assert flagged.severity in ["high", "medium"]


# 6. Test Analytics API Endpoints via HTTP
def test_analytics_api_endpoints():
    csv_data = (
        "Date,Description,Amount,Type,Category\n"
        "2026-08-01,Product Revenue,80000,Income,Sales\n"
        "2026-08-05,Office Rent,20000,Expense,Rent\n"
        "2026-08-10,Software,5000,Expense,Tech\n"
        "2026-08-15,Massive Hardware Purchase,65000,Expense,Tech\n"
    )
    files = {"file": ("api_test_ledger.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")}
    upload_res = client.post("/api/upload", files=files)
    assert upload_res.status_code == 200
    session_id = upload_res.json()["session_id"]

    # Test /api/analytics/summary
    summary_res = client.get(f"/api/analytics/summary?session_id={session_id}")
    assert summary_res.status_code == 200
    s_data = summary_res.json()
    assert s_data["total_income"] == 80000.0
    assert s_data["total_expenses"] == 90000.0
    assert s_data["net_cash_flow"] == -10000.0

    # Test /api/analytics/monthly
    monthly_res = client.get(f"/api/analytics/monthly?session_id={session_id}")
    assert monthly_res.status_code == 200
    assert len(monthly_res.json()) == 1
    assert monthly_res.json()[0]["month"] == "2026-08"

    # Test /api/analytics/categories
    cat_res = client.get(f"/api/analytics/categories?session_id={session_id}&type=expense")
    assert cat_res.status_code == 200
    assert len(cat_res.json()) == 2
    assert cat_res.json()[0]["category"] == "Tech"
    assert cat_res.json()[0]["amount"] == 70000.0

    # Test /api/analytics/anomalies
    anom_res = client.get(f"/api/analytics/anomalies?session_id={session_id}")
    assert anom_res.status_code == 200
    anom_data = anom_res.json()
    assert anom_data["total_anomalies"] >= 1
    assert anom_data["anomalies"][0]["amount"] == 65000.0

    # Test direct aliases (/analytics/summary)
    alias_res = client.get(f"/analytics/summary?session_id={session_id}")
    assert alias_res.status_code == 200
    assert alias_res.json()["total_income"] == 80000.0
