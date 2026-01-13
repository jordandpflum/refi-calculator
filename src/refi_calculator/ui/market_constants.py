"""Constants shared by the market data UI components."""

from __future__ import annotations

MARKET_SERIES: list[tuple[str, str]] = [
    ("30-Year", "MORTGAGE30US"),
    ("15-Year", "MORTGAGE15US"),
]


__all__ = ["MARKET_SERIES"]

__description__ = """
Constants used by the market data tab.
"""
