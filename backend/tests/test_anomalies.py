import io
import pytest
from datetime import date
from fastapi.testclient import TestClient

from main import app
from models.transaction import NormalizedTransaction, TransactionType
from services.anomaly_detector import detect_unusual_transactions_comprehensive

client = TestClient(app)


@pytest.fixture
def transactions_with_variances():
    return [
        # Normal monthly expenses in Software (~₹3k - ₹4k)
        NormalizedTransaction(
            id="txn_s1",
            date=date(2026, 8, 1),
            description="Google Workspace",
            amount=3500.0,
            type=TransactionType.EXPENSE,
            category="Software & Subscriptions",
        ),
        NormalizedTransaction(
            id="txn_s2",
            date=date(2026, 8, 3),
            description="Zoom Video",
            amount=2500.0,
            type=TransactionType.EXPENSE,
            category="Software & Subscriptions",
        ),
        NormalizedTransaction(
            id="txn_s3",
            date=date(2026, 8, 5),
            description="GitHub Enterprise",
            amount=4000.0,
            type=TransactionType.EXPENSE,
            category="Software & Subscriptions",
        ),
        # Normal rent (₹25k)
        NormalizedTransaction(
            id="txn_r1",
            date=date(2026, 8, 2),
            description="Office Lease",
            amount=25000.0,
            type=TransactionType.EXPENSE,
            category="Rent & Facilities",
        ),
        # 1. Extreme Category Variance: ₹78,000 in Software (~23x baseline)
        NormalizedTransaction(
            id="txn_spike1",
            date=date(2026, 8, 15),
            description="Unplanned Cloud Cluster Overrun",
            amount=78000.0,
            type=TransactionType.EXPENSE,
            category="Software & Subscriptions",
        ),
        # 2. Large Budget Concentration: ₹90,000 in Inventory
        NormalizedTransaction(
            id="txn_spike2",
            date=date(2026, 8, 20),
            description="Bulk Heavy Industrial Motor",
            amount=90000.0,
            type=TransactionType.EXPENSE,
            category="Inventory & Supplies",
        ),
    ]


# 1. Test Deterministic Multi-Layer Outlier Detection
def test_comprehensive_anomaly_detection(transactions_with_variances):
    report = detect_unusual_transactions_comprehensive(transactions_with_variances)

    assert report.total_anomalies >= 2
    ids_flagged = [a.id for a in report.anomalies]
    assert "txn_spike1" in ids_flagged
    assert "txn_spike2" in ids_flagged

    spike1 = next(a for a in report.anomalies if a.id == "txn_spike1")
    assert "higher than the typical category average" in spike1.reason.lower()
    assert spike1.amount == 78000.0
    assert spike1.severity in ["high", "medium"]

    # Verify no fraud claim
    for a in report.anomalies:
        assert "fraud" not in a.reason.lower()


# 2. Test Explain Anomaly API Endpoint (HTTP)
def test_explain_anomaly_api_endpoint():
    csv_data = (
        "Date,Description,Amount,Type,Category\n"
        "2026-08-01,Cloud Tools,3000,Expense,Software\n"
        "2026-08-02,Cloud Tools,3500,Expense,Software\n"
        "2026-08-03,Office Lease,20000,Expense,Rent\n"
        "2026-08-15,Bulk Factory Machine,85000,Expense,Software\n"
    )
    files = {"file": ("anomaly_test_ledger.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")}
    upload_res = client.post("/api/upload", files=files)
    assert upload_res.status_code == 200
    session_id = upload_res.json()["session_id"]

    # Retrieve anomalies
    anom_res = client.get(f"/api/analytics/anomalies?session_id={session_id}")
    assert anom_res.status_code == 200
    anom_list = anom_res.json()["anomalies"]
    assert len(anom_list) >= 1
    target_id = anom_list[0]["id"]

    # Request AI anomaly explanation
    explain_res = client.post(
        "/api/ai/explain-anomaly",
        json={"session_id": session_id, "anomaly_id": target_id},
    )
    assert explain_res.status_code == 200
    data = explain_res.json()
    assert data["anomaly_id"] == target_id
    assert "85,000" in data["ai_explanation"] or "85000" in data["ai_explanation"]
    assert data["recommended_action"] != ""

    # Invalid anomaly ID should 404
    bad_res = client.post(
        "/api/ai/explain-anomaly",
        json={"session_id": session_id, "anomaly_id": "nonexistent-id"},
    )
    assert bad_res.status_code == 404
