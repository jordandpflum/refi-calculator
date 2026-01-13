"""Canvas for plotting historical market rates."""

from __future__ import annotations

import tkinter as tk
from datetime import datetime


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
        self.padding = {"left": 70, "right": 20, "top": 20, "bottom": 40}

    def plot(self, series_data: dict[str, list[tuple[datetime, float]]]) -> None:
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

        # Y-axis ticks
        tick_count_y = 4
        for idx in range(tick_count_y + 1):
            rate_value = min_rate + (rate_range / tick_count_y) * idx
            y = y_coord(rate_value)
            self.create_line(
                self.padding["left"] - 8,
                y,
                self.padding["left"],
                y,
                fill="#333",
            )
            self.create_text(
                self.padding["left"] - 14,
                y,
                text=f"{rate_value:.2f}%",
                anchor=tk.E,
                font=("Segoe UI", 7),
                fill="#666",
            )

        # X-axis ticks
        sample_points = next(iter(filtered.values()))
        total_points = len(sample_points)
        tick_step = max(1, total_points // 5)
        tick_indices = list(range(0, total_points, tick_step))
        if total_points - 1 not in tick_indices:
            tick_indices.append(total_points - 1)

        for idx in tick_indices:
            x = x_coord(idx, total_points)
            self.create_line(
                x,
                self.height - self.padding["bottom"],
                x,
                self.height - self.padding["bottom"] + 4,
                fill="#333",
            )
            date_label = sample_points[idx][0].strftime("%Y-%m-%d")
            self.create_text(
                x,
                self.height - self.padding["bottom"] + 14,
                text=date_label,
                anchor=tk.N,
                font=("Segoe UI", 7),
                fill="#666",
            )

        # Axis labels
        self.create_text(
            self.width // 2,
            self.height - 10,
            text="Date (oldest → newest)",
            font=("Segoe UI", 8, "bold"),
            fill="#444",
        )
        self.create_text(
            self.padding["left"] - 55,
            (self.height + self.padding["top"] - self.padding["bottom"]) // 2,
            text="Rate (%)",
            angle=90,
            font=("Segoe UI", 8, "bold"),
            fill="#444",
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


__all__ = ["MarketChart"]

__description__ = """
Canvas helper for plotting historical mortgage rate series.
"""
