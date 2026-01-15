"""Helpers for formatting values displayed in the Streamlit interface."""

from __future__ import annotations

from logging import getLogger

logger = getLogger(__name__)


def format_currency(value: float) -> str:
    """Format a numeric value as whole-dollar currency.

    Args:
        value: Numeric value to format.

    Returns:
        Dollar-formatted string without decimal cents.
    """
    return f"${value:,.0f}"


def format_optional_currency(value: float | None) -> str:
    """Format an optional numeric value as currency, falling back to N/A.

    Args:
        value: Optional numeric value.

    Returns:
        Formatted currency or "N/A" when no value is present.
    """
    if value is None:
        return "N/A"
    return format_currency(value)


def format_months(value: float | int | None) -> str:
    """Describe a month count alongside its equivalent in years.

    Args:
        value: Number of months to convert.

    Returns:
        Human-friendly string or "N/A" when value is missing.
    """
    if value is None:
        return "N/A"
    months = int(value)
    years = value / 12
    return f"{months} mo ({years:.1f} yr)"


def format_signed_currency(value: float) -> str:
    """Format a signed value with explicit plus/minus.

    Args:
        value: Value to format with sign.

    Returns:
        Signed currency string to highlight deltas.
    """
    prefix = "+" if value >= 0 else "-"
    return f"{prefix}{format_currency(abs(value))}"


def format_savings_delta(value: float) -> str:
    """Invert savings sign to match user-facing storytelling.

    Args:
        value: Value representing savings.

    Returns:
        Signed string reflecting the UX messaging used in the GUI.
    """
    prefix = "-" if value >= 0 else "+"
    return f"{prefix}{format_currency(abs(value))}"


logger.debug("Formatting helpers module initialized.")

__all__ = [
    "format_currency",
    "format_optional_currency",
    "format_months",
    "format_signed_currency",
    "format_savings_delta",
]

__description__ = """
Formatting utilities for the Streamlit refinance calculator widgets.
"""
