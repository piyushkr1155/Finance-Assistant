import io
import pytest
from fastapi.testclient import TestClient

from main import app
from services.session_store import session_store

client = TestClient(app)


def test_full_e2e_lifecycle():
    """
    End-to-end integration lifecycle test:
    1. Upload CSV with 10 mixed transactions
    2. Confirm column mapping and check valid counts
    3. Query /api/transactions
    4. Query /api/analytics/summary
    5. Query /api/analytics/monthly
    6. Query /api/analytics/categories
    7. Query /api/analytics/largest-expenses
    8. Query /api/analytics/anomalies
    9. Query /api/ai/ask
    10. Query /api/ai/explain-anomaly
    11. Purge session via DELETE /api/session
    12. Verify subsequent requests return 404
    """
    csv_payload = (
        "Date,Description,Amount,Type,Category\n"
        "2026-07-01,Client Consulting Retainer,120000,Income,Consulting\n"
        "2026-07-05,Office Lease,25000,Expense,Rent\n"
        "2026-07-10,Cloud Infrastructure,3500,Expense,Technology\n"
        "2026-07-15,Marketing Ads,8000,Expense,Marketing\n"
        "2026-08-01,Product License Sales,95000,Income,Sales\n"
        "2026-08-05,Office Lease,25000,Expense,Rent\n"
        "2026-08-10,Cloud Infrastructure,3500,Expense,Technology\n"
        "2026-08-12,Team Offsite Catering,6000,Expense,Team & Culture\n"
        "2026-08-15,Massive Data Center Migration,88000,Expense,Technology\n"  # Anomaly
        "2026-08-20,Hardware Supplies,4500,Expense,Supplies\n"
    )

    # Step 1: Upload File
    files = {"file": ("business_q3_ledger.csv", io.BytesIO(csv_payload.encode("utf-8")), "text/csv")}
    upload_res = client.post("/api/upload", files=files)
    assert upload_res.status_code == 200
    upload_data = upload_res.json()
    session_id = upload_data["session_id"]
    assert upload_data["total_rows_read"] == 10
    assert upload_data["valid_transactions_count"] == 10
    assert upload_data["invalid_rows_count"] == 0

    # Step 2: Query Transactions List
    txns_res = client.get(f"/api/transactions?session_id={session_id}")
    assert txns_res.status_code == 200
    txns_data = txns_res.json()
    assert txns_data["total_count"] == 10
    assert len(txns_data["transactions"]) == 10

    # Step 3: Query Analytics Summary
    # Total Income: 120,000 + 95,000 = 215,000
    # Total Expenses: 25k + 3.5k + 8k + 25k + 3.5k + 6k + 88k + 4.5k = 163,500
    # Net: 215,000 - 163,500 = 51,500
    summary_res = client.get(f"/api/analytics/summary?session_id={session_id}")
    assert summary_res.status_code == 200
    summary_data = summary_res.json()
    assert summary_data["total_income"] == 215000.0
    assert summary_data["total_expenses"] == 163500.0
    assert summary_data["net_cash_flow"] == 51500.0
    assert summary_data["savings_rate_pct"] == round((51500.0 / 215000.0) * 100, 2)
    assert summary_data["income_transaction_count"] == 2
    assert summary_data["expense_transaction_count"] == 8

    # Step 4: Query Monthly Trends
    monthly_res = client.get(f"/api/analytics/monthly?session_id={session_id}")
    assert monthly_res.status_code == 200
    monthly_data = monthly_res.json()
    assert len(monthly_data) == 2
    assert monthly_data[0]["month"] == "2026-07"
    assert monthly_data[1]["month"] == "2026-08"

    # Step 5: Query Categories
    cat_res = client.get(f"/api/analytics/categories?session_id={session_id}&type=expense")
    assert cat_res.status_code == 200
    cat_data = cat_res.json()
    assert len(cat_data) >= 4
    top_cat = cat_data[0]
    assert top_cat["category"] == "Technology"
    # Tech expenses: 3500 + 3500 + 88000 = 95000
    assert top_cat["amount"] == 95000.0

    # Step 6: Query Largest Expenses
    largest_res = client.get(f"/api/analytics/largest-expenses?session_id={session_id}&type=expense&limit=5")
    assert largest_res.status_code == 200
    largest_data = largest_res.json()
    assert len(largest_data) == 5
    assert largest_data[0]["amount"] == 88000.0
    assert largest_data[0]["description"] == "Massive Data Center Migration"

    # Step 7: Query Anomalies
    anom_res = client.get(f"/api/analytics/anomalies?session_id={session_id}")
    assert anom_res.status_code == 200
    anom_data = anom_res.json()
    assert anom_data["total_anomalies"] >= 1
    anomaly_id = anom_data["anomalies"][0]["id"]
    assert anom_data["anomalies"][0]["amount"] == 88000.0

    # Step 8: Ask My Business (Grounded deterministic Q&A)
    ask_res = client.post("/api/ai/ask", json={"session_id": session_id, "query": "Why did my expenses increase?"})
    assert ask_res.status_code == 200
    ask_data = ask_res.json()
    assert ask_data["intent"] == "EXPENSE_INCREASE"
    assert len(ask_data["answer"]) > 0
    assert len(ask_data["key_data"]) > 0

    # Step 9: Explain Anomaly
    explain_res = client.post(
        "/api/ai/explain-anomaly",
        json={"session_id": session_id, "anomaly_id": anomaly_id}
    )
    assert explain_res.status_code == 200
    explain_data = explain_res.json()
    assert explain_data["anomaly_id"] == anomaly_id
    assert "88,000" in explain_data["ai_explanation"] or "88000" in explain_data["ai_explanation"]

    # Step 10: Purge Session (Privacy Guarantee)
    purge_res = client.delete(f"/api/session?session_id={session_id}")
    assert purge_res.status_code == 200
    assert purge_res.json()["status"] == "purged"

    # Step 11: Verify 404 on Subsequent Access
    followup_summary = client.get(f"/api/analytics/summary?session_id={session_id}")
    assert followup_summary.status_code == 404

    followup_txns = client.get(f"/api/transactions?session_id={session_id}")
    assert followup_txns.status_code == 404
