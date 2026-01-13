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

    def plot(self, series_data: dict[str, list[tuple[str, float]]]) -> None:
        """Draw a multi-line chart for the supplied rate series.

        Args:
            series_data: Mapping of series label to date/rate pairs (newest-first).
        """
        self.delete("all")
        filtered = {
            label: list(reversed(points)) for label, points in series_data.items() if points
        }
        if not filtered:
            return

        all_values = [rate for points in filtered.values() for _, rate in points]
        if not all_values:
            return

        min_rate = min(all_values)
        max_rate = max(all_values)
        rate_range = max_rate - min_rate if max_rate != min_rate else 1

        plot_width = self.width - self.padding["left"] - self.padding["right"]
        plot_height = self.height - self.padding["top"] - self.padding["bottom"]

        def x_coord(idx: int, total: int) -> float:
            return self.padding["left"] + (idx / max(total - 1, 1)) * plot_width

        def y_coord(value: float) -> float:
            return self.padding["top"] + (1 - (value - min_rate) / rate_range) * plot_height

        colors = ["#2563eb", "#ec4899", "#16a34a", "#f59e0b"]
        for idx, (label, points) in enumerate(filtered.items()):
            coords = [
                (x_coord(i, len(points)), y_coord(rate)) for i, (_, rate) in enumerate(points)
            ]
            min_coords = 2
            if len(coords) < min_coords:
                continue
            self.create_line(
                *[component for point in coords for component in point],
                fill=colors[idx % len(colors)],
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

        legend_x = self.width - self.padding["right"] - 110
        legend_y = self.padding["top"] + 10
        for idx, label in enumerate(filtered.keys()):
            color = colors[idx % len(colors)]
            self.create_line(
                legend_x,
                legend_y + idx * 16,
                legend_x + 20,
                legend_y + idx * 16,
                fill=color,
                width=2,
            )
            self.create_text(
                legend_x + 25,
                legend_y + idx * 16,
                text=label,
                anchor=tk.W,
                font=("Segoe UI", 8),
                fill="#444",
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
