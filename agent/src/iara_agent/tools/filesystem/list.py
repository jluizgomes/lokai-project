"""File system list tool."""

import os
from typing import Any

import structlog

from iara_agent.tools.base import BaseTool, ToolResult

logger = structlog.get_logger()


class FileSystemListTool(BaseTool):
    """Tool for listing directory contents."""

    name = "filesystem_list"
    description = "List contents of a directory"
    risk_level = "low"
    requires_approval = False

    def __init__(self, allowed_directories: list[str] | None = None):
        self.allowed_directories = allowed_directories or []

    async def execute(
        self,
        path: str = ".",
        show_hidden: bool = False,
        max_entries: int = 100,
    ) -> ToolResult:
        """List directory contents.

        Args:
            path: Path to the directory to list
            show_hidden: Include hidden files (starting with .)
            max_entries: Maximum number of entries to return

        Returns:
            ToolResult with directory listing
        """
        try:
            # Expand user path
            expanded_path = os.path.expanduser(path)
            absolute_path = os.path.abspath(expanded_path)

            # Check if path is allowed
            if self.allowed_directories and not self._is_path_allowed(absolute_path):
                return ToolResult(
                    success=False,
                    error=f"Access denied: {path} is not in an allowed directory",
                )

            # Check if directory exists
            if not os.path.exists(absolute_path):
                return ToolResult(
                    success=False,
                    error=f"Directory not found: {path}",
                )

            # Check if it's a directory
            if not os.path.isdir(absolute_path):
                return ToolResult(
                    success=False,
                    error=f"Not a directory: {path}",
                )

            # List directory contents
            entries = os.listdir(absolute_path)

            # Filter hidden files if needed
            if not show_hidden:
                entries = [e for e in entries if not e.startswith(".")]

            # Sort entries
            entries.sort()

            # Limit entries
            total_count = len(entries)
            entries = entries[:max_entries]

            # Build detailed listing
            listing = []
            for entry in entries:
                entry_path = os.path.join(absolute_path, entry)
                try:
                    stat = os.stat(entry_path)
                    entry_info = {
                        "name": entry,
                        "is_dir": os.path.isdir(entry_path),
                        "is_file": os.path.isfile(entry_path),
                        "size": stat.st_size if os.path.isfile(entry_path) else None,
                    }
                except (PermissionError, OSError):
                    entry_info = {
                        "name": entry,
                        "is_dir": None,
                        "is_file": None,
                        "size": None,
                        "error": "Permission denied",
                    }
                listing.append(entry_info)

            # Format output
            output_lines = []
            for item in listing:
                prefix = "📁" if item.get("is_dir") else "📄"
                size_str = f" ({item['size']} bytes)" if item.get("size") else ""
                output_lines.append(f"{prefix} {item['name']}{size_str}")

            output = "\n".join(output_lines)

            if total_count > max_entries:
                output += f"\n\n... and {total_count - max_entries} more entries"

            logger.info("Directory listed", path=absolute_path, entries=len(listing))

            return ToolResult(
                success=True,
                output=output,
                metadata={
                    "path": absolute_path,
                    "count": len(listing),
                    "total_count": total_count,
                    "entries": listing,
                },
            )

        except PermissionError:
            return ToolResult(
                success=False,
                error=f"Permission denied: {path}",
            )
        except Exception as e:
            logger.exception("Error listing directory", path=path)
            return ToolResult(
                success=False,
                error=str(e),
            )

    def _is_path_allowed(self, path: str) -> bool:
        """Check if the path is within allowed directories."""
        if not self.allowed_directories:
            return True

        for allowed in self.allowed_directories:
            allowed_abs = os.path.abspath(os.path.expanduser(allowed))
            if path.startswith(allowed_abs):
                return True

        return False

    def get_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the directory to list",
                    "default": ".",
                },
                "show_hidden": {
                    "type": "boolean",
                    "description": "Include hidden files",
                    "default": False,
                },
                "max_entries": {
                    "type": "integer",
                    "description": "Maximum number of entries to return",
                    "default": 100,
                },
            },
        }
