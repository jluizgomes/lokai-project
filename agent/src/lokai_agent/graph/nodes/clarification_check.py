"""Clarification check node."""

from typing import Any

import structlog

from lokai_agent.graph.state import AgentState
from lokai_agent.llm.router import LLMRouter

logger = structlog.get_logger()


async def clarification_check(state: AgentState, llm: LLMRouter) -> dict[str, Any]:
    """Check if clarification is needed and generate clarifying questions."""
    intent = state.get("intent")
    message = state.get("current_message", "")

    # If intent is already clear, no clarification needed
    if intent and intent.get("confidence", 0) >= 0.6:
        return {"next_node": "context_gatherer"}

    # Generate clarifying question based on the ambiguity
    if not intent or intent.get("category") == "CLARIFICATION_NEEDED":
        clarification_prompt = f"""The user said: "{message}"

I'm not sure what you'd like me to do. Please help me understand:

1. What specific action would you like me to perform?
2. Are there any files, directories, or applications involved?
3. What should the end result look like?

Please provide more details so I can assist you better."""

        return {
            "messages": [{
                "role": "assistant",
                "content": clarification_prompt,
                "tool_calls": None,
            }],
            "next_node": "response_generator",
        }

    # If confidence is low but we have some understanding
    if intent.get("confidence", 0) < 0.6:
        category = intent.get("category", "unknown action")
        clarification_prompt = f"""I think you want me to perform a {category.lower().replace('_', ' ')}, but I'm not entirely sure.

Based on your message: "{message}"

Could you confirm:
- Is this what you meant?
- Are there any specific details I should know?

Please clarify and I'll proceed with your request."""

        return {
            "messages": [{
                "role": "assistant",
                "content": clarification_prompt,
                "tool_calls": None,
            }],
            "next_node": "response_generator",
        }

    return {"next_node": "context_gatherer"}
