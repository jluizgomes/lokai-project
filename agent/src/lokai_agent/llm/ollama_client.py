"""Ollama LLM client for local model inference."""

from collections.abc import AsyncIterator
from typing import Any

import httpx
import structlog
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings

from lokai_agent.config import settings

logger = structlog.get_logger()


class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self) -> None:
        self.base_url = settings.ollama_host
        self.model = settings.ollama_model
        self.embedding_model = settings.ollama_embedding_model
        self._client: httpx.AsyncClient | None = None
        self._llm: Ollama | None = None
        self._embeddings: OllamaEmbeddings | None = None

    async def initialize(self) -> None:
        """Initialize the client and verify connection."""
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=60.0)

        # Check if Ollama is available
        if not await self.health_check():
            raise ConnectionError(f"Cannot connect to Ollama at {self.base_url}")

        # Initialize LangChain components
        self._llm = Ollama(
            base_url=self.base_url,
            model=self.model,
            temperature=settings.temperature,
        )

        self._embeddings = OllamaEmbeddings(
            base_url=self.base_url,
            model=self.embedding_model,
        )

        logger.info("Ollama client initialized", model=self.model, host=self.base_url)

    async def health_check(self) -> bool:
        """Check if Ollama is available."""
        try:
            if not self._client:
                async with httpx.AsyncClient(base_url=self.base_url, timeout=5.0) as client:
                    response = await client.get("/api/tags")
                    return response.status_code == 200
            else:
                response = await self._client.get("/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.warning("Ollama health check failed", error=str(e))
            return False

    async def list_models(self) -> list[dict[str, Any]]:
        """List available models."""
        if not self._client:
            raise RuntimeError("Client not initialized")

        response = await self._client.get("/api/tags")
        response.raise_for_status()
        data = response.json()
        return data.get("models", [])

    async def generate(self, prompt: str, system: str | None = None) -> str:
        """Generate a response from the model."""
        if not self._client:
            raise RuntimeError("Client not initialized")

        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        if system:
            payload["system"] = system

        response = await self._client.post("/api/generate", json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")

    async def stream(self, prompt: str, system: str | None = None) -> AsyncIterator[str]:
        """Stream a response from the model."""
        if not self._client:
            raise RuntimeError("Client not initialized")

        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
        }

        if system:
            payload["system"] = system

        async with self._client.stream("POST", "/api/generate", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    import json
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]

    async def embed(self, text: str) -> list[float]:
        """Generate embeddings for text."""
        if not self._client:
            raise RuntimeError("Client not initialized")

        payload = {
            "model": self.embedding_model,
            "prompt": text,
        }

        response = await self._client.post("/api/embeddings", json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("embedding", [])

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = []
        for text in texts:
            embedding = await self.embed(text)
            embeddings.append(embedding)
        return embeddings

    @property
    def llm(self) -> Ollama:
        """Get the LangChain LLM instance."""
        if not self._llm:
            raise RuntimeError("Client not initialized")
        return self._llm

    @property
    def embeddings(self) -> OllamaEmbeddings:
        """Get the LangChain embeddings instance."""
        if not self._embeddings:
            raise RuntimeError("Client not initialized")
        return self._embeddings

    async def close(self) -> None:
        """Close the client connection."""
        if self._client:
            await self._client.aclose()
            self._client = None
