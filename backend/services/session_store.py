import time
from typing import Dict, Any, Optional, List
import pandas as pd
from models.transaction import NormalizedTransaction, ColumnMapping


class SessionData:
    def __init__(
        self,
        session_id: str,
        filename: str,
        file_type: str,
        raw_df: pd.DataFrame,
        mapping: ColumnMapping,
        transactions: List[NormalizedTransaction],
    ):
        self.session_id = session_id
        self.filename = filename
        self.file_type = file_type
        self.raw_df = raw_df
        self.mapping = mapping
        self.transactions = transactions
        self.created_at = time.time()
        self.last_accessed = time.time()


class SessionStore:
    def __init__(self):
        self._sessions: Dict[str, SessionData] = {}

    def set(
        self,
        session_id: str,
        filename: str,
        file_type: str,
        raw_df: pd.DataFrame,
        mapping: ColumnMapping,
        transactions: List[NormalizedTransaction],
    ) -> SessionData:
        data = SessionData(
            session_id=session_id,
            filename=filename,
            file_type=file_type,
            raw_df=raw_df,
            mapping=mapping,
            transactions=transactions,
        )
        self._sessions[session_id] = data
        return data

    def get(self, session_id: str) -> Optional[SessionData]:
        sess = self._sessions.get(session_id)
        if sess:
            sess.last_accessed = time.time()
        return sess

    def get_transactions(self, session_id: str) -> Optional[List[NormalizedTransaction]]:
        sess = self.get(session_id)
        return sess.transactions if sess else None

    def update_transactions(
        self, session_id: str, mapping: ColumnMapping, transactions: List[NormalizedTransaction]
    ) -> bool:
        sess = self._sessions.get(session_id)
        if not sess:
            return False
        sess.mapping = mapping
        sess.transactions = transactions
        sess.last_accessed = time.time()
        return True

    def clear(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False


# Global singleton instance
session_store = SessionStore()
