import io
import os
import re
import pandas as pd
from typing import Tuple

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


class FileParserError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes user-provided filename to prevent path traversal, null bytes,
    and injection attacks.
    """
    if not filename:
        return "unnamed_file"

    # Strip directory paths
    base = os.path.basename(filename)

    # Remove null bytes and non-printable control characters
    base = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", base)

    # Remove path traversal characters (../, ..\\)
    base = re.sub(r"\.\.+", ".", base)

    # Remove potentially dangerous characters, allowing alphanumeric, space, dot, underscore, dash
    base = re.sub(r"[^\w\s.-]", "", base).strip()

    # Fallback if empty after sanitization
    if not base:
        return "sanitized_file"

    # Limit filename length to 100 chars
    return base[:100]


def parse_uploaded_file(file_bytes: bytes, filename: str) -> Tuple[pd.DataFrame, str]:
    """
    Parses uploaded CSV or Excel bytes into a pandas DataFrame in memory.
    Validates file extension, size, and handles multiple encodings without writing to disk.
    """
    if not filename:
        raise FileParserError("Filename must not be empty.")

    clean_name = sanitize_filename(filename)
    _, ext = os.path.splitext(clean_name.lower())

    if ext not in SUPPORTED_EXTENSIONS:
        raise FileParserError(
            f"Unsupported file format '{ext}'. Supported formats are: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    if len(file_bytes) == 0:
        raise FileParserError("Uploaded file is empty (0 bytes).")

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise FileParserError(
            f"File size ({len(file_bytes) / (1024 * 1024):.2f}MB) exceeds maximum allowed limit of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB."
        )

    df: pd.DataFrame
    file_type: str = ext.lstrip(".").upper()

    if ext == ".csv":
        df = _parse_csv(file_bytes)
    elif ext in {".xlsx", ".xls"}:
        df = _parse_excel(file_bytes)
    else:
        raise FileParserError(f"Unsupported file type '{ext}'.")

    # Drop completely empty rows and columns
    df = df.dropna(how="all").dropna(axis=1, how="all")

    if df.empty or len(df.columns) == 0:
        raise FileParserError("The uploaded file does not contain any readable data rows or columns.")

    return df, file_type


def _parse_csv(file_bytes: bytes) -> pd.DataFrame:
    encodings_to_try = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]
    delimiters_to_try = [",", ";", "\t"]

    last_error = None
    for enc in encodings_to_try:
        try:
            text_content = file_bytes.decode(enc)
            for delim in delimiters_to_try:
                try:
                    df = pd.read_csv(
                        io.StringIO(text_content),
                        sep=delim,
                        dtype=str,
                        keep_default_na=True,
                        skip_blank_lines=True,
                    )
                    if len(df.columns) > 1 or (len(df.columns) == 1 and delim == ","):
                        return df
                except Exception as e:
                    last_error = e
                    continue
        except UnicodeDecodeError:
            continue

    if last_error:
        raise FileParserError(f"Failed to parse CSV file: {str(last_error)}")
    raise FileParserError("Could not decode CSV file with supported encodings (UTF-8, Latin-1, CP1252).")


def _parse_excel(file_bytes: bytes) -> pd.DataFrame:
    try:
        buffer = io.BytesIO(file_bytes)
        df = pd.read_excel(buffer, engine="openpyxl", dtype=str)
        return df
    except Exception as e:
        err_msg = str(e)
        if any(w in err_msg.lower() for w in ["zip", "badzipfile", "file is not a zip", "corrupt", "header"]):
            raise FileParserError(
                "The uploaded Excel file is corrupted, incomplete, or not a valid XLSX document."
            )
        raise FileParserError(f"Failed to read Excel spreadsheet: {err_msg}")
