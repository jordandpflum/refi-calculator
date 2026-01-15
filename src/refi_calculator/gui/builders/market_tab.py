"""Builders for the market data tab."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from ...core.market.constants import MARKET_PERIOD_OPTIONS, MARKET_SERIES
from ..market_chart import MarketChart

if TYPE_CHECKING:
    from ..app import RefinanceCalculatorApp


def build_market_tab(
    app: RefinanceCalculatorApp,
    parent: ttk.Frame,
) -> None:
    """Construct the market history tab in the main notebook.

    Args:
        app: Application instance that owns the Tkinter state.
        parent: Container frame that hosts the market history elements.
    """
    ttk.Label(
        parent,
        text="Historical Mortgage Rates",
        font=("Segoe UI", 11, "bold"),
    ).pack(anchor=tk.W, pady=(0, 6))

    status_label = ttk.Label(
        parent,
        wraplength=720,
        text="Loading market data...",
    )
    status_label.pack(anchor=tk.W, pady=(0, 6))

    cache_indicator = ttk.Label(
        parent,
        text="Cache: initializing...",
        font=("Segoe UI", 8),
        foreground="#666",
    )
    cache_indicator.pack(anchor=tk.W, pady=(0, 6))

    period_frame = ttk.Frame(parent)
    period_frame.pack(fill=tk.X, pady=(0, 6))
    ttk.Label(period_frame, text="Range:").pack(side=tk.LEFT)
    for label, value in MARKET_PERIOD_OPTIONS:
        ttk.Radiobutton(
            period_frame,
            text=label,
            variable=app.market_period_var,
            value=value,
            command=app._populate_market_tab,
        ).pack(side=tk.LEFT, padx=(6, 0))

    action_frame = ttk.Frame(parent)
    action_frame.pack(fill=tk.X, pady=(0, 6))
    ttk.Button(
        action_frame,
        text="Refresh Market Rates",
        command=app._refresh_market_data,
    ).pack(side=tk.LEFT)

    chart = MarketChart(parent)
    chart.pack(fill=tk.X, pady=(0, 8))

    table_frame = ttk.Frame(parent)
    table_frame.pack(fill=tk.BOTH, expand=True)

    labels = ["Date"] + [label for label, _ in MARKET_SERIES]
    columns = ("date",) + tuple(label.lower().replace(" ", "_") for label in labels[1:])
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
    tree.heading("date", text="Date")
    tree.column("date", width=130, anchor=tk.W)
    for label, column in zip(labels[1:], columns[1:]):
        tree.heading(column, text=label)
        tree.column(column, width=100, anchor=tk.E)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    legend_frame = ttk.Frame(parent)
    legend_frame.pack(anchor=tk.W, pady=(6, 0))
    colors = ["#2563eb", "#ec4899", "#16a34a", "#f59e0b"]
    for idx, (label, _) in enumerate(MARKET_SERIES):
        swatch = tk.Label(
            legend_frame,
            text=" ",
            width=2,
            bg=colors[idx % len(colors)],
            relief=tk.SUNKEN,
        )
        swatch.pack(side=tk.LEFT, padx=(0, 2))
        ttk.Label(
            legend_frame,
            text=label,
            font=("Segoe UI", 8),
        ).pack(side=tk.LEFT, padx=(0, 8))

    app.market_chart = chart
    app.market_tree = tree
    app._market_status_label = status_label
    app._market_cache_indicator = cache_indicator


__all__ = ["build_market_tab"]

__description__ = """
Builders for the market history tab inside the refinance calculator UI.
"""
