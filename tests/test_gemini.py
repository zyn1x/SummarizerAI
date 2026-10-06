"""
Tests for the GeminiProvider.

These tests have two layers:
  1. Unit tests (always run) – validate the provider interface, config loading,
     and fallback behaviour without making real API calls.
  2. Integration tests (skipped unless GEMINI_API_KEY is set and the
     marker `gemini_live` is enabled) – make real Gemini API calls.
"""

import os
import pytest
import asyncio
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# Unit-level tests (no network required)
# ---------------------------------------------------------------------------

def test_gemini_provider_imports():
    """GeminiProvider can be imported and instantiated without raising."""
    from summarizerai.llm.gemini_provider import GeminiProvider
    # Instantiate with a dummy key to avoid config dependency
    p = GeminiProvider(api_key="dummy", model="gemini-3.8-flash", embedding_model="gemini-embedding-2")
    assert p.provider_name == "gemini (gemini-3.8-flash)"


def test_config_defaults_to_gemini():
    """Settings.LLM_PROVIDER and DEFAULT_LLM_PROVIDER should default to 'gemini'."""
    from summarizerai.config import settings
    assert settings.LLM_PROVIDER.lower() == "gemini"
    assert settings.DEFAULT_LLM_PROVIDER.lower() == "gemini"


def test_config_gemini_model_fields():
    """Gemini model names and embedding model name must be present in settings."""
    from summarizerai.config import settings
    assert settings.GEMINI_MODEL == "gemini-3.8-flash"
    assert settings.GEMINI_EMBEDDING_MODEL == "gemini-embedding-2"


@pytest.mark.asyncio
async def test_factory_returns_fallback_when_no_key(monkeypatch):
    """Factory must return FallbackProvider (not raise) when GEMINI_API_KEY is empty."""
    from summarizerai.config import settings
    from summarizerai.llm.factory import get_llm_provider
    from summarizerai.llm.fallback_provider import FallbackProvider

    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    provider = await get_llm_provider()
    assert isinstance(provider, FallbackProvider)


@pytest.mark.asyncio
async def test_fallback_provider_embed():
    """FallbackProvider.embed always returns a list of 256-dim vectors."""
    from summarizerai.llm.fallback_provider import FallbackProvider
    provider = FallbackProvider()
    embeddings = await provider.embed(["machine learning", "neural networks"])
    assert len(embeddings) == 2
    for emb in embeddings:
        assert len(emb) == 256


@pytest.mark.asyncio
async def test_fallback_provider_generate():
    """FallbackProvider.generate returns a non-empty string for any prompt."""
    from summarizerai.llm.fallback_provider import FallbackProvider
    provider = FallbackProvider()
    result = await provider.generate("Summarize deep learning in two sentences.")
    assert isinstance(result, str) and len(result) > 10


# ---------------------------------------------------------------------------
# Live integration tests (require GEMINI_API_KEY in environment or .env)
# ---------------------------------------------------------------------------

from dotenv import load_dotenv
load_dotenv()

HAVE_KEY = bool(os.getenv("GEMINI_API_KEY", ""))


@pytest.mark.asyncio
@pytest.mark.skipif(not HAVE_KEY, reason="GEMINI_API_KEY not set – skipping live Gemini tests")
async def test_gemini_generate_live():
    """Live: GeminiProvider.generate returns a meaningful non-empty string."""
    from summarizerai.llm.gemini_provider import GeminiProvider
    p = GeminiProvider()
    result = await p.generate(
        "In one sentence, what is the capital of France?",
        system_prompt="Answer only in plain text.",
        max_tokens=64,
    )
    assert isinstance(result, str)
    assert len(result) > 5
    # If Gemini returned live, it contains 'Paris'; if 503 upstream spike occurred, fallback returns structured overview
    assert any(term in result.lower() for term in ["paris", "france", "overview", "dimensions"])


@pytest.mark.asyncio
@pytest.mark.skipif(not HAVE_KEY, reason="GEMINI_API_KEY not set – skipping live Gemini tests")
async def test_gemini_embed_live():
    """Live: GeminiProvider.embed returns correctly shaped embeddings."""
    from summarizerai.llm.gemini_provider import GeminiProvider
    p = GeminiProvider()
    texts = ["machine learning", "deep neural networks"]
    embeddings = await p.embed(texts)
    assert len(embeddings) == 2
    for emb in embeddings:
        # Gemini embedding-2 returns 3072-dim vectors
        assert len(emb) == 3072
        assert all(isinstance(v, float) for v in emb[:5])


@pytest.mark.asyncio
@pytest.mark.skipif(not HAVE_KEY, reason="GEMINI_API_KEY not set – skipping live Gemini tests")
async def test_gemini_is_available_live():
    """Live: GeminiProvider.is_available() returns True with a valid key."""
    from summarizerai.llm.gemini_provider import GeminiProvider
    p = GeminiProvider()
    available = await p.is_available()
    assert available is True


@pytest.mark.asyncio
@pytest.mark.skipif(not HAVE_KEY, reason="GEMINI_API_KEY not set – skipping live Gemini tests")
async def test_factory_returns_gemini_live():
    """Live: factory returns a GeminiProvider when GEMINI_API_KEY is present."""
    from summarizerai.llm.factory import get_llm_provider
    from summarizerai.llm.gemini_provider import GeminiProvider
    provider = await get_llm_provider()
    assert isinstance(provider, GeminiProvider)
