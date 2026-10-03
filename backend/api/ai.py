from fastapi import APIRouter
from services.ai_provider import ai_service
from models.ai import AIStatusResponse

router = APIRouter(prefix="/api/ai", tags=["Local AI"])


@router.get("/status", response_model=AIStatusResponse)
def get_ai_status():
    """
    Check if local Ollama daemon is running, inspect installed models,
    and return setup instructions if unavailable.
    """
    return ai_service.get_status()
