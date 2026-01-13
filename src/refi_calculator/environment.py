"""Utilities for loading environment variables from .env files."""

from __future__ import annotations

import os
from collections.abc import Iterable
from logging import getLogger
from pathlib import Path

logger = getLogger(__name__)


def _strip_quotes(value: str) -> str:
    """Remove matching wrapping quotes from a string.

    Args:
        value: The string to strip quotes from.

    Returns:
        The unquoted string.
    """
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]

    return value


def _parse_dotenv_line(line: str) -> tuple[str, str] | None:
    """Parse a single line from a .env file into a key/value pair.

    Args:
        line: The line to parse.

    Returns:
        A tuple of (key, value) if the line is valid, otherwise None.
    """
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    if stripped.startswith("export "):
        stripped = stripped[len("export ") :].strip()

    if "=" not in stripped:
        logger.warning("Skipping malformed .env line: %s", line)
        return None

    key, value = stripped.split("=", 1)
    key = key.strip()
    value = _strip_quotes(value.strip())

    if not key:
        logger.warning("Skipping .env entry with missing key: %s", line)
        return None

    return key, value


def _iter_lines(content: str) -> Iterable[str]:
    """Yield lines from .env file content.

    Args:
        content: The content of the .env file.

    Yields:
        Lines from the content.
    """
    return (line for line in content.splitlines())


def load_dotenv(
    dotenv_path: Path | str | None = None,
    *,
    override_existing: bool = False,
) -> dict[str, str]:
    """Load environment variables from a .env file into the process environment.

    Args:
        dotenv_path: Path to the .env file. Defaults to ``Path.cwd() / ".env"``.
        override_existing: Whether to overwrite existing environment variables.

    Returns:
        A mapping of keys that were set from the .env file to their values.

    Raises:
        OSError: If the .env file could not be read.
    """
    path = Path(dotenv_path) if dotenv_path is not None else Path.cwd() / ".env"
    if not path.exists():
        logger.debug("No .env file found at %s", path)
        return {}

    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        logger.exception("Failed to read .env file at %s", path)
        raise

    loaded: dict[str, str] = {}
    for line in _iter_lines(content):
        pair = _parse_dotenv_line(line)
        if pair is None:
            continue

        key, value = pair
        if override_existing or key not in os.environ:
            os.environ[key] = value
            loaded[key] = value
        else:
            logger.debug("Skipping existing environment variable %s", key)

    logger.debug("Loaded %d environment variables from %s", len(loaded), path)
    return loaded


__all__ = [
    "load_dotenv",
]

__description__ = """
Utilities for loading environment variables from .env files.
"""
