"""Canvas for plotting historical market rates."""

from __future__ import annotations

import tkinter as tk


class MarketChart(tk.Canvas):
    """Simple line chart for market rate series.

    Attributes:
        width: Canvas width.
        height: Canvas height.
        padding: Chart padding.
    """

    width: int
    height: int
    padding: dict[str, int]

    def __init__(self, parent: tk.Misc, width: int = 780, height: int = 220):
        """Initialize the canvas.

        Args:
            parent: Parent widget for the chart.
            width: Chart width in pixels.
            height: Chart height in pixels.
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
        self.padding = {"left": 40, "right": 20, "top": 20, "bottom": 40}

    def plot(self, data: list[tuple[str, float]]) -> None:
        """Draw a line chart for the provided (date, rate) points.

        Args:
            data: Date/rate pairs ordered newest-first.
        """
        self.delete("all")
        if not data:
            return

        points = list(reversed(data))
        values = [rate for _, rate in points]

        min_points = 2
        if len(values) < min_points:
            self.create_text(
                self.width // 2,
                self.height // 2,
                text="Not enough data to plot.",
                fill="#888",
            )
            return

        min_rate = min(values)
        max_rate = max(values)
        rate_range = max_rate - min_rate if max_rate != min_rate else 1

        plot_width = self.width - self.padding["left"] - self.padding["right"]
        plot_height = self.height - self.padding["top"] - self.padding["bottom"]

        def x_coord(idx: int) -> float:
            return self.padding["left"] + (idx / (len(points) - 1)) * plot_width

        def y_coord(value: float) -> float:
            return self.padding["top"] + (1 - (value - min_rate) / rate_range) * plot_height

        coords = []
        for idx, (_, rate) in enumerate(points):
            coords.append((x_coord(idx), y_coord(rate)))

        for i in range(len(coords) - 1):
            self.create_line(
                coords[i][0],
                coords[i][1],
                coords[i + 1][0],
                coords[i + 1][1],
                fill="#2563eb",
                width=2,
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
            self.height - 10,
            text="Date (oldest → newest)",
            font=("Segoe UI", 8),
            fill="#666",
        )

        self.create_text(
            self.padding["left"] - 5,
            self.padding["top"],
            text=f"{max_rate:.2f}%",
            anchor=tk.E,
            font=("Segoe UI", 8),
            fill="#666",
        )

        self.create_text(
            self.padding["left"] - 5,
            self.height - self.padding["bottom"],
            text=f"{min_rate:.2f}%",
            anchor=tk.E,
            font=("Segoe UI", 8),
            fill="#666",
        )


__all__ = ["MarketChart"]

__description__ = """
Canvas helper for plotting historical mortgage rate series.
"""
