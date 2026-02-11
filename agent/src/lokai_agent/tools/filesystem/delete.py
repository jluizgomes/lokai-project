"""File system delete tool."""

import os
import shutil
from typing import Any

import structlog

from lokai_agent.tools.base import BaseTool, ToolResult

logger = structlog.get_logger()


class FileSystemDeleteTool(BaseTool):
    """Tool for deleting files from the file system."""

    name = "filesystem_delete"
    description = "Delete a file or directory from the file system"
    risk_level = "high"
    requires_approval = True

    def __init__(self, allowed_directories: list[str] | None = None):
        self.allowed_directories = allowed_directories or []

    async def execute(
        self,
        path: str,
        recursive: bool = False,
    ) -> ToolResult:
        """Delete a file or directory.

        Args:
            path: Path to the file or directory to delete
            recursive: For directories, delete recursively

        Returns:
            ToolResult with success status
        """
        try:
            # Expand user path
            expanded_path = os.path.expanduser(path)
            absolute_path = os.path.abspath(expanded_path)

            # Safety checks
            dangerous_paths = ["/", "/home", "/Users", os.path.expanduser("~")]
            if absolute_path in dangerous_paths:
                return ToolResult(
                    success=False,
                    error=f"Dangerous operation: Cannot delete {path}",
                )

            # Check if path is allowed
            if self.allowed_directories and not self._is_path_allowed(absolute_path):
                return ToolResult(
                    success=False,
                    error=f"Access denied: {path} is not in an allowed directory",
                )

            # Check if path exists
            if not os.path.exists(absolute_path):
                return ToolResult(
                    success=False,
                    error=f"Path not found: {path}",
                )

            # Delete file or directory
            if os.path.isfile(absolute_path):
                os.remove(absolute_path)
                logger.info("File deleted", path=absolute_path)
            elif os.path.isdir(absolute_path):
                if recursive:
                    shutil.rmtree(absolute_path)
                    logger.info("Directory deleted recursively", path=absolute_path)
                else:
                    try:
                        os.rmdir(absolute_path)
                        logger.info("Empty directory deleted", path=absolute_path)
                    except OSError:
                        return ToolResult(
                            success=False,
                            error=f"Directory not empty: {path}. Use recursive=True to delete.",
                        )
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown path type: {path}",
                )

            return ToolResult(
                success=True,
                output=f"Deleted: {path}",
                metadata={"path": absolute_path},
            )

        except PermissionError:
            return ToolResult(
                success=False,
                error=f"Permission denied: {path}",
            )
        except Exception as e:
            logger.exception("Error deleting path", path=path)
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
                    "description": "Path to the file or directory to delete",
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Delete directory recursively",
                    "default": False,
                },
            },
            "required": ["path"],
        }
