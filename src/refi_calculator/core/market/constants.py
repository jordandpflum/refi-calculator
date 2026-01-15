"""Constants for market data processing in the ReFi calculator."""

from __future__ import annotations

MARKET_SERIES: list[tuple[str, str]] = [
    ("30-Year", "MORTGAGE30US"),
    ("15-Year", "MORTGAGE15US"),
]

MARKET_PERIOD_OPTIONS: list[tuple[str, str]] = [
    ("1 Year", "12"),
    ("2 Years", "24"),
    ("5 Years", "60"),
    ("All", "0"),
]

MARKET_DEFAULT_PERIOD = "12"


__all__ = ["MARKET_SERIES", "MARKET_PERIOD_OPTIONS", "MARKET_DEFAULT_PERIOD"]

__description__ = """
Constants for market data processing in the ReFi calculator.
"""
