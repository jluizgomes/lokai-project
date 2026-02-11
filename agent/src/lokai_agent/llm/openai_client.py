"""OpenAI client for fallback LLM inference."""

from collections.abc import AsyncIterator
from typing import Any

import httpx
import structlog

from lokai_agent.config import settings

logger = structlog.get_logger()


class OpenAIClient:
    """Client for OpenAI API as fallback."""

    def __init__(self) -> None:
        self.api_key = settings.openai_api_key
        self.base_url = "https://api.openai.com/v1"
        self.model = "gpt-3.5-turbo"
        self._client: httpx.AsyncClient | None = None

    async def initialize(self) -> None:
        """Initialize the client."""
        if not self.api_key:
            logger.warning("OpenAI API key not set, fallback will not be available")
            return

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )
        logger.info("OpenAI client initialized")

    @property
    def available(self) -> bool:
        """Check if OpenAI is available."""
        return self._client is not None and self.api_key is not None

    async def generate(self, prompt: str, system: str | None = None) -> str:
        """Generate a response from OpenAI."""
        if not self._client:
            raise RuntimeError("OpenAI client not initialized")

        messages: list[dict[str, str]] = []

        if system:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        response = await self._client.post(
            "/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "temperature": settings.temperature,
                "max_tokens": settings.max_tokens,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def stream(self, prompt: str, system: str | None = None) -> AsyncIterator[str]:
        """Stream a response from OpenAI."""
        if not self._client:
            raise RuntimeError("OpenAI client not initialized")

        messages: list[dict[str, str]] = []

        if system:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        async with self._client.stream(
            "POST",
            "/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "temperature": settings.temperature,
                "max_tokens": settings.max_tokens,
                "stream": True,
            },
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    import json
                    data = json.loads(data_str)
                    if data["choices"][0]["delta"].get("content"):
                        yield data["choices"][0]["delta"]["content"]

    async def close(self) -> None:
        """Close the client connection."""
        if self._client:
            await self._client.aclose()
            self._client = None
