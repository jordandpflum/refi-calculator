"""Chart components for the refinance GUI."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from ..core.charts import build_linear_ticks, build_month_ticks


class SavingsChart(tk.Canvas):
    """Canvas that draws cumulative savings / NPV trends.

    Attributes:
        width: Canvas width.
        height: Canvas height.
        padding: Padding around the plot area.
    """

    width: int
    height: int
    padding: dict[str, int]

    def __init__(
        self,
        parent: tk.Misc,
        width: int = 400,
        height: int = 200,
    ):
        """Initialize SavingsChart.

        Args:
            parent: Parent Tkinter widget (any widget subclass).
            width: Canvas width.
            height: Canvas height.
        """
        super().__init__(
            parent,
            width=width,
            height=height,
            bg="white",
            highlightthickness=1,
            highlightbackground="#ccc",
        )
        self.width = width
        self.height = height
        self.padding = {
            "left": 60,
            "right": 20,
            "top": 20,
            "bottom": 40,
        }

    def plot(
        self,
        data: list[tuple[int, float, float]],
        breakeven: int | None,
    ) -> None:
        """Plot cumulative savings tuples and optional breakeven marker.

        Args:
            data: List of (month, nominal savings, NPV savings) tuples.
            breakeven: Optional breakeven month to mark on the chart.
        """
        self.delete("all")
        min_number_of_data_points = 2
        if len(data) < min_number_of_data_points:
            return

        months = [d[0] for d in data]
        nominal = [d[1] for d in data]
        npv = [d[2] for d in data]

        all_values = nominal + npv
        y_min, y_max = min(all_values), max(all_values)
        if y_min == y_max:
            expansion = abs(y_max) or 1.0
            y_min -= expansion / 2
            y_max += expansion / 2
        y_range = y_max - y_min
        if y_range == 0:
            y_range = 1.0

        plot_w = self.width - self.padding["left"] - self.padding["right"]
        plot_h = self.height - self.padding["top"] - self.padding["bottom"]

        max_month = max(months)
        if max_month == 0:
            max_month = 1

        def to_canvas(month: int, value: float) -> tuple[float, float]:
            x = self.padding["left"] + (month / max_month) * plot_w
            y = self.padding["top"] + (1 - (value - y_min) / y_range) * plot_h
            return x, y

        if y_min < 0 < y_max:
            self._draw_zero_reference(to_canvas)

        if breakeven and breakeven <= max_month:
            self._draw_breakeven_line(breakeven, to_canvas)

        nominal_points = self._canvas_points(months, nominal, to_canvas)
        npv_points = self._canvas_points(months, npv, to_canvas)

        self._render_series(nominal_points, "#2563eb")
        self._render_series(npv_points, "#16a34a")

        left = self.padding["left"]
        right = self.width - self.padding["right"]
        bottom = self.height - self.padding["bottom"]

        self._draw_axis_lines(left, bottom, right)
        self._draw_month_ticks(left, bottom, plot_w, max_month)
        self._draw_value_ticks(left, plot_h, bottom, y_min, y_max, y_range)
        self._draw_range_labels(left, bottom, y_min, y_max)
        self._draw_legend()

    def _draw_zero_reference(
        self,
        to_canvas: Callable[[int, float], tuple[float, float]],
    ) -> None:
        _, zero_y = to_canvas(0, 0)
        self.create_line(
            self.padding["left"],
            zero_y,
            self.width - self.padding["right"],
            zero_y,
            fill="#ccc",
            dash=(4, 2),
        )
        self.create_text(
            self.padding["left"] + 4,
            zero_y - 5,
            text="0 cumulative savings",
            anchor=tk.SW,
            font=("Segoe UI", 7),
            fill="#666",
        )

    def _draw_breakeven_line(
        self,
        breakeven: int,
        to_canvas: Callable[[int, float], tuple[float, float]],
    ) -> None:
        be_x, _ = to_canvas(breakeven, 0)
        self.create_line(
            be_x,
            self.padding["top"],
            be_x,
            self.height - self.padding["bottom"],
            fill="#888",
            dash=(2, 2),
        )
        self.create_text(
            be_x,
            self.padding["top"] - 5,
            text=f"BE: {breakeven}mo",
            font=("Segoe UI", 7),
            fill="#666",
        )

    def _canvas_points(
        self,
        months: list[int],
        values: list[float],
        to_canvas: Callable[[int, float], tuple[float, float]],
    ) -> list[tuple[float, float]]:
        return [to_canvas(month, value) for month, value in zip(months, values)]

    def _render_series(self, points: list[tuple[float, float]], color: str) -> None:
        if len(points) > 1:
            self.create_line(
                *[coord for point in points for coord in point],
                fill=color,
                width=2,
                smooth=True,
            )

    def _draw_axis_lines(self, left: float, bottom: float, right: float) -> None:
        self.create_line(
            left,
            self.padding["top"],
            left,
            bottom,
            fill="#333",
        )
        self.create_line(
            left,
            bottom,
            right,
            bottom,
            fill="#333",
        )

    def _draw_month_ticks(
        self,
        left: float,
        bottom: float,
        plot_width: float,
        max_month: int,
    ) -> None:
        for month in build_month_ticks(max_month):
            x = left + (month / max_month) * plot_width
            self.create_line(x, bottom, x, bottom + 5, fill="#999")
            self.create_text(
                x,
                bottom + 12,
                text=f"{month} mo",
                anchor=tk.N,
                font=("Segoe UI", 7),
                fill="#666",
            )

    def _draw_value_ticks(
        self,
        left: float,
        plot_height: float,
        bottom: float,
        y_min: float,
        y_max: float,
        y_range: float,
    ) -> None:
        top = self.padding["top"]
        for value in build_linear_ticks(y_min, y_max):
            y = top + (1 - (value - y_min) / y_range) * plot_height
            self.create_line(left - 5, y, left, y, fill="#999")
            self.create_text(
                left - 8,
                y,
                text=f"${value / 1000:.0f}k",
                anchor=tk.E,
                font=("Segoe UI", 7),
                fill="#666",
            )

    def _draw_range_labels(self, left: float, bottom: float, y_min: float, y_max: float) -> None:
        self.create_text(
            self.width // 2,
            self.height - 8,
            text="Months",
            font=("Segoe UI", 8),
            fill="#666",
        )
        self.create_text(
            left - 5,
            self.padding["top"],
            text=f"${y_max / 1000:.0f}k",
            anchor=tk.E,
            font=("Segoe UI", 7),
            fill="#666",
        )
        self.create_text(
            left - 5,
            bottom,
            text=f"${y_min / 1000:.0f}k",
            anchor=tk.E,
            font=("Segoe UI", 7),
            fill="#666",
        )

    def _draw_legend(self) -> None:
        legend_x = self.width - self.padding["right"] - 90
        self.create_line(legend_x, 14, legend_x + 24, 14, fill="#2563eb", width=2)
        self.create_text(
            legend_x + 28,
            14,
            text="Nominal",
            anchor=tk.W,
            font=("Segoe UI", 7),
            fill="#666",
        )
        self.create_line(legend_x, 26, legend_x + 24, 26, fill="#16a34a", width=2)
        self.create_text(
            legend_x + 28,
            26,
            text="NPV",
            anchor=tk.W,
            font=("Segoe UI", 7),
            fill="#666",
        )


class AmortizationChart(tk.Canvas):
    """Chart showing remaining balances for current and new loans.

    Attributes:
        width: Canvas width.
        height: Canvas height.
        padding: Plot padding.
    """

    width: int
    height: int
    padding: dict[str, int]

    def __init__(
        self,
        parent: tk.Misc,
        width: int = 400,
        height: int = 220,
    ):
        """Initialize AmortizationChart.

        Args:
            parent: Parent Tkinter widget (any widget subclass).
            width: Canvas width.
            height: Canvas height.
        """
        super().__init__(
            parent,
            width=width,
            height=height,
            bg="white",
            highlightthickness=1,
            highlightbackground="#ccc",
        )
        self.width = width
        self.height = height
        self.padding = {
            "left": 60,
            "right": 20,
            "top": 30,
            "bottom": 40,
        }

    def plot(
        self,
        current_schedule: list[dict],
        new_schedule: list[dict],
    ) -> None:
        """Plot remaining balances for both loans.

        Args:
            current_schedule: Monthly data for the current loan.
            new_schedule: Monthly data for the new loan.
        """
        self.delete("all")
        if not current_schedule or not new_schedule:
            return

        current_months = [row["month"] for row in current_schedule]
        current_balances = [row["balance"] for row in current_schedule]
        new_months = [row["month"] for row in new_schedule]
        new_balances = [row["balance"] for row in new_schedule]

        max_month = max(current_months[-1], new_months[-1])
        if max_month == 0:
            max_month = 1

        all_balances = [0.0]
        all_balances.extend(current_balances)
        all_balances.extend(new_balances)
        max_balance = max(all_balances)
        y_min = 0.0
        y_max = max_balance if max_balance > 0 else 1.0
        y_range = y_max - y_min if y_max != y_min else 1.0

        plot_w = self.width - self.padding["left"] - self.padding["right"]
        plot_h = self.height - self.padding["top"] - self.padding["bottom"]

        def to_canvas(month: int, balance: float) -> tuple[float, float]:
            x = self.padding["left"] + (month / max_month) * plot_w
            y = self.padding["top"] + (1 - (balance - y_min) / y_range) * plot_h
            return x, y

        current_points = [to_canvas(m, b) for m, b in zip(current_months, current_balances)]
        new_points = [to_canvas(m, b) for m, b in zip(new_months, new_balances)]

        if len(current_points) > 1:
            self.create_line(
                *[value for point in current_points for value in point],
                fill="#dc2626",
                width=2,
                smooth=True,
            )
        if len(new_points) > 1:
            self.create_line(
                *[value for point in new_points for value in point],
                fill="#2563eb",
                width=2,
                smooth=True,
            )

        left = self.padding["left"]
        bottom = self.height - self.padding["bottom"]
        right = self.width - self.padding["right"]

        self.create_line(left, self.padding["top"], left, bottom, fill="#333")
        self.create_line(left, bottom, right, bottom, fill="#333")

        for month in build_month_ticks(max_month):
            x = left + (month / max_month) * plot_w
            self.create_line(x, bottom, x, bottom + 5, fill="#999")
            self.create_text(
                x,
                bottom + 12,
                text=f"{month} mo",
                anchor=tk.N,
                font=("Segoe UI", 7),
                fill="#666",
            )

        for value in build_linear_ticks(y_min, y_max):
            y = self.padding["top"] + (1 - (value - y_min) / y_range) * plot_h
            self.create_line(left - 5, y, left, y, fill="#999")
            self.create_text(
                left - 8,
                y,
                text=f"${value / 1000:.0f}k",
                anchor=tk.E,
                font=("Segoe UI", 7),
                fill="#666",
            )

        self.create_text(
            self.padding["left"],
            self.padding["top"] - 6,
            text="Remaining Balance",
            anchor=tk.SW,
            font=("Segoe UI", 7),
            fill="#666",
        )
        self.create_text(
            self.width // 2,
            self.height - 8,
            text="Months",
            font=("Segoe UI", 8),
            fill="#666",
        )

        legend_x = self.width - self.padding["right"] - 90
        self.create_line(legend_x, 14, legend_x + 24, 14, fill="#dc2626", width=2)
        self.create_text(
            legend_x + 28,
            14,
            text="Current",
            anchor=tk.W,
            font=("Segoe UI", 7),
            fill="#666",
        )
        self.create_line(legend_x, 26, legend_x + 24, 26, fill="#2563eb", width=2)
        self.create_text(
            legend_x + 28,
            26,
            text="New",
            anchor=tk.W,
            font=("Segoe UI", 7),
            fill="#666",
        )


__all__ = [
    "AmortizationChart",
    "SavingsChart",
]

__description__ = """
Canvas helpers for cumulative savings and amortization comparison visuals.
"""
