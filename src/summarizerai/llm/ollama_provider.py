import httpx
import logging
from typing import List, Optional
from summarizerai.llm.provider import LLMProvider
from summarizerai.config import settings

logger = logging.getLogger(__name__)

class OllamaProvider(LLMProvider):
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None, embed_model: Optional[str] = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.embed_model = embed_model or settings.OLLAMA_EMBED_MODEL

    @property
    def provider_name(self) -> str:
        return f"ollama ({self.model})"

    async def is_available(self) -> bool:
        """Check if Ollama service is reachable and has the requested model available."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code != 200:
                    return False
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                # Match e.g. "llama3.2" against "llama3.2:latest"
                model_base = self.model.split(":")[0]
                has_model = any(model_base in m for m in models)
                return has_model
        except Exception:
            return False

    async def list_models(self) -> List[str]:
        """List models installed in local Ollama instance."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code == 200:
                    data = resp.json()
                    return [m.get("name") for m in data.get("models", [])]
        except Exception as e:
            logger.warning(f"Could not list Ollama models: {e}")
        return []

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 2048) -> str:
        """Generate text using Ollama generate API with seamless fallback."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.3,
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(f"{self.base_url}/api/generate", json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("response", "").strip()
                else:
                    logger.warning(f"Ollama returned HTTP {resp.status_code}: {resp.text}. Falling back to local offline provider.")
        except Exception as e:
            logger.warning(f"Ollama generate request failed: {e}. Falling back to local offline provider.")

        from summarizerai.llm.fallback_provider import FallbackProvider
        return await FallbackProvider().generate(prompt, system_prompt, max_tokens)

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Ollama embedding API."""
        embeddings: List[List[float]] = []
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                for text in texts:
                    # Ollama embeddings endpoint
                    payload = {
                        "model": self.embed_model,
                        "prompt": text,
                    }
                    resp = await client.post(f"{self.base_url}/api/embeddings", json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        embeddings.append(data.get("embedding", []))
                    else:
                        # Fallback for individual item if embed model isn't pulled yet
                        raise RuntimeError(f"Ollama embedding failed with HTTP {resp.status_code}")
            return embeddings
        except Exception as e:
            logger.warning(f"Ollama embeddings failed ({e}), falling back to local vector representation.")
            from summarizerai.llm.fallback_provider import FallbackProvider
            fallback = FallbackProvider()
            return await fallback.embed(texts)
