"""File system write tool."""

import os
from typing import Any

import structlog

from iara_agent.tools.base import BaseTool, ToolResult

logger = structlog.get_logger()


class FileSystemWriteTool(BaseTool):
    """Tool for writing files to the file system."""

    name = "filesystem_write"
    description = "Write content to a file on the file system"
    risk_level = "medium"
    requires_approval = True

    def __init__(self, allowed_directories: list[str] | None = None):
        self.allowed_directories = allowed_directories or []

    async def execute(
        self,
        path: str,
        content: str,
        encoding: str = "utf-8",
        create_dirs: bool = True,
        overwrite: bool = False,
    ) -> ToolResult:
        """Write content to a file.

        Args:
            path: Path to the file to write
            content: Content to write to the file
            encoding: File encoding (default: utf-8)
            create_dirs: Create parent directories if they don't exist
            overwrite: Overwrite existing file if it exists

        Returns:
            ToolResult with success status
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

            # Check if file exists and overwrite is not allowed
            if os.path.exists(absolute_path) and not overwrite:
                return ToolResult(
                    success=False,
                    error=f"File already exists: {path}. Set overwrite=True to replace.",
                )

            # Create parent directories if needed
            parent_dir = os.path.dirname(absolute_path)
            if parent_dir and not os.path.exists(parent_dir):
                if create_dirs:
                    os.makedirs(parent_dir, exist_ok=True)
                else:
                    return ToolResult(
                        success=False,
                        error=f"Parent directory does not exist: {parent_dir}",
                    )

            # Write the file
            with open(absolute_path, "w", encoding=encoding) as f:
                f.write(content)

            logger.info("File written successfully", path=absolute_path, size=len(content))

            return ToolResult(
                success=True,
                output=f"File written successfully: {path}",
                metadata={
                    "path": absolute_path,
                    "size": len(content),
                    "encoding": encoding,
                },
            )

        except PermissionError:
            return ToolResult(
                success=False,
                error=f"Permission denied: {path}",
            )
        except Exception as e:
            logger.exception("Error writing file", path=path)
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
                    "description": "Path to the file to write",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file",
                },
                "encoding": {
                    "type": "string",
                    "description": "File encoding",
                    "default": "utf-8",
                },
                "create_dirs": {
                    "type": "boolean",
                    "description": "Create parent directories if they don't exist",
                    "default": True,
                },
                "overwrite": {
                    "type": "boolean",
                    "description": "Overwrite existing file if it exists",
                    "default": False,
                },
            },
            "required": ["path", "content"],
        }
