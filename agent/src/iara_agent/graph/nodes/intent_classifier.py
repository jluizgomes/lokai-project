"""Intent classification node."""

import json
from typing import Any

import structlog

from iara_agent.graph.state import AgentState, Intent
from iara_agent.prompts.intent import INTENT_CLASSIFICATION_PROMPT
from iara_agent.llm.router import LLMRouter

logger = structlog.get_logger()


async def intent_classifier(state: AgentState, llm: LLMRouter) -> dict[str, Any]:
    """Classify the user's intent from their message."""
    messages = state.get("messages", [])

    if not messages:
        return {"intent": None, "error": "No messages to classify"}

    # Get the latest user message
    user_message = None
    for msg in reversed(messages):
        if msg["role"] == "user":
            user_message = msg["content"]
            break

    if not user_message:
        return {"intent": None, "error": "No user message found"}

    # Format the classification prompt
    prompt = INTENT_CLASSIFICATION_PROMPT.format(message=user_message)

    try:
        # Get classification from LLM
        response = await llm.generate(prompt, use_system_prompt=False)

        # Parse JSON response
        # Find JSON in response (it might have extra text)
        json_start = response.find("{")
        json_end = response.rfind("}") + 1

        if json_start >= 0 and json_end > json_start:
            json_str = response[json_start:json_end]
            classification = json.loads(json_str)

            intent: Intent = {
                "category": classification.get("intent", "OTHER"),
                "confidence": float(classification.get("confidence", 0.5)),
                "risk_level": classification.get("risk_level", "low"),
                "requires_approval": classification.get("requires_approval", False),
                "entities": classification.get("entities", {}),
                "explanation": classification.get("explanation", ""),
            }

            logger.info(
                "Intent classified",
                intent=intent["category"],
                confidence=intent["confidence"],
            )

            return {
                "current_message": user_message,
                "intent": intent,
            }
        else:
            logger.warning("Could not parse intent classification response", response=response)
            return {
                "current_message": user_message,
                "intent": {
                    "category": "OTHER",
                    "confidence": 0.3,
                    "risk_level": "low",
                    "requires_approval": False,
                    "entities": {},
                    "explanation": "Could not parse classification",
                },
            }

    except json.JSONDecodeError as e:
        logger.error("JSON decode error in intent classification", error=str(e))
        return {
            "current_message": user_message,
            "intent": {
                "category": "OTHER",
                "confidence": 0.3,
                "risk_level": "low",
                "requires_approval": False,
                "entities": {},
                "explanation": f"JSON parse error: {e}",
            },
        }
    except Exception as e:
        logger.exception("Error in intent classification", error=str(e))
        return {
            "current_message": user_message,
            "intent": None,
            "error": str(e),
        }
