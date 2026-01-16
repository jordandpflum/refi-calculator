"""Tests for the Streamlit formatting helpers."""

from __future__ import annotations

from refi_calculator.web import formatting


def test_format_currency_displays_whole_dollars() -> None:
    """Currency formatting rounds to the nearest dollar without cents."""

    assert formatting.format_currency(1234.56) == "$1,235"
    assert formatting.format_currency(-987.4) == "$-987"


def test_format_optional_currency_handles_none() -> None:
    """Optional formatting falls back to N/A when no value is provided."""

    assert formatting.format_optional_currency(None) == "N/A"
    assert formatting.format_optional_currency(10) == "$10"


def test_format_months_displays_months_and_years() -> None:
    """Month formatting includes both months and fractional years."""

    assert formatting.format_months(18) == "18 mo (1.5 yr)"
    assert formatting.format_months(None) == "N/A"


def test_format_signed_currency_and_savings_delta_prefix() -> None:
    """Signed formatters emit explicit signs consistent with UX conventions."""

    assert formatting.format_signed_currency(1500) == "+$1,500"
    assert formatting.format_signed_currency(-500) == "-$500"
    assert formatting.format_savings_delta(200) == "-$200"
    assert formatting.format_savings_delta(-200) == "+$200"
