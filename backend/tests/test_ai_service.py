import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from main import app
from services.ai_provider import (
    OllamaProvider,
    AIService,
    FutureProvider,
    ai_service,
)

client = TestClient(app)


# 1. Test Graceful Degradation when Ollama is Offline
def test_ollama_offline_graceful_handling():
    # Use invalid port to guarantee offline connection error
    provider = OllamaProvider(base_url="http://127.0.0.1:99999", timeout_seconds=1)
    status = provider.check_availability()

    assert status.available is False
    assert status.active_model is None
    assert "Local AI is unavailable. Please start Ollama and select a model." in status.message
    assert "ollama run" in status.setup_instructions.lower()

    # Generate request should also return clean fallback message without raising an error
    gen_result = provider.generate("Test prompt")
    assert gen_result["success"] is False
    assert gen_result["is_fallback"] is True
    assert "Local AI is unavailable. Please start Ollama and select a model." in gen_result["response"]


# 2. Test Model Selection Heuristics when Ollama is Online
def test_model_selection_heuristics():
    provider = OllamaProvider()

    # Case A: Preferred model present among others
    models_list = ["codellama:latest", "llama3.2:1b", "mistral:latest"]
    best = provider._select_best_model(models_list)
    assert best == "llama3.2:1b"

    # Case B: Only generic / custom models present (no hardcoding failure)
    custom_list = ["custom-fin-model:latest", "other:7b"]
    best_custom = provider._select_best_model(custom_list)
    assert best_custom == "custom-fin-model:latest"


# 3. Test Mocked Successful Ollama Interaction
def test_mocked_ollama_online():
    provider = OllamaProvider()

    mock_tags_response = MagicMock()
    mock_tags_response.status_code = 200
    mock_tags_response.json.return_value = {
        "models": [{"name": "qwen2.5:1.5b"}, {"name": "llama3.2:1b"}]
    }

    mock_generate_response = MagicMock()
    mock_generate_response.status_code = 200
    mock_generate_response.json.return_value = {
        "response": "Monthly expenses increased mainly due to Inventory restocking."
    }

    with patch("httpx.Client.get", return_value=mock_tags_response):
        status = provider.check_availability()
        assert status.available is True
        assert status.active_model == "llama3.2:1b"
        assert "qwen2.5:1.5b" in status.available_models

    with patch("httpx.Client.get", return_value=mock_tags_response), \
         patch("httpx.Client.post", return_value=mock_generate_response):
        res = provider.generate("Why did expenses increase?")
        assert res["success"] is True
        assert res["model_used"] == "llama3.2:1b"
        assert "Inventory restocking" in res["response"]


# 4. Test FutureProvider / Architecture Abstraction
def test_future_provider_abstraction():
    future_provider = FutureProvider()
    service = AIService(provider=future_provider)

    status = service.get_status()
    assert status.available is False
    assert status.service == "FutureProvider"


# 5. Test AI API Status Endpoint via HTTP
def test_ai_status_endpoint():
    response = client.get("/api/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert "available" in data
    assert "service" in data
    assert "message" in data


# 6. Test Main Health Check Includes AI Status
def test_health_check_includes_ai():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "ollama_available" in data
    assert "message" in data
