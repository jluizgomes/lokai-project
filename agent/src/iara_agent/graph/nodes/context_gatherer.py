"""Context gathering node."""

import os
from typing import Any

import structlog

from iara_agent.graph.state import AgentState
from iara_agent.llm.router import LLMRouter

logger = structlog.get_logger()


async def context_gatherer(state: AgentState, llm: LLMRouter) -> dict[str, Any]:
    """Gather relevant context for the user's request."""
    intent = state.get("intent")

    context: dict[str, Any] = {
        "current_directory": os.getcwd(),
        "home_directory": os.path.expanduser("~"),
        "username": os.environ.get("USER", "unknown"),
    }

    if not intent:
        return {"context": context}

    entities = intent.get("entities", {})

    # Gather context based on intent category
    category = intent.get("category", "")

    if category.startswith("FILESYSTEM"):
        # Gather file system context
        paths = entities.get("paths", [])

        context["file_info"] = []
        for path in paths[:5]:  # Limit to 5 paths
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                stat = os.stat(expanded_path)
                context["file_info"].append({
                    "path": expanded_path,
                    "exists": True,
                    "is_file": os.path.isfile(expanded_path),
                    "is_dir": os.path.isdir(expanded_path),
                    "size": stat.st_size,
                })
            else:
                context["file_info"].append({
                    "path": expanded_path,
                    "exists": False,
                })

        # List current directory if no specific paths
        if not paths:
            try:
                context["directory_listing"] = os.listdir(os.getcwd())[:20]
            except PermissionError:
                context["directory_listing"] = []

    elif category == "GIT_OPERATION":
        # Check if we're in a git repository
        try:
            import subprocess
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            context["is_git_repo"] = result.returncode == 0

            if context["is_git_repo"]:
                # Get current branch
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                context["git_branch"] = result.stdout.strip()

                # Get status summary
                result = subprocess.run(
                    ["git", "status", "--short"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                context["git_status"] = result.stdout.strip()[:500]
        except Exception as e:
            logger.warning("Could not gather git context", error=str(e))
            context["is_git_repo"] = False

    elif category == "TERMINAL_COMMAND":
        # Gather shell environment context
        context["shell"] = os.environ.get("SHELL", "/bin/bash")
        context["path"] = os.environ.get("PATH", "").split(":")[:10]

    logger.info("Context gathered", category=category)

    return {"context": context}
