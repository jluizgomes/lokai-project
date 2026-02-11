"""Response generation node."""

from typing import Any

import structlog

from lokai_agent.graph.state import AgentState
from lokai_agent.llm.router import LLMRouter

logger = structlog.get_logger()


async def response_generator(state: AgentState, llm: LLMRouter) -> dict[str, Any]:
    """Generate the final response to the user."""
    intent = state.get("intent")
    action_plan = state.get("action_plan")
    tool_calls = state.get("tool_calls", [])
    pending_approval = state.get("pending_approval")
    error = state.get("error")
    messages = state.get("messages", [])

    # Check for existing assistant messages (from clarification)
    for msg in messages:
        if msg["role"] == "assistant" and msg.get("content"):
            # Already have a response from clarification
            return {"should_continue": False}

    # Handle error case
    if error:
        response = f"I encountered an error while processing your request:\n\n**Error**: {error}\n\nWould you like me to try a different approach?"
        return {
            "messages": [{
                "role": "assistant",
                "content": response,
                "tool_calls": None,
            }],
            "should_continue": False,
        }

    # Handle pending approval
    if pending_approval and pending_approval.get("approved") is None:
        steps_list = "\n".join([
            f"- {step.get('description', 'Action')}"
            for step in pending_approval.get("steps", [])
        ])

        response = f"""I'd like to perform the following actions:

**{pending_approval.get('action', 'Planned Action')}**

{steps_list}

**Risk Level**: {pending_approval.get('risk_level', 'unknown').upper()}

Do you approve these actions?"""

        return {
            "messages": [{
                "role": "assistant",
                "content": response,
                "tool_calls": None,
            }],
            "should_continue": False,
        }

    # Handle completed actions
    if tool_calls:
        successful = [tc for tc in tool_calls if tc.get("status") == "complete"]
        failed = [tc for tc in tool_calls if tc.get("status") == "error"]

        if successful and not failed:
            # All actions succeeded
            results = []
            for tc in successful:
                result = tc.get("result", "")
                if len(result) > 500:
                    result = result[:500] + "..."
                results.append(f"**{tc['name']}**: {result}")

            response = f"I've completed your request.\n\n" + "\n\n".join(results)

        elif failed and not successful:
            # All actions failed
            errors = [f"- {tc['name']}: {tc.get('error', 'Unknown error')}" for tc in failed]
            response = f"I wasn't able to complete your request due to errors:\n\n" + "\n".join(errors)

        else:
            # Mixed results
            response = "Here's what happened:\n\n"

            if successful:
                response += "**Completed:**\n"
                for tc in successful:
                    result = tc.get("result", "")
                    if len(result) > 200:
                        result = result[:200] + "..."
                    response += f"- {tc['name']}: {result}\n"

            if failed:
                response += "\n**Failed:**\n"
                for tc in failed:
                    response += f"- {tc['name']}: {tc.get('error', 'Unknown error')}\n"

        return {
            "messages": [{
                "role": "assistant",
                "content": response,
                "tool_calls": tool_calls,
            }],
            "should_continue": False,
        }

    # Handle simple responses (greetings, questions)
    if intent:
        category = intent.get("category", "")

        if category == "GREETING":
            response = "Hello! I'm Lokai, your desktop AI assistant. How can I help you today?"
        elif category == "QUESTION":
            # Generate an answer using the LLM
            message = state.get("current_message", "")
            response = await llm.generate(message)
        else:
            response = "I'm not sure how to help with that. Could you please provide more details?"
    else:
        response = "I'm here to help. What would you like me to do?"

    return {
        "messages": [{
            "role": "assistant",
            "content": response,
            "tool_calls": None,
        }],
        "should_continue": False,
    }
