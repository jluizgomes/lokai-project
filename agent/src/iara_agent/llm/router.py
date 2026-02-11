"""LLM Router for managing multiple LLM providers with fallback."""

from collections.abc import AsyncIterator
from typing import Any

import structlog

from iara_agent.llm.ollama_client import OllamaClient
from iara_agent.llm.openai_client import OpenAIClient
from iara_agent.prompts.system import SYSTEM_PROMPT

logger = structlog.get_logger()


class LLMRouter:
    """Router for managing LLM providers with fallback chain."""

    def __init__(self) -> None:
        self.ollama = OllamaClient()
        self.openai = OpenAIClient()
        self._primary_available = False
        self._fallback_available = False

    async def initialize(self) -> None:
        """Initialize all LLM providers."""
        # Try to initialize Ollama (primary)
        try:
            await self.ollama.initialize()
            self._primary_available = True
            logger.info("Primary LLM (Ollama) initialized")
        except Exception as e:
            logger.warning("Failed to initialize Ollama", error=str(e))
            self._primary_available = False

        # Try to initialize OpenAI (fallback)
        try:
            await self.openai.initialize()
            self._fallback_available = self.openai.available
            if self._fallback_available:
                logger.info("Fallback LLM (OpenAI) initialized")
        except Exception as e:
            logger.warning("Failed to initialize OpenAI fallback", error=str(e))
            self._fallback_available = False

        if not self._primary_available and not self._fallback_available:
            raise RuntimeError("No LLM providers available")

    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        use_system_prompt: bool = True,
    ) -> str:
        """Generate a response using available LLM with fallback."""
        effective_system = system or (SYSTEM_PROMPT if use_system_prompt else None)

        if self._primary_available:
            try:
                return await self.ollama.generate(prompt, effective_system)
            except Exception as e:
                logger.warning("Ollama generation failed, trying fallback", error=str(e))

        if self._fallback_available:
            try:
                return await self.openai.generate(prompt, effective_system)
            except Exception as e:
                logger.error("OpenAI fallback failed", error=str(e))
                raise

        raise RuntimeError("No LLM providers available for generation")

    async def stream(
        self,
        prompt: str,
        system: str | None = None,
        use_system_prompt: bool = True,
    ) -> AsyncIterator[str]:
        """Stream a response using available LLM with fallback."""
        effective_system = system or (SYSTEM_PROMPT if use_system_prompt else None)

        if self._primary_available:
            try:
                async for token in self.ollama.stream(prompt, effective_system):
                    yield token
                return
            except Exception as e:
                logger.warning("Ollama streaming failed, trying fallback", error=str(e))

        if self._fallback_available:
            try:
                async for token in self.openai.stream(prompt, effective_system):
                    yield token
                return
            except Exception as e:
                logger.error("OpenAI fallback streaming failed", error=str(e))
                raise

        raise RuntimeError("No LLM providers available for streaming")

    async def embed(self, text: str) -> list[float]:
        """Generate embeddings (Ollama only for now)."""
        if not self._primary_available:
            raise RuntimeError("Ollama not available for embeddings")

        return await self.ollama.embed(text)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        if not self._primary_available:
            raise RuntimeError("Ollama not available for embeddings")

        return await self.ollama.embed_batch(texts)

    @property
    def llm(self) -> Any:
        """Get the LangChain LLM instance from Ollama."""
        if self._primary_available:
            return self.ollama.llm
        raise RuntimeError("No LLM available")

    @property
    def embeddings(self) -> Any:
        """Get the LangChain embeddings instance from Ollama."""
        if self._primary_available:
            return self.ollama.embeddings
        raise RuntimeError("No embeddings available")

    async def close(self) -> None:
        """Close all client connections."""
        await self.ollama.close()
        await self.openai.close()
