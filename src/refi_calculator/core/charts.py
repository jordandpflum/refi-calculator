"""Shared chart helper utilities for refinance visualizations."""

from __future__ import annotations

MIN_LINEAR_TICKS = 2


def build_month_ticks(max_month: int, max_ticks: int = 6) -> list[int]:
    """Generate tick positions for month-based axes.

    Args:
        max_month: Latest month number to display on the axis.
        max_ticks: Maximum number of tick marks to emit.

    Returns:
        A list of month values to use for axis ticks.
    """
    if max_month <= 0:
        return [0]

    tick_count = min(max_ticks, max_month + 1)
    if tick_count <= 1:
        return [max_month]

    interval = max_month / (tick_count - 1)
    ticks: list[int] = []
    last = -1
    for i in range(tick_count):
        tick = int(round(i * interval))
        if tick <= last:
            tick = last + 1
        tick = min(max_month, tick)
        ticks.append(tick)
        last = tick

    if ticks[-1] != max_month:
        ticks[-1] = max_month

    return ticks


def build_linear_ticks(min_value: float, max_value: float, max_ticks: int = 5) -> list[float]:
    """Generate evenly spaced linear axis tick values.

    Args:
        min_value: Minimum value to include on the axis.
        max_value: Maximum value to include on the axis.
        max_ticks: Maximum number of ticks to produce.

    Returns:
        A list of axis values covering the requested range.
    """
    if max_ticks < MIN_LINEAR_TICKS:
        return [min_value, max_value]

    span = max_value - min_value
    if span == 0:
        expansion = abs(max_value) or 1.0
        min_value -= expansion / 2
        max_value += expansion / 2
        span = max_value - min_value

    step = span / (max_ticks - 1)
    ticks = [min_value + step * i for i in range(max_ticks)]
    ticks[-1] = max_value
    return ticks


__all__ = [
    "MIN_LINEAR_TICKS",
    "build_month_ticks",
    "build_linear_ticks",
]

__description__ = """
Shared chart utilities for all refinance-calculator interfaces.
"""
