import io
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from main import app
from services.context_builder import build_financial_context, context_to_numbers_set
from services.ai_validator import extract_numbers_from_text, validate_ai_response
from services.prompt_templates import (
    SYSTEM_FINANCIAL_ANALYST_PROMPT,
    build_executive_insights_prompt,
)

client = TestClient(app)


@pytest.fixture
def active_session_id():
    csv_data = (
        "Date,Description,Amount,Type,Category\n"
        "2026-07-01,Product Revenue,150000,Income,Sales & Revenue\n"
        "2026-07-05,Office Lease,25000,Expense,Rent & Facilities\n"
        "2026-08-01,Product Revenue,180000,Income,Sales & Revenue\n"
        "2026-08-05,Office Lease,25000,Expense,Rent & Facilities\n"
        "2026-08-10,Software Subscriptions,5000,Expense,Software & Subscriptions\n"
        "2026-08-14,Bulk Server Upgrade,75000,Expense,Software & Subscriptions\n"
    )
    files = {"file": ("analyst_test_ledger.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")}
    res = client.post("/api/upload", files=files)
    assert res.status_code == 200
    return res.json()["session_id"]


# 1. Test Context Builder generates certified ground truth
def test_build_financial_context(active_session_id):
    ctx = build_financial_context(active_session_id)

    assert "kpis" in ctx
    assert ctx["kpis"]["total_income"] == 330000.0  # 150k + 180k
    assert ctx["kpis"]["total_expenses"] == 130000.0  # 25k + 25k + 5k + 75k
    assert ctx["kpis"]["net_cash_flow"] == 200000.0
    assert len(ctx["monthly_summary"]) == 2
    assert len(ctx["top_expense_categories"]) >= 1

    # Test numbers extraction
    numbers = context_to_numbers_set(ctx)
    assert 330000.0 in numbers
    assert 130000.0 in numbers
    assert 200000.0 in numbers


# 2. Test Anti-Hallucination Prompt Template
def test_system_prompt_guardrails():
    assert "Zero Hallucinations" in SYSTEM_FINANCIAL_ANALYST_PROMPT
    assert "ONLY the verified numbers" in SYSTEM_FINANCIAL_ANALYST_PROMPT
    assert "Do not provide definitive legal, tax, or accounting advice" in SYSTEM_FINANCIAL_ANALYST_PROMPT

    prompt = build_executive_insights_prompt('{"total_income": 330000}')
    assert "CERTIFIED FINANCIAL CONTEXT" in prompt
    assert "Overall Financial Health" in prompt


# 3. Test Output Validator: Clean Grounded Output vs Hallucinated Output
def test_ai_output_validator():
    mock_context = {
        "kpis": {"total_income": 330000.0, "total_expenses": 130000.0, "net_cash_flow": 200000.0},
        "top_expense_categories": [{"category": "Software", "amount": 80000.0, "percentage": 61.5}],
    }

    # Case A: Grounded text with matching numbers
    grounded_text = "Total income was ₹330,000 against expenses of ₹130,000, leaving a net cash surplus of ₹200,000."
    _, is_verified, ungrounded = validate_ai_response(grounded_text, mock_context)
    assert is_verified is True
    assert len(ungrounded) == 0

    # Case B: Hallucinated text with numbers absent from context
    hallucinated_text = "Your business generated $999,999 and lost $450,000 on luxury dining."
    _, is_verified_bad, ungrounded_bad = validate_ai_response(hallucinated_text, mock_context)
    assert is_verified_bad is False
    assert 999999.0 in ungrounded_bad


# 4. Test Insights API Endpoint (Ollama Offline Fallback)
def test_ai_insights_endpoint_offline_fallback(active_session_id):
    res = client.post("/api/ai/insights", json={"session_id": active_session_id})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "330,000" in data["response"]
    assert "130,000" in data["response"]
    assert "200,000" in data["response"]


# 5. Test Insights API Endpoint (Mocked Ollama Online)
def test_ai_insights_endpoint_mocked_online(active_session_id):
    mock_status_res = MagicMock()
    mock_status_res.status_code = 200
    mock_status_res.json.return_value = {"models": [{"name": "llama3.2:1b"}]}

    mock_gen_res = MagicMock()
    mock_gen_res.status_code = 200
    mock_gen_res.json.return_value = {
        "response": "The business exhibits solid financial health with ₹330,000 in income and ₹130,000 in expenses."
    }

    with patch("httpx.Client.get", return_value=mock_status_res), \
         patch("httpx.Client.post", return_value=mock_gen_res):
        res = client.post("/api/ai/insights", json={"session_id": active_session_id})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["model_used"] == "llama3.2:1b"
        assert "330,000" in data["response"]
