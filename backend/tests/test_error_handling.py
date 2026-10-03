import io
import pytest
from unittest.mock import patch
import httpx
from fastapi.testclient import TestClient

from main import app
from services.file_parser import MAX_FILE_SIZE_BYTES
from services.session_store import session_store
from services.ai_provider import ai_service, OllamaProvider
from models.ai import AIStatusResponse

client = TestClient(app)


# 1. Invalid File Extension (.pdf, .exe, .png)
def test_invalid_file_extension():
    files = {"file": ("invoice.pdf", b"%PDF-1.4 dummy binary content", "application/pdf")}
    res = client.post("/api/upload", files=files)
    assert res.status_code == 400
    assert "unsupported file format" in res.json()["detail"].lower()

    files_exe = {"file": ("malware.exe", b"MZ\x90\x00 dummy executable", "application/x-msdownload")}
    res_exe = client.post("/api/upload", files=files_exe)
    assert res_exe.status_code == 400
    assert "unsupported file format" in res_exe.json()["detail"].lower()


# 2. Corrupted Excel File
def test_corrupted_excel_file():
    corrupted_bytes = b"PK\x03\x04ThisIsNotARealZipArchiveOrExcelWorkbook"
    files = {"file": ("corrupt_ledger.xlsx", corrupted_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    res = client.post("/api/upload", files=files)
    assert res.status_code == 400
    detail = res.json()["detail"].lower()
    assert "corrupted" in detail or "valid xlsx" in detail


# 3. Missing Required Columns (Detected and reported to client for manual mapping)
def test_missing_required_columns():
    csv_missing = (
        "Description,Category,Notes\n"
        "Office Rent,Rent,Monthly invoice\n"
        "Software Subscription,Software,Monthly fee\n"
    )
    files = {"file": ("missing_cols.csv", csv_missing.encode("utf-8"), "text/csv")}
    res = client.post("/api/upload", files=files)
    assert res.status_code == 200
    data = res.json()
    assert "Date" in data["missing_required_fields"]
    assert "Amount (or Debit & Credit)" in data["missing_required_fields"]
    assert data["valid_transactions_count"] == 0


# 4. Invalid Number Format Handling (Gracefully isolated into invalid_rows)
def test_invalid_number_format_handling():
    csv_invalid_amount = (
        "Date,Description,Amount,Type\n"
        "2026-08-01,Cloud Hosting,not_a_number,Expense\n"
        "2026-08-02,Client Payment,five_hundred,Income\n"
    )
    files = {"file": ("bad_amounts.csv", csv_invalid_amount.encode("utf-8"), "text/csv")}
    res = client.post("/api/upload", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["total_rows_read"] == 2
    assert data["valid_transactions_count"] == 0
    assert data["invalid_rows_count"] == 2
    assert len(data["invalid_rows_sample"]) == 2
    assert "invalid or zero amount" in data["invalid_rows_sample"][0]["reason"].lower()


# 5. Empty File and Empty Dataset (0 rows or headers only)
def test_empty_file_and_empty_dataset():
    # Completely empty file (0 bytes)
    empty_bytes = b""
    files = {"file": ("empty.csv", empty_bytes, "text/csv")}
    res = client.post("/api/upload", files=files)
    assert res.status_code == 400
    assert "empty" in res.json()["detail"].lower()

    # Headers only (0 data rows)
    headers_only = "Date,Description,Amount,Category,Type\n"
    files = {"file": ("headers_only.csv", headers_only.encode("utf-8"), "text/csv")}
    res = client.post("/api/upload", files=files)
    assert res.status_code == 400
    detail = res.json()["detail"].lower()
    assert "does not contain any readable data rows" in detail or "empty" in detail


# 6. File Exceeding 10MB Limit
def test_file_exceeds_size_limit():
    oversized = b"A" * (MAX_FILE_SIZE_BYTES + 512)
    files = {"file": ("huge.csv", oversized, "text/csv")}
    res = client.post("/api/upload", files=files)
    assert res.status_code == 400
    assert "maximum allowed limit" in res.json()["detail"].lower()


# 7. Local AI Offline Fallbacks for all AI Endpoints
def test_ai_offline_endpoints_fallbacks():
    # Setup sample session first
    csv_data = (
        "Date,Description,Amount,Category,Type\n"
        "2026-08-01,Client Payment,5000,Consulting,Income\n"
        "2026-08-05,Software License,200,Software,Expense\n"
    )
    upload_res = client.post("/api/upload", files={"file": ("test.csv", csv_data.encode("utf-8"), "text/csv")})
    assert upload_res.status_code == 200
    session_id = upload_res.json()["session_id"]

    # When Ollama is offline:
    with patch.object(ai_service, "get_status") as mock_status, \
         patch.object(ai_service, "generate") as mock_gen:
        mock_status.return_value = AIStatusResponse(
            available=False,
            service="Ollama",
            active_model=None,
            available_models=[],
            message="Local AI is unavailable. Please start Ollama and select a model.",
            setup_instructions="Install Ollama.",
        )
        mock_gen.return_value = {
            "success": False,
            "model_used": None,
            "response": "Local AI is unavailable. Please start Ollama and select a model.",
            "is_fallback": True,
        }

        # 7a. Insights endpoint
        res_insights = client.post("/api/ai/insights", json={"session_id": session_id})
        assert res_insights.status_code == 200
        data_ins = res_insights.json()
        assert data_ins["is_fallback"] is True
        assert "executive summary" in data_ins["response"].lower()

        # 7b. Ask My Business endpoint
        res_ask = client.post("/api/ai/ask", json={"session_id": session_id, "query": "What was my highest expense?"})
        assert res_ask.status_code == 200
        data_ask = res_ask.json()
        assert len(data_ask["answer"]) > 0

        # 7c. Explain Anomaly endpoint
        # Get an anomaly id from session
        anom_res = client.get(f"/api/analytics/anomalies?session_id={session_id}")
        anoms = anom_res.json()["anomalies"]
        if anoms:
            target_id = anoms[0]["id"]
            res_anomaly = client.post(
                "/api/ai/explain-anomaly",
                json={"session_id": session_id, "anomaly_id": target_id},
            )
            assert res_anomaly.status_code == 200
            data_anom = res_anomaly.json()
            assert data_anom["is_fallback"] is True
            assert len(data_anom["ai_explanation"]) > 0


# 8. Local AI Timeout Graceful Handling
def test_ai_timeout_handling():
    provider = OllamaProvider(base_url="http://127.0.0.1:11434", timeout_seconds=1)

    with patch.object(provider, "check_availability") as mock_avail, \
         patch("httpx.Client.post", side_effect=httpx.TimeoutException("Read timed out")):
        mock_avail.return_value = AIStatusResponse(
            available=True,
            service="Ollama",
            active_model="llama3.2:1b",
            available_models=["llama3.2:1b"],
            message="Ready",
            setup_instructions="",
        )

        res = provider.generate("Analyze this budget")
        assert res["success"] is False
        assert res["is_fallback"] is True
        assert "timed out" in res["response"].lower()


# 9. Global Exception Handler
def test_global_exception_handler():
    # Use raise_server_exceptions=False so TestClient allows the FastAPI app's exception_handler to execute
    non_raising_client = TestClient(app, raise_server_exceptions=False)
    with patch("services.session_store.session_store.get", side_effect=RuntimeError("Simulated unexpected crash")):
        res = non_raising_client.get("/api/analytics/summary?session_id=any-session")
        assert res.status_code == 500
        json_data = res.json()
        assert json_data["error"] == "Internal Server Error"
        assert "detail" in json_data
        assert "unexpected error" in json_data["detail"].lower()
