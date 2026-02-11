"""Action execution node."""

from typing import Any

import structlog

from lokai_agent.graph.state import AgentState, ToolCall
from lokai_agent.llm.router import LLMRouter

logger = structlog.get_logger()


async def action_executor(state: AgentState, llm: LLMRouter) -> dict[str, Any]:
    """Execute the planned actions."""
    action_plan = state.get("action_plan")
    pending_approval = state.get("pending_approval")

    if not action_plan:
        return {"tool_calls": [], "error": "No action plan to execute"}

    # Check if we were waiting for approval
    if pending_approval and not pending_approval.get("approved"):
        if pending_approval.get("denied"):
            return {
                "tool_calls": [],
                "messages": [{
                    "role": "assistant",
                    "content": "I understand. I won't proceed with that action. Is there something else I can help you with?",
                    "tool_calls": None,
                }],
            }
        # Still pending
        return {"tool_calls": []}

    # Execute each step in the plan
    tool_calls: list[ToolCall] = []
    results: list[str] = []

    for step in action_plan.get("steps", []):
        tool_name = step.get("tool", "")
        parameters = step.get("parameters", {})

        # Create tool call record
        tool_call: ToolCall = {
            "id": f"tool_{len(tool_calls)}_{tool_name}",
            "name": tool_name,
            "parameters": parameters,
            "status": "running",
            "result": None,
            "error": None,
        }
        tool_calls.append(tool_call)

        try:
            # Execute the tool
            result = await execute_tool(tool_name, parameters)
            tool_call["status"] = "complete"
            tool_call["result"] = result
            results.append(f"Step {step.get('step_number', '?')}: {result}")

            logger.info(
                "Tool executed",
                tool=tool_name,
                status="success",
            )

        except Exception as e:
            tool_call["status"] = "error"
            tool_call["error"] = str(e)

            logger.error(
                "Tool execution failed",
                tool=tool_name,
                error=str(e),
            )

            # Decide whether to continue or abort
            if step.get("risk_level") in ("medium", "high"):
                return {
                    "tool_calls": tool_calls,
                    "error": f"Critical step failed: {e}",
                }

    return {
        "tool_calls": tool_calls,
        "execution_results": results,
    }


async def execute_tool(tool_name: str, parameters: dict[str, Any]) -> str:
    """Execute a specific tool. This is a placeholder for actual tool implementations."""

    # Import tool implementations
    # For now, return placeholder results

    if tool_name == "filesystem_read":
        path = parameters.get("path", "")
        return await _execute_filesystem_read(path)

    elif tool_name == "filesystem_list":
        path = parameters.get("path", ".")
        return await _execute_filesystem_list(path)

    elif tool_name == "filesystem_write":
        path = parameters.get("path", "")
        content = parameters.get("content", "")
        return await _execute_filesystem_write(path, content)

    elif tool_name == "terminal_execute":
        command = parameters.get("command", "")
        return await _execute_terminal_command(command)

    else:
        return f"Tool '{tool_name}' not implemented yet"


async def _execute_filesystem_read(path: str) -> str:
    """Read a file."""
    import os

    expanded_path = os.path.expanduser(path)

    if not os.path.exists(expanded_path):
        raise FileNotFoundError(f"File not found: {path}")

    if not os.path.isfile(expanded_path):
        raise ValueError(f"Not a file: {path}")

    with open(expanded_path, "r") as f:
        content = f.read()

    return content[:10000]  # Limit to 10KB


async def _execute_filesystem_list(path: str) -> str:
    """List directory contents."""
    import os

    expanded_path = os.path.expanduser(path)

    if not os.path.exists(expanded_path):
        raise FileNotFoundError(f"Directory not found: {path}")

    if not os.path.isdir(expanded_path):
        raise ValueError(f"Not a directory: {path}")

    entries = os.listdir(expanded_path)
    return "\n".join(entries[:100])  # Limit to 100 entries


async def _execute_filesystem_write(path: str, content: str) -> str:
    """Write to a file."""
    import os

    expanded_path = os.path.expanduser(path)

    # Ensure directory exists
    os.makedirs(os.path.dirname(expanded_path), exist_ok=True)

    with open(expanded_path, "w") as f:
        f.write(content)

    return f"File written: {path}"


async def _execute_terminal_command(command: str) -> str:
    """Execute a terminal command."""
    import subprocess

    # Safety check - block dangerous commands
    dangerous_patterns = ["rm -rf /", "mkfs", "dd if=", ":(){", "fork bomb"]
    for pattern in dangerous_patterns:
        if pattern in command.lower():
            raise ValueError(f"Dangerous command blocked: {command}")

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30,
    )

    output = result.stdout
    if result.stderr:
        output += f"\nStderr: {result.stderr}"

    return output[:10000]  # Limit output
