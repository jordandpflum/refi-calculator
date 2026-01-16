"""Tests for the environment utilities."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from refi_calculator.environment import (
    _parse_dotenv_line,
    _strip_quotes,
    load_dotenv,
)


def test_load_dotenv_reads_values(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure values from a .env file populate ``os.environ``.

    Args:
        tmp_path: Temporary directory for test files.
        monkeypatch: Pytest fixture for modifying environment variables.
    """

    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text(
        """
# comment should be ignored
FIRST=first
export QUOTED="quoted value"
SPACED='spaced value'
""",
        encoding="utf-8",
    )

    monkeypatch.delenv("FIRST", raising=False)
    monkeypatch.delenv("QUOTED", raising=False)
    monkeypatch.delenv("SPACED", raising=False)

    loaded = load_dotenv(dotenv_path=dotenv_path)

    assert loaded == {"FIRST": "first", "QUOTED": "quoted value", "SPACED": "spaced value"}
    assert os.environ["FIRST"] == "first"
    assert os.environ["QUOTED"] == "quoted value"
    assert os.environ["SPACED"] == "spaced value"


def test_load_dotenv_respects_existing_values(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Existing environment values are preserved unless overridden.

    Args:
        tmp_path: Temporary directory for test files.
        monkeypatch: Pytest fixture for modifying environment variables.
    """

    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text("EXISTING=from-file\n", encoding="utf-8")

    monkeypatch.setenv("EXISTING", "original")

    loaded = load_dotenv(dotenv_path=dotenv_path)

    assert loaded == {}
    assert os.environ["EXISTING"] == "original"

    loaded_override = load_dotenv(dotenv_path=dotenv_path, override_existing=True)

    assert loaded_override == {"EXISTING": "from-file"}
    assert os.environ["EXISTING"] == "from-file"


def test_load_dotenv_returns_empty_when_missing(tmp_path: Path) -> None:
    """Missing .env files do nothing and return an empty mapping.

    Args:
        tmp_path: Temporary directory for test files.
    """

    missing_path = tmp_path / ".env"

    assert not missing_path.exists()
    assert load_dotenv(dotenv_path=missing_path) == {}


def test_strip_quotes_drops_wrapping_chars() -> None:
    """Only matching wrapping quotes should be stripped."""

    assert _strip_quotes('"quoted value"') == "quoted value"
    assert _strip_quotes("'another quoted value'") == "another quoted value"
    assert _strip_quotes("'mismatched\"") == "'mismatched\""


def test_parse_dotenv_line_handles_exports_and_malformed_lines() -> None:
    """Export prefixes and invalid lines are handled gracefully."""

    assert _parse_dotenv_line("export KEY=value") == ("KEY", "value")
    assert _parse_dotenv_line("KEY=value=with=equals") == ("KEY", "value=with=equals")
    assert _parse_dotenv_line("   # comment  ") is None
    assert _parse_dotenv_line("MISSING_EQUALS") is None
    assert _parse_dotenv_line("=novalue") is None


def test_load_dotenv_raises_when_file_unreadable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """OSError while reading the .env file propagates.

    Args:
        tmp_path: Temporary directory for test files.
        monkeypatch: Pytest fixture for modifying behavior.
    """

    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text("", encoding="utf-8")

    original_read_text = Path.read_text

    def _fail_read(self: Path, *args, **kwargs) -> str:
        if self == dotenv_path:
            raise OSError("boom")
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", _fail_read)

    with pytest.raises(OSError):
        load_dotenv(dotenv_path=dotenv_path)


__all__ = [
    "test_load_dotenv_reads_values",
    "test_load_dotenv_respects_existing_values",
    "test_load_dotenv_returns_empty_when_missing",
    "test_strip_quotes_drops_wrapping_chars",
    "test_parse_dotenv_line_handles_exports_and_malformed_lines",
    "test_load_dotenv_raises_when_file_unreadable",
]
