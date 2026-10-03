import os
import httpx
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from models.ai import AIStatusResponse

PREFERRED_MODELS = [
    "llama3.2:1b",
    "llama3.2",
    "llama3.2:3b",
    "qwen2.5:1.5b",
    "qwen2.5:0.5b",
    "qwen2.5:3b",
    "phi3:mini",
    "phi3",
    "mistral",
    "llama3.1",
    "llama3",
]


class BaseAIProvider(ABC):
    """Abstract Base Class for AI Providers."""

    @abstractmethod
    def check_availability(self) -> AIStatusResponse:
        pass

    @abstractmethod
    def generate(
        self, prompt: str, system: Optional[str] = None, model: Optional[str] = None
    ) -> Dict[str, Any]:
        pass


class OllamaProvider(BaseAIProvider):
    """
    Ollama Local AI Provider.
    Interfaces directly with the local Ollama daemon via HTTP REST API.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout_seconds: int = 45,
    ):
        self.base_url = (
            base_url
            or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        ).rstrip("/")
        self.timeout_seconds = int(
            os.getenv("OLLAMA_TIMEOUT_SECONDS", str(timeout_seconds))
        )

    def check_availability(self) -> AIStatusResponse:
        """
        Queries Ollama daemon to check connectivity and list available local models.
        Never crashes if Ollama is not installed or offline.
        """
        setup_instructions = (
            "Setup Local AI with Ollama:\n"
            "1. Download and install Ollama from https://ollama.com\n"
            "2. Open a terminal and run: ollama run llama3.2:1b\n"
            "3. Refresh this page to activate local natural-language insights."
        )

        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(f"{self.base_url}/api/tags")
                if res.status_code != 200:
                    return AIStatusResponse(
                        available=False,
                        service="Ollama",
                        active_model=None,
                        available_models=[],
                        message="Local AI is unavailable. Please start Ollama and select a model.",
                        setup_instructions=setup_instructions,
                    )

                data = res.json()
                raw_models = data.get("models", [])
                model_names = [m.get("name", "") for m in raw_models if m.get("name")]

                if not model_names:
                    return AIStatusResponse(
                        available=True,
                        service="Ollama",
                        active_model=None,
                        available_models=[],
                        message="Ollama is running, but no models are downloaded yet. Run 'ollama run llama3.2:1b'.",
                        setup_instructions=setup_instructions,
                    )

                # Select best available model based on preferences
                active_model = self._select_best_model(model_names)

                return AIStatusResponse(
                    available=True,
                    service="Ollama",
                    active_model=active_model,
                    available_models=model_names,
                    message=f"Local AI ready using {active_model}.",
                    setup_instructions=setup_instructions,
                )

        except Exception:
            return AIStatusResponse(
                available=False,
                service="Ollama",
                active_model=None,
                available_models=[],
                message="Local AI is unavailable. Please start Ollama and select a model.",
                setup_instructions=setup_instructions,
            )

    def _select_best_model(self, available_models: List[str]) -> str:
        """Selects the best installed model without hardcoding assumptions."""
        # 1. Check preferred lightweight fast models first
        for preferred in PREFERRED_MODELS:
            for avail in available_models:
                if avail.lower() == preferred.lower() or avail.lower().startswith(f"{preferred.lower()}:"):
                    return avail

        # 2. If no preferred match, pick first available installed model
        return available_models[0]

    def generate(
        self, prompt: str, system: Optional[str] = None, model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates text using the local Ollama instance.
        Gracefully returns fallback response if Ollama is offline or times out.
        """
        status = self.check_availability()
        if not status.available:
            return {
                "success": False,
                "model_used": None,
                "response": (
                    "Local AI is unavailable. Please start Ollama and select a model.\n"
                    "All deterministic calculations, charts, and anomaly detectors remain fully operational."
                ),
                "is_fallback": True,
            }

        target_model = model or status.active_model
        if not target_model:
            return {
                "success": False,
                "model_used": None,
                "response": (
                    "No local model found in Ollama. Please download a model by running: "
                    "`ollama run llama3.2:1b` in your terminal."
                ),
                "is_fallback": True,
            }

        payload: Dict[str, Any] = {
            "model": target_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for deterministic adherence
                "top_p": 0.9,
            },
        }

        if system:
            payload["system"] = system

        try:
            with httpx.Client(timeout=float(self.timeout_seconds)) as client:
                res = client.post(f"{self.base_url}/api/generate", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    response_text = data.get("response", "").strip()
                    return {
                        "success": True,
                        "model_used": target_model,
                        "response": response_text,
                        "is_fallback": False,
                    }
                else:
                    return {
                        "success": False,
                        "model_used": target_model,
                        "response": f"Ollama returned error status code: {res.status_code}",
                        "is_fallback": True,
                    }
        except httpx.TimeoutException:
            return {
                "success": False,
                "model_used": target_model,
                "response": f"Local AI model timed out after {self.timeout_seconds}s. Try a lighter model like llama3.2:1b.",
                "is_fallback": True,
            }
        except Exception as e:
            return {
                "success": False,
                "model_used": target_model,
                "response": f"Error communicating with local AI: {str(e)}",
                "is_fallback": True,
            }


class FutureProvider(BaseAIProvider):
    """
    Placeholder/Extension provider for future local backends (e.g., ONNX, llama.cpp python bindings).
    """

    def check_availability(self) -> AIStatusResponse:
        return AIStatusResponse(
            available=False,
            service="FutureProvider",
            message="Alternative local backend not yet configured.",
            setup_instructions="Use Ollama as primary local intelligence provider.",
        )

    def generate(
        self, prompt: str, system: Optional[str] = None, model: Optional[str] = None
    ) -> Dict[str, Any]:
        return {
            "success": False,
            "model_used": None,
            "response": "FutureProvider is an architectural extension point.",
            "is_fallback": True,
        }


class AIService:
    """
    High-level AI Service orchestrator.
    Manages active local AI provider and encapsulates fallback logic.
    """

    def __init__(self, provider: Optional[BaseAIProvider] = None):
        self.provider = provider or OllamaProvider()

    def get_status(self) -> AIStatusResponse:
        return self.provider.check_availability()

    def generate(
        self, prompt: str, system: Optional[str] = None, model: Optional[str] = None
    ) -> Dict[str, Any]:
        return self.provider.generate(prompt, system=system, model=model)


# Global singleton instance
ai_service = AIService()
