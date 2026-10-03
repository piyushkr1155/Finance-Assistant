import uuid
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Query

from models.transaction import (
    UploadResult,
    ConfirmMappingRequest,
    TransactionListResponse,
    ColumnMapping,
)
from services.file_parser import parse_uploaded_file, FileParserError
from services.normalizer import detect_columns, normalize_transactions
from services.session_store import session_store

router = APIRouter(prefix="/api", tags=["Data Import"])


@router.post("/upload", response_model=UploadResult)
async def upload_file(file: UploadFile = File(...)):
    """
    Ingest CSV or Excel file, auto-detect column mapping, and normalize transactions.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected for upload.")

    try:
        content = await file.read()
        df, file_type = parse_uploaded_file(content, file.filename)
    except FileParserError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

    session_id = uuid.uuid4().hex
    raw_columns = list(df.columns)

    # 1. Heuristic column detection
    detected_mapping = detect_columns(raw_columns)

    # 2. Normalize transactions
    transactions, invalid_rows, warnings = normalize_transactions(
        df=df,
        mapping=detected_mapping,
        session_id=session_id,
    )

    # Check for missing required fields
    missing_fields = []
    if not detected_mapping.date_col:
        missing_fields.append("Date")
    if not detected_mapping.amount_col and not (detected_mapping.debit_col and detected_mapping.credit_col):
        missing_fields.append("Amount (or Debit & Credit)")

    # 3. Store in session
    session_store.set(
        session_id=session_id,
        filename=file.filename,
        file_type=file_type,
        raw_df=df,
        mapping=detected_mapping,
        transactions=transactions,
    )

    mapping_dict = {
        "date_col": detected_mapping.date_col,
        "description_col": detected_mapping.description_col,
        "amount_col": detected_mapping.amount_col,
        "type_col": detected_mapping.type_col,
        "category_col": detected_mapping.category_col,
        "debit_col": detected_mapping.debit_col,
        "credit_col": detected_mapping.credit_col,
    }

    return UploadResult(
        session_id=session_id,
        filename=file.filename,
        file_type=file_type,
        total_rows_read=len(df),
        valid_transactions_count=len(transactions),
        invalid_rows_count=len(invalid_rows),
        columns_detected=raw_columns,
        column_mapping_used=mapping_dict,
        is_auto_mapped=True,
        missing_required_fields=missing_fields,
        invalid_rows_sample=invalid_rows[:5],
        sample_transactions=transactions[:10],
        warnings=warnings,
    )


@router.post("/upload/confirm-mapping", response_model=UploadResult)
async def confirm_mapping(payload: ConfirmMappingRequest):
    """
    Apply custom or updated column mapping to an existing session's raw data.
    """
    sess = session_store.get(payload.session_id)
    if not sess:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{payload.session_id}' not found or expired. Please re-upload the file."
        )

    # Re-normalize with the user-provided mapping
    transactions, invalid_rows, warnings = normalize_transactions(
        df=sess.raw_df,
        mapping=payload.mapping,
        session_id=payload.session_id,
    )

    missing_fields = []
    if not payload.mapping.date_col or payload.mapping.date_col not in sess.raw_df.columns:
        missing_fields.append("Date")
    has_amount = payload.mapping.amount_col and payload.mapping.amount_col in sess.raw_df.columns
    has_debit_credit = (
        payload.mapping.debit_col and payload.mapping.debit_col in sess.raw_df.columns and
        payload.mapping.credit_col and payload.mapping.credit_col in sess.raw_df.columns
    )
    if not has_amount and not has_debit_credit:
        missing_fields.append("Amount (or Debit & Credit)")

    session_store.update_transactions(
        session_id=payload.session_id,
        mapping=payload.mapping,
        transactions=transactions,
    )

    mapping_dict = {
        "date_col": payload.mapping.date_col,
        "description_col": payload.mapping.description_col,
        "amount_col": payload.mapping.amount_col,
        "type_col": payload.mapping.type_col,
        "category_col": payload.mapping.category_col,
        "debit_col": payload.mapping.debit_col,
        "credit_col": payload.mapping.credit_col,
    }

    return UploadResult(
        session_id=payload.session_id,
        filename=sess.filename,
        file_type=sess.file_type,
        total_rows_read=len(sess.raw_df),
        valid_transactions_count=len(transactions),
        invalid_rows_count=len(invalid_rows),
        columns_detected=list(sess.raw_df.columns),
        column_mapping_used=mapping_dict,
        is_auto_mapped=False,
        missing_required_fields=missing_fields,
        invalid_rows_sample=invalid_rows[:5],
        sample_transactions=transactions[:10],
        warnings=warnings,
    )


@router.get("/transactions", response_model=TransactionListResponse)
def get_transactions(
    session_id: str = Query(..., description="Active session ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None, description="Filter by description or category"),
    type: Optional[str] = Query(None, description="'income' or 'expense'"),
):
    """
    Retrieve normalized transactions for a session with optional filtering and pagination.
    """
    transactions = session_store.get_transactions(session_id)
    if transactions is None:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found. Please upload a file first."
        )

    filtered = transactions

    if type:
        filtered = [t for t in filtered if t.type.value.lower() == type.lower()]

    if search:
        s_lower = search.lower()
        filtered = [
            t for t in filtered
            if s_lower in t.description.lower() or s_lower in t.category.lower()
        ]

    total_count = len(filtered)
    paginated = filtered[offset : offset + limit]

    return TransactionListResponse(
        session_id=session_id,
        total_count=total_count,
        transactions=paginated,
    )
