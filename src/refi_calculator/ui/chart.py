"""Savings chart component for the refinance GUI."""

from __future__ import annotations

import tkinter as tk


class SavingsChart(tk.Canvas):
    """Canvas that draws cumulative savings / NPV trends."""

    def __init__(
        self,
        parent,
        width=400,
        height=200,
    ):
        """Initialize SavingsChart.

        Args:
            parent: Parent Tkinter widget.
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
        self.padding = {"left": 60, "right": 20, "top": 20, "bottom": 40}

    def plot(
        self,
        data: list[tuple[int, float, float]],
        breakeven: int | None,
    ) -> None:
        """Plot cumulative savings tuples and optional breakeven marker."""
        self.delete("all")
        min_number_of_data_points = 2
        if len(data) < min_number_of_data_points:
            return

        months = [d[0] for d in data]
        nominal = [d[1] for d in data]
        npv = [d[2] for d in data]

        all_values = nominal + npv
        y_min, y_max = min(all_values), max(all_values)
        y_range = y_max - y_min if y_max != y_min else 1

        plot_w = self.width - self.padding["left"] - self.padding["right"]
        plot_h = self.height - self.padding["top"] - self.padding["bottom"]

        def to_canvas(month: int, value: float) -> tuple[float, float]:
            x = self.padding["left"] + (month / max(months)) * plot_w
            y = self.padding["top"] + (1 - (value - y_min) / y_range) * plot_h
            return x, y

        if y_min < 0 < y_max:
            _, zero_y = to_canvas(0, 0)
            self.create_line(
                self.padding["left"],
                zero_y,
                self.width - self.padding["right"],
                zero_y,
                fill="#ccc",
                dash=(4, 2),
            )

        if breakeven and breakeven <= max(months):
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

        nominal_points = [to_canvas(m, v) for m, v in zip(months, nominal)]
        npv_points = [to_canvas(m, v) for m, v in zip(months, npv)]

        if len(nominal_points) > 1:
            self.create_line(
                *[c for p in nominal_points for c in p],
                fill="#2563eb",
                width=2,
                smooth=True,
            )
        if len(npv_points) > 1:
            self.create_line(
                *[c for p in npv_points for c in p],
                fill="#16a34a",
                width=2,
                smooth=True,
            )

        self.create_line(
            self.padding["left"],
            self.padding["top"],
            self.padding["left"],
            self.height - self.padding["bottom"],
            fill="#333",
        )
        self.create_line(
            self.padding["left"],
            self.height - self.padding["bottom"],
            self.width - self.padding["right"],
            self.height - self.padding["bottom"],
            fill="#333",
        )

        self.create_text(
            self.width // 2,
            self.height - 8,
            text="Months",
            font=("Segoe UI", 8),
            fill="#666",
        )
        self.create_text(
            self.padding["left"] - 5,
            self.padding["top"],
            text=f"${y_max / 1000:.0f}k",
            anchor=tk.E,
            font=("Segoe UI", 7),
            fill="#666",
        )
        self.create_text(
            self.padding["left"] - 5,
            self.height - self.padding["bottom"],
            text=f"${y_min / 1000:.0f}k",
            anchor=tk.E,
            font=("Segoe UI", 7),
            fill="#666",
        )

        self.create_line(self.width - 100, 12, self.width - 80, 12, fill="#2563eb", width=2)
        self.create_text(
            self.width - 75,
            12,
            text="Nominal",
            anchor=tk.W,
            font=("Segoe UI", 7),
            fill="#666",
        )
        self.create_line(self.width - 100, 25, self.width - 80, 25, fill="#16a34a", width=2)
        self.create_text(
            self.width - 75,
            25,
            text="NPV",
            anchor=tk.W,
            font=("Segoe UI", 7),
            fill="#666",
        )


__all__ = ["SavingsChart"]

__description__ = """
Canvas helper for cumulative savings / NPV visuals.
"""
