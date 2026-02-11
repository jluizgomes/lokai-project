"""Input validation utilities."""

import os
import re


def validate_path(
    path: str,
    allowed_directories: list[str] | None = None,
    must_exist: bool = False,
    must_be_file: bool = False,
    must_be_directory: bool = False,
) -> tuple[bool, str | None]:
    """Validate a file path.

    Args:
        path: The path to validate
        allowed_directories: List of allowed directory prefixes
        must_exist: Path must exist
        must_be_file: Path must be a file
        must_be_directory: Path must be a directory

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path:
        return False, "Path cannot be empty"

    # Expand user path
    expanded_path = os.path.expanduser(path)
    absolute_path = os.path.abspath(expanded_path)

    # Check for dangerous paths
    dangerous_paths = ["/", "/bin", "/sbin", "/usr", "/etc", "/var", "/sys", "/proc"]
    if absolute_path in dangerous_paths:
        return False, f"Access to system directory not allowed: {path}"

    # Check allowed directories
    if allowed_directories:
        is_allowed = False
        for allowed in allowed_directories:
            allowed_abs = os.path.abspath(os.path.expanduser(allowed))
            if absolute_path.startswith(allowed_abs):
                is_allowed = True
                break

        if not is_allowed:
            return False, f"Path not in allowed directories: {path}"

    # Check existence
    if must_exist and not os.path.exists(absolute_path):
        return False, f"Path does not exist: {path}"

    # Check type
    if must_be_file and os.path.exists(absolute_path) and not os.path.isfile(absolute_path):
        return False, f"Path is not a file: {path}"

    if must_be_directory and os.path.exists(absolute_path) and not os.path.isdir(absolute_path):
        return False, f"Path is not a directory: {path}"

    return True, None


def validate_command(
    command: str,
    allowed_commands: list[str] | None = None,
    blocked_commands: list[str] | None = None,
) -> tuple[bool, str | None]:
    """Validate a shell command.

    Args:
        command: The command to validate
        allowed_commands: List of allowed command patterns (regex)
        blocked_commands: List of blocked command patterns (regex)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not command:
        return False, "Command cannot be empty"

    # Check for dangerous patterns
    dangerous_patterns = [
        r"rm\s+(-rf?|--recursive)\s+/",  # rm -rf /
        r"mkfs",  # Format filesystem
        r"dd\s+if=.*of=/dev",  # Write to device
        r":[(][:][)]|fork\s*bomb",  # Fork bomb
        r"chmod\s+777\s+/",  # Dangerous chmod
        r">\s*/dev/sda",  # Write to disk
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return False, f"Dangerous command pattern blocked: {pattern}"

    # Check blocked commands
    if blocked_commands:
        for pattern in blocked_commands:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"Command blocked by policy: {pattern}"

    # Check allowed commands (if specified, command must match at least one)
    if allowed_commands:
        is_allowed = False
        for pattern in allowed_commands:
            if re.search(pattern, command, re.IGNORECASE):
                is_allowed = True
                break

        if not is_allowed:
            return False, "Command not in allowed list"

    return True, None


def validate_url(url: str) -> tuple[bool, str | None]:
    """Validate a URL.

    Args:
        url: The URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL cannot be empty"

    # Basic URL pattern
    url_pattern = r"^https?://[^\s<>\"{}|\\^`\[\]]+$"

    if not re.match(url_pattern, url):
        return False, "Invalid URL format"

    # Block local addresses (unless explicitly allowed)
    local_patterns = [
        r"^https?://localhost",
        r"^https?://127\.",
        r"^https?://0\.",
        r"^https?://\[::1\]",
    ]

    for pattern in local_patterns:
        if re.match(pattern, url, re.IGNORECASE):
            return False, "Local URLs not allowed by default"

    return True, None
