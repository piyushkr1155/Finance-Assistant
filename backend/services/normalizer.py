import re
import uuid
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd

from models.transaction import (
    NormalizedTransaction,
    TransactionType,
    ColumnMapping,
    InvalidRowDetail,
)

# Synonyms for heuristic column detection
SYNONYMS = {
    "date": [
        "date", "txn_date", "txndate", "transaction_date", "trans_date",
        "posting_date", "value_date", "time", "timestamp", "datetime"
    ],
    "description": [
        "description", "desc", "narration", "details", "particulars",
        "memo", "payee", "merchant", "remarks", "name", "title", "notes", "party"
    ],
    "amount": [
        "amount", "amt", "net_amount", "total", "transaction_amount", "value", "price"
    ],
    "debit": [
        "debit", "dr", "withdrawal", "expense_amount", "paid_out", "money_out", "spend", "expenses"
    ],
    "credit": [
        "credit", "cr", "deposit", "income_amount", "received_in", "money_in", "sales", "revenue", "income"
    ],
    "type": [
        "type", "transaction_type", "txn_type", "dr_cr", "credit_debit", "direction"
    ],
    "category": [
        "category", "account", "head", "expense_category", "tag", "group", "classification", "label"
    ],
}

CATEGORY_KEYWORDS = {
    "Payroll": ["salary", "payroll", "wage", "stipend", "bonus", "contractor"],
    "Rent & Facilities": ["rent", "lease", "office rent", "warehouse", "maintenance"],
    "Software & Subscriptions": ["software", "aws", "cloud", "github", "zoom", "slack", "google workspace", "adobe", "hosting", "domain", "saas"],
    "Marketing & Ads": ["marketing", "ads", "facebook", "meta", "google ads", "instagram", "campaign", "adwords"],
    "Inventory & Supplies": ["inventory", "supplies", "stock", "raw material", "purchase", "wholesale", "vendor", "packaging"],
    "Utilities": ["electricity", "water", "utility", "internet", "wifi", "broadband", "power", "gas"],
    "Travel & Commute": ["travel", "flight", "hotel", "uber", "ola", "taxi", "fuel", "train", "parking"],
    "Professional Services": ["legal", "accounting", "audit", "consultant", "advisory", "tax", "ca fee"],
    "Food & Dining": ["food", "meal", "coffee", "restaurant", "lunch", "dinner", "catering", "snacks"],
    "Sales & Revenue": ["sale", "client payment", "invoice", "customer", "consulting fee", "revenue", "service fee"],
}


def sanitize_column_name(col: str) -> str:
    """Normalize string column name: lowercase, strip, spaces to underscores, remove special chars."""
    col = str(col).strip().lower()
    col = re.sub(r"[^\w\s]", "_", col)
    col = re.sub(r"\s+", "_", col)
    return col.strip("_")


def detect_columns(df_columns: List[str]) -> ColumnMapping:
    """
    Heuristically matches original column names to standard fields.
    """
    col_map = ColumnMapping()
    normalized_cols = {col: sanitize_column_name(col) for col in df_columns}

    matched_cols = set()

    for field, synonyms in SYNONYMS.items():
        # First pass: exact matches
        for orig_col, clean_col in normalized_cols.items():
            if orig_col in matched_cols:
                continue
            if clean_col in synonyms:
                _set_mapping_field(col_map, field, orig_col)
                matched_cols.add(orig_col)
                break

        # Second pass: substring matches if not matched yet
        if _get_mapping_field(col_map, field) is None:
            for orig_col, clean_col in normalized_cols.items():
                if orig_col in matched_cols:
                    continue
                if any(syn in clean_col for syn in synonyms):
                    _set_mapping_field(col_map, field, orig_col)
                    matched_cols.add(orig_col)
                    break

    return col_map


def _set_mapping_field(mapping: ColumnMapping, field: str, col_name: str) -> None:
    if field == "date":
        mapping.date_col = col_name
    elif field == "description":
        mapping.description_col = col_name
    elif field == "amount":
        mapping.amount_col = col_name
    elif field == "debit":
        mapping.debit_col = col_name
    elif field == "credit":
        mapping.credit_col = col_name
    elif field == "type":
        mapping.type_col = col_name
    elif field == "category":
        mapping.category_col = col_name


def _get_mapping_field(mapping: ColumnMapping, field: str) -> Optional[str]:
    if field == "date":
        return mapping.date_col
    elif field == "description":
        return mapping.description_col
    elif field == "amount":
        return mapping.amount_col
    elif field == "debit":
        return mapping.debit_col
    elif field == "credit":
        return mapping.credit_col
    elif field == "type":
        return mapping.type_col
    elif field == "category":
        return mapping.category_col
    return None


def clean_number(val: Any) -> Optional[float]:
    """Parse string or numeric value into float, handling currencies and parentheses."""
    if val is None or pd.isna(val):
        return None

    if isinstance(val, (int, float)):
        return float(val)

    s = str(val).strip()
    if not s:
        return None

    # Handle parentheses notation for negative numbers: (1,200.50) -> -1200.50
    is_negative = False
    if s.startswith("(") and s.endswith(")"):
        is_negative = True
        s = s[1:-1].strip()

    # Remove currency symbols ($, INR, Rs, ₹, €, £) and commas
    s = re.sub(r"[^\d.-]", "", s)
    if not s or s == "-" or s == ".":
        return None

    try:
        num = float(s)
        return -num if is_negative else num
    except ValueError:
        return None


def parse_flexible_date(val: Any) -> Optional[date]:
    """Parses various date formats safely."""
    if val is None or pd.isna(val):
        return None

    if isinstance(val, (date, datetime)):
        return val.date() if isinstance(val, datetime) else val

    s = str(val).strip()
    if not s:
        return None

    # Handle Excel numeric serial dates (e.g. 45123)
    if re.match(r"^\d{5}(\.\d+)?$", s):
        try:
            excel_date = pd.to_datetime(float(s), unit="D", origin="1899-12-30")
            return excel_date.date()
        except Exception:
            pass

    # Try standard pandas parser
    try:
        dt = pd.to_datetime(s, dayfirst=False, errors="coerce")
        if pd.isna(dt):
            dt = pd.to_datetime(s, dayfirst=True, errors="coerce")
        if not pd.isna(dt):
            return dt.date()
    except Exception:
        pass

    return None


def infer_category(description: str, txn_type: TransactionType) -> str:
    """Infers category from description keywords, with safe defaults."""
    desc_lower = str(description).lower()
    for cat_name, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            return cat_name

    return "General Income" if txn_type == TransactionType.INCOME else "General Expense"


def normalize_transactions(
    df: pd.DataFrame,
    mapping: ColumnMapping,
    session_id: str
) -> Tuple[List[NormalizedTransaction], List[InvalidRowDetail], List[str]]:
    """
    Transforms raw DataFrame into a list of NormalizedTransaction objects.
    Records any invalid rows and produces actionable warnings.
    """
    transactions: List[NormalizedTransaction] = []
    invalid_rows: List[InvalidRowDetail] = []
    warnings: List[str] = []

    # Check for date column
    if not mapping.date_col or mapping.date_col not in df.columns:
        warnings.append("Date column is missing or not mapped.")
        return transactions, invalid_rows, warnings

    has_debit_credit = (
        mapping.debit_col and mapping.debit_col in df.columns and
        mapping.credit_col and mapping.credit_col in df.columns
    )
    has_amount = mapping.amount_col and mapping.amount_col in df.columns

    if not has_debit_credit and not has_amount:
        warnings.append("No valid Amount or Debit/Credit columns mapped.")
        return transactions, invalid_rows, warnings

    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        row_num = int(idx) + 1  # 1-indexed for business user readability

        # 1. Parse Date
        raw_date = row.get(mapping.date_col)
        parsed_date = parse_flexible_date(raw_date)
        if not parsed_date:
            invalid_rows.append(
                InvalidRowDetail(
                    row_index=row_num,
                    reason=f"Could not parse valid date from '{raw_date}'",
                    data=row_dict,
                )
            )
            continue

        # 2. Parse Description
        description = "Transaction"
        if mapping.description_col and mapping.description_col in df.columns:
            val = row.get(mapping.description_col)
            if val is not None and not pd.isna(val) and str(val).strip():
                description = str(val).strip()

        # 3. Determine Amount & Transaction Type
        amount: Optional[float] = None
        txn_type: TransactionType = TransactionType.EXPENSE

        if has_debit_credit:
            debit_val = clean_number(row.get(mapping.debit_col))
            credit_val = clean_number(row.get(mapping.credit_col))

            if credit_val and credit_val > 0:
                amount = credit_val
                txn_type = TransactionType.INCOME
            elif debit_val and debit_val > 0:
                amount = debit_val
                txn_type = TransactionType.EXPENSE
            elif debit_val is not None and credit_val is not None:
                # Both zero or empty
                invalid_rows.append(
                    InvalidRowDetail(
                        row_index=row_num,
                        reason="Both Debit and Credit amounts are zero or empty.",
                        data=row_dict,
                    )
                )
                continue
            else:
                invalid_rows.append(
                    InvalidRowDetail(
                        row_index=row_num,
                        reason="Could not parse Debit or Credit amounts.",
                        data=row_dict,
                    )
                )
                continue
        else:
            raw_amt_val = row.get(mapping.amount_col)
            parsed_amt = clean_number(raw_amt_val)
            if parsed_amt is None or parsed_amt == 0:
                invalid_rows.append(
                    InvalidRowDetail(
                        row_index=row_num,
                        reason=f"Invalid or zero amount '{raw_amt_val}'",
                        data=row_dict,
                    )
                )
                continue

            # Check explicit type column if provided
            if mapping.type_col and mapping.type_col in df.columns:
                raw_type = str(row.get(mapping.type_col, "")).lower()
                if any(k in raw_type for k in ["income", "credit", "cr", "deposit", "sale", "received", "in"]):
                    txn_type = TransactionType.INCOME
                    amount = abs(parsed_amt)
                elif any(k in raw_type for k in ["expense", "debit", "dr", "withdrawal", "payment", "out"]):
                    txn_type = TransactionType.EXPENSE
                    amount = abs(parsed_amt)
                else:
                    # Fallback to sign
                    txn_type = TransactionType.INCOME if parsed_amt > 0 else TransactionType.EXPENSE
                    amount = abs(parsed_amt)
            else:
                # Single amount column without type column
                # Standard convention: positive is income, negative is expense, OR positive expense if typical ledger
                if parsed_amt < 0:
                    txn_type = TransactionType.EXPENSE
                    amount = abs(parsed_amt)
                else:
                    # Check description keywords for income vs expense
                    desc_lower = description.lower()
                    if any(k in desc_lower for k in ["invoice", "customer payment", "sales", "consulting revenue", "deposit"]):
                        txn_type = TransactionType.INCOME
                    else:
                        txn_type = TransactionType.EXPENSE
                    amount = parsed_amt

        # 4. Parse Category
        category = ""
        if mapping.category_col and mapping.category_col in df.columns:
            cat_val = row.get(mapping.category_col)
            if cat_val is not None and not pd.isna(cat_val) and str(cat_val).strip():
                category = str(cat_val).strip()

        if not category:
            category = infer_category(description, txn_type)

        txn = NormalizedTransaction(
            id=f"txn_{idx}_{uuid.uuid4().hex[:6]}",
            date=parsed_date,
            description=description,
            amount=round(amount, 2),
            type=txn_type,
            category=category,
            raw_amount=str(row.get(mapping.amount_col or mapping.debit_col or ""))
        )
        transactions.append(txn)

    return transactions, invalid_rows, warnings
