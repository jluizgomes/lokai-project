"""File system read tool."""

import os
from typing import Any

import structlog

from iara_agent.tools.base import BaseTool, ToolResult

logger = structlog.get_logger()


class FileSystemReadTool(BaseTool):
    """Tool for reading files from the file system."""

    name = "filesystem_read"
    description = "Read the contents of a file from the file system"
    risk_level = "low"
    requires_approval = False

    def __init__(self, allowed_directories: list[str] | None = None):
        self.allowed_directories = allowed_directories or []

    async def execute(
        self,
        path: str,
        encoding: str = "utf-8",
        max_size: int = 1024 * 1024,  # 1MB default
    ) -> ToolResult:
        """Read a file from the file system.

        Args:
            path: Path to the file to read
            encoding: File encoding (default: utf-8)
            max_size: Maximum file size to read in bytes

        Returns:
            ToolResult with file contents or error
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

            # Check if file exists
            if not os.path.exists(absolute_path):
                return ToolResult(
                    success=False,
                    error=f"File not found: {path}",
                )

            # Check if it's a file
            if not os.path.isfile(absolute_path):
                return ToolResult(
                    success=False,
                    error=f"Not a file: {path}",
                )

            # Check file size
            file_size = os.path.getsize(absolute_path)
            if file_size > max_size:
                return ToolResult(
                    success=False,
                    error=f"File too large: {file_size} bytes (max: {max_size})",
                )

            # Read the file
            with open(absolute_path, "r", encoding=encoding) as f:
                content = f.read()

            logger.info("File read successfully", path=absolute_path, size=len(content))

            return ToolResult(
                success=True,
                output=content,
                metadata={
                    "path": absolute_path,
                    "size": file_size,
                    "encoding": encoding,
                },
            )

        except UnicodeDecodeError as e:
            return ToolResult(
                success=False,
                error=f"Encoding error: {e}. Try a different encoding.",
            )
        except PermissionError:
            return ToolResult(
                success=False,
                error=f"Permission denied: {path}",
            )
        except Exception as e:
            logger.exception("Error reading file", path=path)
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
                    "description": "Path to the file to read",
                },
                "encoding": {
                    "type": "string",
                    "description": "File encoding",
                    "default": "utf-8",
                },
                "max_size": {
                    "type": "integer",
                    "description": "Maximum file size in bytes",
                    "default": 1048576,
                },
            },
            "required": ["path"],
        }
