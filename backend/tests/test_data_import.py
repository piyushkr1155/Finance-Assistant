import io
import pytest
import pandas as pd
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def create_csv_bytes(content: str) -> io.BytesIO:
    return io.BytesIO(content.encode("utf-8"))


def create_excel_bytes(df: pd.DataFrame) -> io.BytesIO:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output


# 1. Test Valid CSV Upload
def test_upload_valid_csv():
    csv_data = (
        "Date,Description,Amount,Type,Category\n"
        "2026-08-01,Inventory purchase,25000,Expense,Inventory\n"
        "2026-08-02,Customer payment,42000,Income,Sales\n"
        "2026-08-03,Office supplies,1500,Expense,Supplies\n"
    )
    files = {"file": ("test_ledger.csv", create_csv_bytes(csv_data), "text/csv")}
    response = client.post("/api/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["file_type"] == "CSV"
    assert data["total_rows_read"] == 3
    assert data["valid_transactions_count"] == 3
    assert data["invalid_rows_count"] == 0
    assert len(data["sample_transactions"]) == 3
    assert data["sample_transactions"][0]["amount"] == 25000.0
    assert data["sample_transactions"][0]["type"] == "expense"
    assert data["sample_transactions"][1]["type"] == "income"


# 2. Test Valid Excel (XLSX) Upload
def test_upload_valid_xlsx():
    df = pd.DataFrame({
        "Posting Date": ["2026-08-05", "2026-08-06"],
        "Particulars": ["Server hosting", "Client retainer"],
        "Net Amount": ["$3,200.50", "₹1,50,000.00"],
        "Direction": ["Debit", "Credit"],
        "Head": ["Software", "Consulting"],
    })
    excel_io = create_excel_bytes(df)
    files = {
        "file": ("financials.xlsx", excel_io, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    }
    response = client.post("/api/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["file_type"] == "XLSX"
    assert data["total_rows_read"] == 2
    assert data["valid_transactions_count"] == 2
    assert data["sample_transactions"][0]["amount"] == 3200.50
    assert data["sample_transactions"][0]["type"] == "expense"
    assert data["sample_transactions"][1]["amount"] == 150000.0
    assert data["sample_transactions"][1]["type"] == "income"


# 3. Test Dual Column Format (Debit and Credit Columns)
def test_upload_debit_credit_columns():
    csv_data = (
        "Date,Narration,Debit,Credit\n"
        "2026-08-10,Google Ads,12000,\n"
        "2026-08-11,Product Sales,,85000\n"
    )
    files = {"file": ("bank_statement.csv", create_csv_bytes(csv_data), "text/csv")}
    response = client.post("/api/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["valid_transactions_count"] == 2
    txns = data["sample_transactions"]
    assert txns[0]["type"] == "expense"
    assert txns[0]["amount"] == 12000.0
    assert txns[1]["type"] == "income"
    assert txns[1]["amount"] == 85000.0


# 4. Test Missing Required Columns (e.g. no Amount or Debit/Credit)
def test_upload_missing_amount_column():
    csv_data = (
        "Date,Description,Notes\n"
        "2026-08-01,Just notes,nothing here\n"
    )
    files = {"file": ("bad_columns.csv", create_csv_bytes(csv_data), "text/csv")}
    response = client.post("/api/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert "Amount (or Debit & Credit)" in data["missing_required_fields"]
    assert data["valid_transactions_count"] == 0


# 5. Test Invalid Amounts (Handling corrupted rows gracefully)
def test_upload_invalid_amount_rows():
    csv_data = (
        "Date,Description,Amount\n"
        "2026-08-01,Valid expense,500.00\n"
        "2026-08-02,Corrupted entry,NOT_A_NUMBER\n"
        "2026-08-03,Zero amount,0.00\n"
        "2026-08-04,Valid income,-250.00\n"
    )
    files = {"file": ("dirty_data.csv", create_csv_bytes(csv_data), "text/csv")}
    response = client.post("/api/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["total_rows_read"] == 4
    assert data["valid_transactions_count"] == 2
    assert data["invalid_rows_count"] == 2
    assert len(data["invalid_rows_sample"]) > 0
    assert data["invalid_rows_sample"][0]["row_index"] == 2


# 6. Test Empty File
def test_upload_empty_file():
    files = {"file": ("empty.csv", io.BytesIO(b""), "text/csv")}
    response = client.post("/api/upload", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


# 7. Test Unsupported File Format
def test_upload_unsupported_file():
    files = {"file": ("document.pdf", io.BytesIO(b"dummy pdf content"), "application/pdf")}
    response = client.post("/api/upload", files=files)
    assert response.status_code == 400
    assert "unsupported file format" in response.json()["detail"].lower()


# 8. Test Confirm / Override Column Mapping
def test_confirm_column_mapping_override():
    # Upload CSV with unusual non-standard headers
    csv_data = (
        "ColA,ColB,ColC\n"
        "2026-08-15,Consulting Fee,4500\n"
        "2026-08-16,Office Supplies,320\n"
    )
    files = {"file": ("unmapped.csv", create_csv_bytes(csv_data), "text/csv")}
    upload_res = client.post("/api/upload", files=files)
    assert upload_res.status_code == 200
    session_id = upload_res.json()["session_id"]

    # Explicitly map ColA -> date, ColB -> description, ColC -> amount
    confirm_payload = {
        "session_id": session_id,
        "mapping": {
            "date_col": "ColA",
            "description_col": "ColB",
            "amount_col": "ColC",
        }
    }
    confirm_res = client.post("/api/upload/confirm-mapping", json=confirm_payload)
    assert confirm_res.status_code == 200
    data = confirm_res.json()
    assert data["is_auto_mapped"] is False
    assert data["valid_transactions_count"] == 2
    assert data["sample_transactions"][0]["description"] == "Consulting Fee"
    assert data["sample_transactions"][0]["amount"] == 4500.0


# 9. Test Get Normalized Transactions endpoint
def test_get_transactions_endpoint():
    csv_data = (
        "Date,Description,Amount,Type\n"
        "2026-08-01,Office Rent,25000,Expense\n"
        "2026-08-02,Product Sales,60000,Income\n"
    )
    files = {"file": ("query_test.csv", create_csv_bytes(csv_data), "text/csv")}
    upload_res = client.post("/api/upload", files=files)
    session_id = upload_res.json()["session_id"]

    # Query all
    txns_res = client.get(f"/api/transactions?session_id={session_id}")
    assert txns_res.status_code == 200
    assert txns_res.json()["total_count"] == 2

    # Filter by type
    income_res = client.get(f"/api/transactions?session_id={session_id}&type=income")
    assert income_res.status_code == 200
    assert income_res.json()["total_count"] == 1
    assert income_res.json()["transactions"][0]["description"] == "Product Sales"
