from abc import ABC, abstractmethod
from typing import List, Optional

class LLMProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g. 'ollama', 'openai', 'fallback')."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider is online and responsive."""
        pass

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 2048) -> str:
        """Generate text completion."""
        pass

    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate vector embeddings for a list of text strings."""
        pass
