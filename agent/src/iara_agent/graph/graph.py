"""LangGraph graph definition for the IARA agent."""

from typing import Any

from langgraph.graph import StateGraph, END
import structlog

from iara_agent.graph.state import AgentState
from iara_agent.graph.nodes import (
    intent_classifier,
    context_gatherer,
    clarification_check,
    action_planner,
    permission_checker,
    action_executor,
    learning_phase,
    response_generator,
)
from iara_agent.llm.router import LLMRouter

logger = structlog.get_logger()


def create_agent_graph(llm_router: LLMRouter) -> StateGraph:
    """Create the agent state machine graph."""

    # Create the graph
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("intent_classifier", lambda state: intent_classifier(state, llm_router))
    graph.add_node("context_gatherer", lambda state: context_gatherer(state, llm_router))
    graph.add_node("clarification_check", lambda state: clarification_check(state, llm_router))
    graph.add_node("action_planner", lambda state: action_planner(state, llm_router))
    graph.add_node("permission_checker", lambda state: permission_checker(state, llm_router))
    graph.add_node("action_executor", lambda state: action_executor(state, llm_router))
    graph.add_node("learning_phase", lambda state: learning_phase(state, llm_router))
    graph.add_node("response_generator", lambda state: response_generator(state, llm_router))

    # Define edges
    graph.set_entry_point("intent_classifier")

    # From intent_classifier
    graph.add_conditional_edges(
        "intent_classifier",
        route_from_intent,
        {
            "clarification": "clarification_check",
            "context": "context_gatherer",
            "respond": "response_generator",
        }
    )

    # From clarification_check
    graph.add_conditional_edges(
        "clarification_check",
        route_from_clarification,
        {
            "ask": "response_generator",
            "continue": "context_gatherer",
        }
    )

    # From context_gatherer
    graph.add_edge("context_gatherer", "action_planner")

    # From action_planner
    graph.add_conditional_edges(
        "action_planner",
        route_from_planner,
        {
            "permission": "permission_checker",
            "execute": "action_executor",
            "respond": "response_generator",
        }
    )

    # From permission_checker
    graph.add_conditional_edges(
        "permission_checker",
        route_from_permission,
        {
            "approved": "action_executor",
            "denied": "response_generator",
            "pending": "response_generator",
        }
    )

    # From action_executor
    graph.add_conditional_edges(
        "action_executor",
        route_from_executor,
        {
            "learning": "learning_phase",
            "respond": "response_generator",
            "error": "response_generator",
        }
    )

    # From learning_phase
    graph.add_edge("learning_phase", "response_generator")

    # From response_generator
    graph.add_edge("response_generator", END)

    return graph.compile()


def route_from_intent(state: AgentState) -> str:
    """Route from intent classifier."""
    intent = state.get("intent")

    if not intent:
        return "clarification"

    if intent["category"] == "CLARIFICATION_NEEDED":
        return "clarification"

    if intent["category"] in ("GREETING", "QUESTION"):
        return "respond"

    if intent["confidence"] < 0.6:
        return "clarification"

    return "context"


def route_from_clarification(state: AgentState) -> str:
    """Route from clarification check."""
    # Check if we have enough information
    intent = state.get("intent")

    if intent and intent["category"] != "CLARIFICATION_NEEDED" and intent["confidence"] >= 0.6:
        return "continue"

    return "ask"


def route_from_planner(state: AgentState) -> str:
    """Route from action planner."""
    plan = state.get("action_plan")

    if not plan or not plan.get("steps"):
        return "respond"

    if plan.get("requires_confirmation"):
        return "permission"

    return "execute"


def route_from_permission(state: AgentState) -> str:
    """Route from permission checker."""
    pending = state.get("pending_approval")

    if pending is None:
        return "approved"

    if pending.get("approved"):
        return "approved"

    if pending.get("denied"):
        return "denied"

    return "pending"


def route_from_executor(state: AgentState) -> str:
    """Route from action executor."""
    error = state.get("error")

    if error:
        return "error"

    # Check if learning is enabled
    # For now, always go to learning phase
    return "learning"
