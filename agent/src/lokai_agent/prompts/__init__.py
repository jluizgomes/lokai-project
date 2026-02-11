"""Prompt templates for the Lokai agent."""

from lokai_agent.prompts.system import SYSTEM_PROMPT
from lokai_agent.prompts.intent import INTENT_CLASSIFICATION_PROMPT
from lokai_agent.prompts.planning import ACTION_PLANNING_PROMPT

__all__ = ["SYSTEM_PROMPT", "INTENT_CLASSIFICATION_PROMPT", "ACTION_PLANNING_PROMPT"]
