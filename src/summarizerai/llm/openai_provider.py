import httpx
import logging
from typing import List, Optional
from summarizerai.llm.provider import LLMProvider
from summarizerai.config import settings

logger = logging.getLogger(__name__)

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self.base_url = "https://api.openai.com/v1"

    @property
    def provider_name(self) -> str:
        return f"openai ({self.model})"

    async def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 2048) -> str:
        if not self.api_key:
            raise RuntimeError("OpenAI API key is not configured.")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.2,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
            raise RuntimeError(f"OpenAI error {resp.status_code}: {resp.text}")

    async def embed(self, texts: List[str]) -> List[List[float]]:
        if not self.api_key:
            from summarizerai.llm.fallback_provider import FallbackProvider
            return await FallbackProvider().embed(texts)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "text-embedding-3-small",
            "input": texts,
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.base_url}/embeddings", headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return [item["embedding"] for item in data["data"]]
            raise RuntimeError(f"OpenAI embeddings error {resp.status_code}: {resp.text}")
