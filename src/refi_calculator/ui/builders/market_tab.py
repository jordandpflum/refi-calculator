"""Builders for the market data tab."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

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
        text="Historical 30-Year Fixed Rates",
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

    tree_frame = ttk.Frame(parent)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    columns = ("date", "rate")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
    tree.heading("date", text="Date")
    tree.heading("rate", text="Rate (%)")
    tree.column("date", width=130, anchor=tk.W)
    tree.column("rate", width=110, anchor=tk.E)

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    action_frame = ttk.Frame(parent)
    action_frame.pack(fill=tk.X, pady=(6, 0))
    ttk.Button(
        action_frame,
        text="Refresh Market Rates",
        command=app._refresh_market_data,
    ).pack(side=tk.LEFT)

    app.market_tree = tree
    app._market_status_label = status_label
    app._market_cache_indicator = cache_indicator


__all__ = ["build_market_tab"]

__description__ = """
Builders for the market history tab inside the refinance calculator UI.
"""
