"""Tests for the GUI chart components using injected tkinter stubs."""

from __future__ import annotations

from datetime import datetime


def _has_text(operations: list[tuple[str, tuple[object, ...], dict[str, object]]], text: str) -> bool:
    """Detect a text draw call within recorded operations."""

    return any(
        op[0] == "create_text" and op[2].get("text") == text
        for op in operations
        if op[2]
    )


def test_savings_chart_draws_zero_reference_and_breakeven(
    reload_gui_module: callable,
) -> None:
    """SavingsChart plots zero reference and breakeven when the range crosses zero."""

    chart_module = reload_gui_module("refi_calculator.gui.chart")
    chart = chart_module.SavingsChart(parent=None, width=200, height=150)
    data = [(0, -1_000.0, -700.0), (12, 2_500.0, 2_200.0)]
    chart.plot(data, breakeven=6)

    assert _has_text(chart.operations, "0 cumulative savings")
    assert _has_text(chart.operations, "BE: 6mo")
    line_ops = [op for op in chart.operations if op[0] == "create_line"]
    assert len(line_ops) > 5


def test_savings_chart_bails_out_with_insufficient_points(
    reload_gui_module: callable,
) -> None:
    """SavingsChart stops before drawing when data has fewer than two points."""

    chart_module = reload_gui_module("refi_calculator.gui.chart")
    chart = chart_module.SavingsChart(parent=None, width=200, height=150)
    chart.plot([(0, 0.0, 0.0)], breakeven=None)

    assert chart.operations == [("delete", ("all",), {})]


def test_amortization_chart_draws_axis_labels(
    reload_gui_module: callable,
) -> None:
    """AmortizationChart reports the expected axis labels when both schedules exist."""

    chart_module = reload_gui_module("refi_calculator.gui.chart")
    chart = chart_module.AmortizationChart(parent=None, width=220, height=180)
    current_schedule = [
        {"month": 1, "balance": 1_000.0},
        {"month": 2, "balance": 800.0},
    ]
    new_schedule = [
        {"month": 1, "balance": 1_200.0},
        {"month": 2, "balance": 600.0},
    ]
    chart.plot(current_schedule, new_schedule)

    assert _has_text(chart.operations, "Remaining Balance")
    assert _has_text(chart.operations, "Months")


def test_market_chart_draws_series_and_axes(
    reload_gui_module: callable,
) -> None:
    """MarketChart draws axes, ticks, and legends for each provided series."""

    chart_module = reload_gui_module("refi_calculator.gui.market_chart")
    chart = chart_module.MarketChart(parent=None, width=320, height=200)
    base_date = datetime(2024, 1, 1)
    series_data = {
        "Series A": [
            (base_date, 3.0),
            (base_date.replace(month=2), 3.5),
            (base_date.replace(month=3), 3.7),
        ],
        "Series B": [
            (base_date, 2.5),
            (base_date.replace(month=2), 2.8),
            (base_date.replace(month=3), 3.0),
        ],
    }
    chart.plot(series_data)

    assert _has_text(chart.operations, "Rate (%)")
    assert _has_text(chart.operations, "Date (oldest → newest)")
    assert _has_text(chart.operations, "Series A")
    assert _has_text(chart.operations, "Series B")


__all__ = [
    "test_savings_chart_draws_zero_reference_and_breakeven",
    "test_savings_chart_bails_out_with_insufficient_points",
    "test_amortization_chart_draws_axis_labels",
    "test_market_chart_draws_series_and_axes",
]
