"""
Gemini LLM provider using the official Google `google-genai` SDK v2.

Uses `google.genai.Client.aio` for async operations so it integrates
naturally with FastAPI's async runtime without blocking the event loop.
Falls back to `FallbackProvider` on any error so the app never hard-crashes.
"""

import asyncio
import logging
from typing import List, Optional

from google import genai
from google.genai import types as genai_types

from summarizerai.config import settings
from summarizerai.llm.provider import LLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """
    Cloud LLM provider backed by Google Gemini via the `google-genai` SDK.

    Configuration is driven by settings:
        GEMINI_API_KEY            – required
        GEMINI_MODEL              – e.g. "gemini-3.8-flash" (default)
        GEMINI_EMBEDDING_MODEL    – e.g. "gemini-embedding-2" (default)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        embedding_model: Optional[str] = None,
    ):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.embedding_model = embedding_model or settings.GEMINI_EMBEDDING_MODEL
        # Build client once; reused across all calls
        self._client: Optional[genai.Client] = None

    def _get_client(self) -> genai.Client:
        if self._client is None:
            if not self.api_key:
                raise RuntimeError(
                    "GEMINI_API_KEY is not set. "
                    "Add it to your .env file (backend only – never exposed to the frontend)."
                )
            http_options = genai_types.HttpOptions(
                timeout=20000,
                retry_options=genai_types.HttpRetryOptions(attempts=2, initial_delay=0.5, max_delay=2.0),
            )
            self._client = genai.Client(api_key=self.api_key, http_options=http_options)
        return self._client

    @property
    def provider_name(self) -> str:
        return f"gemini ({self.model})"

    # ------------------------------------------------------------------
    # Availability
    # ------------------------------------------------------------------

    async def is_available(self) -> bool:
        """
        Performs a lightweight models.get call to verify the API key and
        network connectivity.  Returns False (does not raise) on any error.
        """
        if not self.api_key:
            return False
        try:
            client = self._get_client()
            # list first model to validate key + connectivity
            async for _ in await client.aio.models.list():
                break
            return True
        except Exception as e:
            logger.warning("Gemini availability check failed: %s", e)
            return False

    # ------------------------------------------------------------------
    # Text generation
    # ------------------------------------------------------------------

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
    ) -> str:
        """
        Generate a text completion using Gemini.

        `system_prompt` is passed as `system_instruction` in the config
        (Gemini's native equivalent of OpenAI's system role).
        Falls back to `FallbackProvider` on any error.
        """
        try:
            client = self._get_client()

            config = genai_types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=0.2,
                system_instruction=system_prompt if system_prompt else None,
            )

            response = await client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )

            text = response.text
            if not text and response.candidates:
                parts = []
                for cand in response.candidates:
                    if cand.content and cand.content.parts:
                        for p in cand.content.parts:
                            if hasattr(p, "text") and p.text:
                                parts.append(p.text)
                if parts:
                    text = "".join(parts).strip()

            if text:
                return text.strip()

            logger.warning("Gemini returned an empty response. Falling back to local offline provider.")
            from summarizerai.llm.fallback_provider import FallbackProvider
            return await FallbackProvider().generate(prompt, system_prompt, max_tokens)

        except Exception as e:
            logger.warning(
                "Gemini generate failed (%s). Falling back to local offline provider.", e
            )
            from summarizerai.llm.fallback_provider import FallbackProvider
            return await FallbackProvider().generate(prompt, system_prompt, max_tokens)

    # ------------------------------------------------------------------
    # Embeddings
    # ------------------------------------------------------------------

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate vector embeddings using the Gemini embedding model.

        The `embed_content` endpoint accepts a list of strings.
        `EmbedContentResponse.embeddings` is a list of `ContentEmbedding`
        objects, each with a `.values` field (List[float]).
        Falls back to `FallbackProvider` on error.
        """
        if not texts:
            return []

        try:
            client = self._get_client()
            # Use semaphore to cap concurrent embed calls and avoid 429 rate limits
            sem = asyncio.Semaphore(10)

            async def _embed_one(t: str):
                async with sem:
                    return await client.aio.models.embed_content(
                        model=self.embedding_model,
                        contents=t,
                    )

            responses = await asyncio.gather(*[_embed_one(t) for t in texts])
            embeddings = []
            for resp in responses:
                if resp.embeddings and len(resp.embeddings) > 0:
                    embeddings.append(resp.embeddings[0].values)
                elif hasattr(resp, "embedding") and resp.embedding:
                    embeddings.append(resp.embedding.values)
                else:
                    embeddings.append([])
            # pyrefly: ignore [bad-return]
            return embeddings

        except Exception as e:
            logger.warning(
                "Gemini embed failed (%s). Falling back to local offline provider.", e
            )
            from summarizerai.llm.fallback_provider import FallbackProvider
            return await FallbackProvider().embed(texts)
