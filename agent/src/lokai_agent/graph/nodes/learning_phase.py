"""Learning phase node."""

from typing import Any

import structlog

from lokai_agent.graph.state import AgentState
from lokai_agent.llm.router import LLMRouter

logger = structlog.get_logger()


async def learning_phase(state: AgentState, llm: LLMRouter) -> dict[str, Any]:
    """Learn from the completed action for future suggestions."""
    intent = state.get("intent")
    action_plan = state.get("action_plan")
    tool_calls = state.get("tool_calls", [])
    context = state.get("context", {})

    if not action_plan or not tool_calls:
        return {"detected_patterns": [], "suggestions": []}

    # Extract successful actions for pattern learning
    successful_actions = [
        tc for tc in tool_calls
        if tc.get("status") == "complete"
    ]

    if not successful_actions:
        return {"detected_patterns": [], "suggestions": []}

    # Build pattern data
    pattern_data = {
        "intent": intent.get("category") if intent else None,
        "context": {
            "directory": context.get("current_directory"),
            "is_git_repo": context.get("is_git_repo"),
        },
        "actions": [
            {
                "tool": tc["name"],
                "parameters": tc["parameters"],
            }
            for tc in successful_actions
        ],
    }

    # Store pattern for future learning
    # This would typically go to the database
    detected_patterns = [{
        "pattern_id": f"pattern_{hash(str(pattern_data))}",
        "pattern_type": "action_sequence",
        "trigger": state.get("current_message", ""),
        "actions": pattern_data["actions"],
        "context": pattern_data["context"],
        "confidence": 0.5,  # Initial confidence
        "frequency": 1,
    }]

    logger.info(
        "Pattern learned",
        intent=pattern_data.get("intent"),
        actions_count=len(successful_actions),
    )

    return {
        "detected_patterns": detected_patterns,
        "suggestions": [],  # Suggestions would be generated based on pattern matching
    }
