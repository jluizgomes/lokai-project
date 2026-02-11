"""Base tool class for IARA tools."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class ToolResult(BaseModel):
    """Result from a tool execution."""
    success: bool
    output: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = {}


class BaseTool(ABC):
    """Base class for all IARA tools."""

    name: str
    description: str
    risk_level: str = "low"  # low, medium, high
    requires_approval: bool = False

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with the given parameters."""
        pass

    def get_schema(self) -> dict[str, Any]:
        """Get the JSON schema for this tool's parameters."""
        return {}

    def __str__(self) -> str:
        return f"Tool({self.name})"
