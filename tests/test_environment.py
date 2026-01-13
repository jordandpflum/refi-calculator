"""Tests for the environment utilities."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from refi_calculator.environment import load_dotenv


def test_load_dotenv_reads_values(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure values from a .env file populate ``os.environ``."""

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


def test_load_dotenv_respects_existing_values(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Existing environment values are preserved unless overridden."""

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
    """Missing .env files do nothing and return an empty mapping."""

    missing_path = tmp_path / ".env"

    assert not missing_path.exists()
    assert load_dotenv(dotenv_path=missing_path) == {}


__all__ = ["test_load_dotenv_reads_values", "test_load_dotenv_respects_existing_values"]
