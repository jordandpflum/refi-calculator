"""Tests for the chart helper utilities."""

from __future__ import annotations

from refi_calculator.core import charts


def test_build_month_ticks_zero_max_returns_zero() -> None:
    """Zero or negative max months collapse to [0]."""

    assert charts.build_month_ticks(max_month=0) == [0]
    assert charts.build_month_ticks(max_month=-5) == [0]


def test_build_month_ticks_produces_distinct_ticks() -> None:
    """Ticks are monotonic, within the max, and include the final month."""

    ticks = charts.build_month_ticks(max_month=11, max_ticks=4)
    assert ticks[-1] == 11
    assert len(set(ticks)) == len(ticks)
    assert all(0 <= tick <= 11 for tick in ticks)
    assert ticks == sorted(ticks)


def test_build_linear_ticks_insufficient_max_ticks_returns_extremes() -> None:
    """If the caller requests fewer than MIN_LINEAR_TICKS ticks, only min and max show."""

    values = charts.build_linear_ticks(min_value=10.0, max_value=20.0, max_ticks=1)
    assert values == [10.0, 20.0]


def test_build_linear_ticks_zero_span_expands_range() -> None:
    """Zero span is expanded symmetrically before generating ticks."""

    ticks = charts.build_linear_ticks(min_value=5.0, max_value=5.0, max_ticks=5)
    assert len(ticks) == 5
    assert ticks[0] < 5.0 < ticks[-1]
    assert ticks[-1] == 7.5


def test_build_linear_ticks_regular_range_returns_even_intervals() -> None:
    """Regular increasing ranges split evenly between min and max."""

    ticks = charts.build_linear_ticks(min_value=0.0, max_value=8.0, max_ticks=5)
    assert ticks == [0.0, 2.0, 4.0, 6.0, 8.0]


__all__ = [
    "test_build_month_ticks_zero_max_returns_zero",
    "test_build_month_ticks_produces_distinct_ticks",
    "test_build_linear_ticks_insufficient_max_ticks_returns_extremes",
    "test_build_linear_ticks_zero_span_expands_range",
    "test_build_linear_ticks_regular_range_returns_even_intervals",
]
