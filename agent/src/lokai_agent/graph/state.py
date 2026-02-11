"""Agent state definition for LangGraph."""

from typing import Annotated, Any, TypedDict
from operator import add


class Message(TypedDict):
    """A message in the conversation."""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    tool_calls: list[dict[str, Any]] | None


class ToolCall(TypedDict):
    """A tool call."""
    id: str
    name: str
    parameters: dict[str, Any]
    status: str  # "pending", "running", "complete", "error"
    result: str | None
    error: str | None


class Intent(TypedDict):
    """Classified intent."""
    category: str
    confidence: float
    risk_level: str
    requires_approval: bool
    entities: dict[str, list[str]]
    explanation: str


class ActionPlan(TypedDict):
    """An action plan."""
    summary: str
    steps: list[dict[str, Any]]
    total_risk_level: str
    requires_confirmation: bool
    confirmation_message: str | None


class AgentState(TypedDict):
    """The state of the agent graph."""
    # Conversation
    messages: Annotated[list[Message], add]

    # Current processing
    current_message: str | None
    intent: Intent | None
    action_plan: ActionPlan | None

    # Tool execution
    tool_calls: list[ToolCall]
    pending_approval: dict[str, Any] | None

    # Context
    context: dict[str, Any]

    # Learning
    detected_patterns: list[dict[str, Any]]
    suggestions: list[dict[str, Any]]

    # Control flow
    next_node: str | None
    should_continue: bool
    error: str | None
