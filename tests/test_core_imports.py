"""Tests guarding the shared core package imports."""

from __future__ import annotations

from refi_calculator.core import calculations, models


def test_core_imports_without_gui_deps() -> None:
    """Ensure the core package loads without GUI dependencies."""

    assert hasattr(calculations, "analyze_refinance")
    assert hasattr(models, "LoanParams")


__all__ = ["test_core_imports_without_gui_deps"]
