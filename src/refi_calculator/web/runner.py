"""Helper that launches the Streamlit web placeholder through the Streamlit CLI."""

from __future__ import annotations

import sys
from pathlib import Path

from streamlit.web import cli as stcli


def main() -> None:
    """Run the Streamlit app via the CLI to ensure a proper ScriptRunContext."""
    script_path = Path(__file__).resolve().parent / "app.py"
    sys.argv = ["streamlit", "run", str(script_path)]
    stcli.main()


__all__ = ["main"]

__description__ = """
Entrypoint that runs the refinance calculator Streamlit app with the official CLI.
"""
