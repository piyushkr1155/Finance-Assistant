import io
import pytest
from fastapi.testclient import TestClient

from main import app
from services.file_parser import sanitize_filename, parse_uploaded_file, FileParserError, MAX_FILE_SIZE_BYTES
from services.session_store import session_store

client = TestClient(app)


# 1. Test Filename Sanitization prevents Directory Traversal
def test_sanitize_filename():
    assert sanitize_filename("../../../etc/passwd.csv") == "passwd.csv"
    assert sanitize_filename("..\\..\\windows\\system32\\cmd.exe.xlsx") == "cmd.exe.xlsx"
    assert sanitize_filename("my\x00_ledger.csv") == "my_ledger.csv"
    assert sanitize_filename("safe_statement_2026.csv") == "safe_statement_2026.csv"
    assert sanitize_filename("") == "unnamed_file"


# 2. Test File Size Limit Enforcement (> 10MB rejected)
def test_file_size_limit_rejection():
    # 11 MB of dummy data
    oversized_bytes = b"0" * (MAX_FILE_SIZE_BYTES + 1024)

    with pytest.raises(FileParserError) as exc_info:
        parse_uploaded_file(oversized_bytes, "oversized.csv")

    assert "exceeds maximum allowed limit" in str(exc_info.value).lower()


# 3. Test In-Memory Session Purge Endpoint (DELETE /api/session)
def test_session_purge_privacy():
    csv_data = (
        "Date,Description,Amount,Type\n"
        "2026-08-01,Private Consulting,50000,Income\n"
    )
    files = {"file": ("confidential.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")}
    upload_res = client.post("/api/upload", files=files)
    assert upload_res.status_code == 200
    session_id = upload_res.json()["session_id"]

    # Verify session exists in memory
    assert session_store.get(session_id) is not None

    # Call purge endpoint
    purge_res = client.delete(f"/api/session?session_id={session_id}")
    assert purge_res.status_code == 200
    assert purge_res.json()["status"] == "purged"

    # Verify session is erased from memory
    assert session_store.get(session_id) is None

    # Subsequent transaction queries should return 404 Not Found
    get_res = client.get(f"/api/transactions?session_id={session_id}")
    assert get_res.status_code == 404

    # Purging an already purged session should return 404
    second_purge = client.delete(f"/api/session?session_id={session_id}")
    assert second_purge.status_code == 404
