"""
Provider-agnostic LLM factory.

Resolution order (determined by DEFAULT_LLM_PROVIDER in .env):
  "gemini"   →  GeminiProvider   (default – cloud, requires GEMINI_API_KEY)
  "ollama"   →  OllamaProvider   (optional local runner)
  "openai"   →  OpenAIProvider   (optional cloud, requires OPENAI_API_KEY)
  anything   →  FallbackProvider (always works, deterministic offline engine)

Each provider is tried once; if it reports itself unavailable the factory
falls through to FallbackProvider so startup never raises an exception.
"""

import logging
from summarizerai.config import settings
from summarizerai.llm.provider import LLMProvider
from summarizerai.llm.fallback_provider import FallbackProvider

logger = logging.getLogger(__name__)


async def get_llm_provider() -> LLMProvider:
    """
    Return the active LLMProvider instance based on the configured preference.

    The logic is intentionally sequential (not parallel) so only one
    provider is instantiated per request; providers share no mutable state.
    """
    # Support both LLM_PROVIDER and DEFAULT_LLM_PROVIDER from .env
    preferred = (getattr(settings, "LLM_PROVIDER", None) or settings.DEFAULT_LLM_PROVIDER or "gemini").lower().strip()

    # ------------------------------------------------------------------ #
    # Google Gemini – primary cloud provider                              #
    # ------------------------------------------------------------------ #
    if preferred == "gemini":
        if not settings.GEMINI_API_KEY:
            logger.warning(
                "LLM_PROVIDER=gemini but GEMINI_API_KEY is empty. "
                "Using local FallbackProvider. Set GEMINI_API_KEY in .env to enable Gemini."
            )
            return FallbackProvider()

        from summarizerai.llm.gemini_provider import GeminiProvider
        gemini = GeminiProvider()
        # Skip heavy availability ping in dev – trust the key check above.
        # Set DEBUG=false in production to force the connectivity check.
        if not settings.DEBUG:
            if not await gemini.is_available():
                logger.warning(
                    "Gemini is configured but availability check failed. "
                    "Falling back to local offline provider."
                )
                return FallbackProvider()
        logger.info("Using Gemini LLM provider (%s).", gemini.model)
        return gemini

    # ------------------------------------------------------------------ #
    # Ollama – optional local-first provider                              #
    # ------------------------------------------------------------------ #
    elif preferred == "ollama":
        from summarizerai.llm.ollama_provider import OllamaProvider
        ollama = OllamaProvider()
        if await ollama.is_available():
            logger.info("Using local Ollama LLM provider (%s).", ollama.model)
            return ollama
        logger.warning(
            "Ollama is configured as default provider but is not responding on %s. "
            "Falling back to local offline provider.",
            settings.OLLAMA_BASE_URL,
        )
        return FallbackProvider()

    # ------------------------------------------------------------------ #
    # OpenAI – optional cloud provider                                    #
    # ------------------------------------------------------------------ #
    elif preferred == "openai":
        if not settings.OPENAI_API_KEY:
            logger.warning("DEFAULT_LLM_PROVIDER=openai but OPENAI_API_KEY is empty. Using FallbackProvider.")
            return FallbackProvider()
        from summarizerai.llm.openai_provider import OpenAIProvider
        openai = OpenAIProvider()
        if await openai.is_available():
            logger.info("Using OpenAI LLM provider (%s).", openai.model)
            return openai
        return FallbackProvider()

    # ------------------------------------------------------------------ #
    # Explicit fallback or unrecognised value                             #
    # ------------------------------------------------------------------ #
    logger.info("Using local offline FallbackProvider (provider=%s).", preferred)
    return FallbackProvider()
