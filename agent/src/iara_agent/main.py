"""IARA Agent main entry point - JSON-RPC server over stdio."""

import asyncio
import json
import sys
from typing import Any

import structlog
from pydantic import BaseModel

from iara_agent.config import settings
from iara_agent.graph.graph import create_agent_graph
from iara_agent.llm.router import LLMRouter

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class JsonRpcRequest(BaseModel):
    """JSON-RPC 2.0 request."""

    jsonrpc: str = "2.0"
    id: int
    method: str
    params: dict[str, Any] | None = None


class JsonRpcResponse(BaseModel):
    """JSON-RPC 2.0 response."""

    jsonrpc: str = "2.0"
    id: int
    result: Any | None = None
    error: dict[str, Any] | None = None


class JsonRpcStreamingToken(BaseModel):
    """Streaming token response."""

    jsonrpc: str = "2.0"
    id: int
    streaming: bool = True
    token: str


class JsonRpcStreamingComplete(BaseModel):
    """Streaming complete response."""

    jsonrpc: str = "2.0"
    id: int
    complete: bool = True
    result: str


class IaraAgent:
    """Main IARA agent class handling JSON-RPC communication."""

    def __init__(self) -> None:
        self.llm_router: LLMRouter | None = None
        self.graph: Any = None
        self._running = True

    async def initialize(self) -> None:
        """Initialize the agent components."""
        logger.info("Initializing IARA agent...")

        # Initialize LLM router
        self.llm_router = LLMRouter()
        await self.llm_router.initialize()

        # Create the agent graph
        self.graph = create_agent_graph(self.llm_router)

        logger.info("IARA agent initialized successfully")

    async def handle_request(self, request: JsonRpcRequest) -> JsonRpcResponse:
        """Handle a JSON-RPC request."""
        try:
            if request.method == "ping":
                return JsonRpcResponse(id=request.id, result={"status": "ok"})

            elif request.method == "process_message":
                params = request.params or {}
                message = params.get("message", "")
                streaming = params.get("streaming", False)

                if streaming:
                    # Handle streaming response
                    await self._process_message_streaming(request.id, message)
                    return JsonRpcResponse(id=request.id, result={"streaming": True})
                else:
                    result = await self._process_message(message)
                    return JsonRpcResponse(id=request.id, result=result)

            elif request.method == "execute_tool":
                params = request.params or {}
                tool_name = params.get("tool", "")
                tool_params = params.get("params", {})
                result = await self._execute_tool(tool_name, tool_params)
                return JsonRpcResponse(id=request.id, result=result)

            elif request.method == "cancel":
                # Cancel current operation
                return JsonRpcResponse(id=request.id, result={"cancelled": True})

            elif request.method == "get_context":
                context = await self._get_context()
                return JsonRpcResponse(id=request.id, result=context)

            else:
                return JsonRpcResponse(
                    id=request.id,
                    error={"code": -32601, "message": f"Method not found: {request.method}"},
                )

        except Exception as e:
            logger.exception("Error handling request", method=request.method)
            return JsonRpcResponse(
                id=request.id,
                error={"code": -32603, "message": str(e)},
            )

    async def _process_message(self, message: str) -> dict[str, Any]:
        """Process a user message and return the response."""
        if not self.graph:
            raise RuntimeError("Agent not initialized")

        # Run the agent graph
        state = {"messages": [{"role": "user", "content": message}]}
        result = await self.graph.ainvoke(state)

        # Extract the response
        response_message = result.get("messages", [])[-1] if result.get("messages") else None

        return {
            "content": response_message.get("content", "") if response_message else "",
            "tool_calls": result.get("tool_calls", []),
        }

    async def _process_message_streaming(self, request_id: int, message: str) -> None:
        """Process a message with streaming response."""
        if not self.llm_router:
            raise RuntimeError("Agent not initialized")

        full_response = ""

        try:
            async for token in self.llm_router.stream(message):
                full_response += token
                # Send streaming token
                streaming_response = JsonRpcStreamingToken(id=request_id, token=token)
                self._send_response(streaming_response.model_dump())

            # Send completion
            complete_response = JsonRpcStreamingComplete(id=request_id, result=full_response)
            self._send_response(complete_response.model_dump())

        except Exception as e:
            logger.exception("Error in streaming", error=str(e))
            error_response = JsonRpcResponse(
                id=request_id,
                error={"code": -32603, "message": str(e)},
            )
            self._send_response(error_response.model_dump())

    async def _execute_tool(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Execute a specific tool."""
        # Tool execution will be implemented with LangChain tools
        return {"executed": tool_name, "params": params, "result": "Tool execution pending"}

    async def _get_context(self) -> dict[str, Any]:
        """Get current context information."""
        import os
        import platform

        return {
            "current_directory": os.getcwd(),
            "platform": platform.system(),
            "hostname": platform.node(),
            "home_dir": os.path.expanduser("~"),
        }

    def _send_response(self, response: dict[str, Any]) -> None:
        """Send a JSON-RPC response to stdout."""
        print(json.dumps(response), flush=True)

    async def run(self) -> None:
        """Run the agent, reading from stdin and writing to stdout."""
        await self.initialize()

        logger.info("IARA agent ready, listening for requests...")

        while self._running:
            try:
                # Read a line from stdin
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)

                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                # Parse the JSON-RPC request
                try:
                    data = json.loads(line)
                    request = JsonRpcRequest(**data)
                except json.JSONDecodeError as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": f"Parse error: {e}"},
                    }
                    self._send_response(error_response)
                    continue

                # Handle the request
                response = await self.handle_request(request)
                self._send_response(response.model_dump())

            except Exception as e:
                logger.exception("Error in main loop", error=str(e))

    def stop(self) -> None:
        """Stop the agent."""
        self._running = False


async def main() -> None:
    """Main entry point."""
    agent = IaraAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
