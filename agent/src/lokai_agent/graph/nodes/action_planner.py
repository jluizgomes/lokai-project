"""Action planning node."""

import json
from typing import Any

import structlog

from lokai_agent.graph.state import AgentState, ActionPlan
from lokai_agent.prompts.planning import ACTION_PLANNING_PROMPT
from lokai_agent.llm.router import LLMRouter

logger = structlog.get_logger()


async def action_planner(state: AgentState, llm: LLMRouter) -> dict[str, Any]:
    """Create an action plan based on the user's intent."""
    intent = state.get("intent")
    context = state.get("context", {})
    message = state.get("current_message", "")

    if not intent:
        return {"action_plan": None, "error": "No intent to plan for"}

    # Format the planning prompt
    prompt = ACTION_PLANNING_PROMPT.format(
        message=message,
        intent=intent.get("category", ""),
        entities=json.dumps(intent.get("entities", {})),
        current_directory=context.get("current_directory", "unknown"),
        recent_files=json.dumps(context.get("directory_listing", [])[:5]),
    )

    try:
        response = await llm.generate(prompt, use_system_prompt=False)

        # Parse JSON response
        json_start = response.find("{")
        json_end = response.rfind("}") + 1

        if json_start >= 0 and json_end > json_start:
            json_str = response[json_start:json_end]
            plan_data = json.loads(json_str)

            action_plan: ActionPlan = {
                "summary": plan_data.get("plan_summary", ""),
                "steps": plan_data.get("steps", []),
                "total_risk_level": plan_data.get("total_risk_level", "low"),
                "requires_confirmation": plan_data.get("requires_user_confirmation", False),
                "confirmation_message": plan_data.get("confirmation_message"),
            }

            # Override confirmation based on risk level
            if action_plan["total_risk_level"] in ("medium", "high"):
                action_plan["requires_confirmation"] = True

            # Check individual steps for approval requirements
            for step in action_plan["steps"]:
                if step.get("requires_approval", False):
                    action_plan["requires_confirmation"] = True
                    break

            logger.info(
                "Action plan created",
                steps=len(action_plan["steps"]),
                risk=action_plan["total_risk_level"],
            )

            return {"action_plan": action_plan}
        else:
            logger.warning("Could not parse action plan response", response=response)
            return {"action_plan": None}

    except json.JSONDecodeError as e:
        logger.error("JSON decode error in action planning", error=str(e))
        return {"action_plan": None, "error": f"JSON parse error: {e}"}
    except Exception as e:
        logger.exception("Error in action planning", error=str(e))
        return {"action_plan": None, "error": str(e)}
