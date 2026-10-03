from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class AIStatusResponse(BaseModel):
    available: bool
    service: str = "Ollama"
    active_model: Optional[str] = None
    available_models: List[str] = []
    message: str
    setup_instructions: str


class AIGenerateRequest(BaseModel):
    session_id: str
    prompt: Optional[str] = None
    model: Optional[str] = None


class AIGenerateResponse(BaseModel):
    success: bool
    model_used: Optional[str] = None
    response: str
    is_fallback: bool = False
    context_used: Optional[Dict[str, Any]] = None


class AskBusinessRequest(BaseModel):
    session_id: str
    query: str


class AskBusinessResponse(BaseModel):
    query: str
    intent: str
    answer: str
    key_data: List[str]
    why_it_matters: str
    what_to_check: List[str]
    evidence: Dict[str, Any] = {}
