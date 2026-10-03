from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import date


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class NormalizedTransaction(BaseModel):
    id: str
    date: date
    description: str
    amount: float
    type: TransactionType
    category: str
    raw_amount: Optional[str] = None


class ColumnMapping(BaseModel):
    date_col: Optional[str] = None
    description_col: Optional[str] = None
    amount_col: Optional[str] = None
    type_col: Optional[str] = None
    category_col: Optional[str] = None
    debit_col: Optional[str] = None
    credit_col: Optional[str] = None


class InvalidRowDetail(BaseModel):
    row_index: int
    reason: str
    data: Dict[str, Any]


class UploadResult(BaseModel):
    session_id: str
    filename: str
    file_type: str
    total_rows_read: int
    valid_transactions_count: int
    invalid_rows_count: int
    columns_detected: List[str]
    column_mapping_used: Dict[str, Optional[str]]
    is_auto_mapped: bool
    missing_required_fields: List[str] = []
    invalid_rows_sample: List[InvalidRowDetail] = []
    sample_transactions: List[NormalizedTransaction] = []
    warnings: List[str] = []


class ConfirmMappingRequest(BaseModel):
    session_id: str
    mapping: ColumnMapping


class TransactionListResponse(BaseModel):
    session_id: str
    total_count: int
    transactions: List[NormalizedTransaction]
