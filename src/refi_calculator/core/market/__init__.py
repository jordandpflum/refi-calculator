"""Market data helpers for the refinance calculator core."""

from __future__ import annotations

from .fred import fetch_fred_series

__all__ = ["fetch_fred_series"]

__description__ = """
Shared helpers for retrieving market data in core interfaces.
"""
