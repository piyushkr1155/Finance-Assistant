import io
import pytest
from fastapi.testclient import TestClient

from main import app
from services.intent_router import detect_intent, BusinessQueryIntent, generate_structured_business_answer

client = TestClient(app)


@pytest.fixture
def active_session_id():
    csv_data = (
        "Date,Description,Amount,Type,Category\n"
        "2026-07-01,Client Retainer A,100000,Income,Sales & Revenue\n"
        "2026-07-05,Office Lease July,25000,Expense,Rent & Facilities\n"
        "2026-07-10,Software Subscriptions,5000,Expense,Software & Subscriptions\n"
        "2026-08-01,Client Retainer B,120000,Income,Sales & Revenue\n"
        "2026-08-05,Office Lease August,25000,Expense,Rent & Facilities\n"
        "2026-08-10,Software Subscriptions,6000,Expense,Software & Subscriptions\n"
        "2026-08-14,Bulk Factory Equipment Spare,88000,Expense,Inventory & Supplies\n"
    )
    files = {"file": ("ask_test_ledger.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")}
    res = client.post("/api/upload", files=files)
    assert res.status_code == 200
    return res.json()["session_id"]


# 1. Test Intent Classification
def test_intent_detection():
    assert detect_intent("Why did expenses increase this month?") == BusinessQueryIntent.EXPENSE_INCREASE
    assert detect_intent("Why were expenses higher in August?") == BusinessQueryIntent.EXPENSE_INCREASE
    assert detect_intent("What are my biggest expense categories?") == BusinessQueryIntent.CATEGORY_BREAKDOWN
    assert detect_intent("Where am I spending the most money?") == BusinessQueryIntent.CATEGORY_BREAKDOWN
    assert detect_intent("Which transactions look unusual?") == BusinessQueryIntent.UNUSUAL_TRANSACTIONS
    assert detect_intent("Any suspicious anomalies?") == BusinessQueryIntent.UNUSUAL_TRANSACTIONS
    assert detect_intent("Is my business profitable and what is my cash flow?") == BusinessQueryIntent.CASH_FLOW_PROFIT


# 2. Test 4-Part Structured Business Answer Generation
def test_structured_answer_generation(active_session_id):
    ans = generate_structured_business_answer(
        session_id=active_session_id,
        query="Why were expenses higher this month?"
    )

    assert ans["intent"] == BusinessQueryIntent.EXPENSE_INCREASE.value
    assert "increased" in ans["answer"].lower()
    assert len(ans["key_data"]) >= 3
    # Check that August expense (25k + 6k + 88k = 119k) and July expense (25k + 5k = 30k) are stated
    key_data_str = " ".join(ans["key_data"])
    assert "119,000" in key_data_str
    assert "30,000" in key_data_str
    assert ans["why_it_matters"] != ""
    assert len(ans["what_to_check"]) >= 1


# 3. Test Ask My Business API Endpoint via HTTP
def test_ask_my_business_endpoint(active_session_id):
    # Query 1: Expense increase
    payload = {
        "session_id": active_session_id,
        "query": "Why did expenses increase this month?",
    }
    res = client.post("/api/ai/ask", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["query"] == payload["query"]
    assert data["intent"] == "EXPENSE_INCREASE"
    assert "answer" in data
    assert len(data["key_data"]) > 0
    assert "why_it_matters" in data
    assert len(data["what_to_check"]) > 0

    # Query 2: Biggest categories
    payload2 = {
        "session_id": active_session_id,
        "query": "What are my biggest expense categories?",
    }
    res2 = client.post("/api/ai/ask", json=payload2)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["intent"] == "CATEGORY_BREAKDOWN"
    assert "Inventory & Supplies" in data2["answer"] or "Rent" in data2["answer"]

    # Query 3: Nonexistent session error handling
    bad_res = client.post("/api/ai/ask", json={"session_id": "nonexistent-session", "query": "hello"})
    assert bad_res.status_code == 404
