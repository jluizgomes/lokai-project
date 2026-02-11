"""Permission checking node."""

from typing import Any

import structlog

from lokai_agent.graph.state import AgentState
from lokai_agent.llm.router import LLMRouter

logger = structlog.get_logger()


async def permission_checker(state: AgentState, llm: LLMRouter) -> dict[str, Any]:
    """Check permissions for the planned actions."""
    action_plan = state.get("action_plan")

    if not action_plan:
        return {"pending_approval": None}

    # Check if confirmation is required
    if not action_plan.get("requires_confirmation"):
        return {"pending_approval": None}

    # Build approval request
    steps_summary = []
    for step in action_plan.get("steps", []):
        steps_summary.append(f"- {step.get('description', 'Unknown action')}")

    approval_request = {
        "id": f"approval_{hash(action_plan['summary'])}",
        "action": action_plan.get("summary", "Planned action"),
        "description": "\n".join(steps_summary),
        "risk_level": action_plan.get("total_risk_level", "low"),
        "steps": action_plan.get("steps", []),
        "confirmation_message": action_plan.get("confirmation_message"),
        "approved": None,  # Will be set by user response
        "denied": None,
    }

    logger.info(
        "Permission check required",
        risk_level=approval_request["risk_level"],
        steps=len(action_plan.get("steps", [])),
    )

    return {"pending_approval": approval_request}
