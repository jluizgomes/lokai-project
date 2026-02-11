"""Input sanitization utilities."""

import re
import os


def sanitize_path(path: str) -> str:
    """Sanitize a file path.

    Args:
        path: The path to sanitize

    Returns:
        Sanitized path
    """
    # Remove null bytes
    path = path.replace("\x00", "")

    # Normalize path
    path = os.path.normpath(path)

    # Remove dangerous sequences
    dangerous_patterns = [
        r"\.\./",  # Parent directory traversal
        r"//+",    # Multiple slashes
        r"[<>:\"|?*]",  # Invalid characters on some systems
    ]

    for pattern in dangerous_patterns:
        path = re.sub(pattern, "", path)

    return path


def sanitize_command(command: str) -> str:
    """Sanitize a shell command.

    Args:
        command: The command to sanitize

    Returns:
        Sanitized command
    """
    # Remove null bytes
    command = command.replace("\x00", "")

    # Remove dangerous command chains
    dangerous_patterns = [
        r";\s*rm\s+-rf\s+/",
        r";\s*rm\s+-rf\s+\*",
        r"\|\s*sh",
        r"\|\s*bash",
        r"`[^`]*`",  # Backtick command substitution
        r"\$\([^)]*\)",  # $() command substitution
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            raise ValueError(f"Dangerous command pattern detected: {pattern}")

    return command


def sanitize_output(output: str, max_length: int = 10000) -> str:
    """Sanitize command output.

    Args:
        output: The output to sanitize
        max_length: Maximum length of output

    Returns:
        Sanitized output
    """
    # Remove null bytes
    output = output.replace("\x00", "")

    # Truncate if too long
    if len(output) > max_length:
        output = output[:max_length] + "\n... (output truncated)"

    return output
