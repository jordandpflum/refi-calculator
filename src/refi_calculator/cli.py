"""Command-line launcher for the refinance calculator app."""

from __future__ import annotations

import argparse
import os
from importlib.metadata import PackageNotFoundError, version
from logging import basicConfig, getLogger

from refi_calculator.environment import load_dotenv
from refi_calculator.gui.app import main as launch_gui

logger = getLogger(__name__)


def _get_distribution_version() -> str | None:
    if env_version := os.environ.get("REFI_VERSION"):
        return env_version
    try:
        return version("refi-calculator")
    except PackageNotFoundError:
        logger.debug("Unable to determine installed version.")
        return None


def _create_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser.

    Returns:
        A configured parser for handling CLI options.
    """
    parser = argparse.ArgumentParser(
        prog="refi-calculator",
        description="Launch the refinance calculator UI.",
    )
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=_get_distribution_version() or "refi-calculator (development build)",
        help="Show version information and exit.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    """Launch the refinance calculator UI.

    Args:
        argv: Optional argument list; defaults to ``sys.argv`` when ``None``.
    """
    parser = _create_parser()
    parser.parse_args(argv)
    load_dotenv()
    basicConfig(level="INFO")
    logger.info("Launching Refi-Calculator UI")
    launch_gui()


__all__ = ["main"]

__description__ = """
Command-line launcher for the refinance calculator UI.
"""
