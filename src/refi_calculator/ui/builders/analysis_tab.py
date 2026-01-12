"""Analysis tab builders."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import RefinanceCalculatorApp


def build_sensitivity_tab(
    app: RefinanceCalculatorApp,
    parent: ttk.Frame,
) -> None:
    """Build the sensitivity analysis tree.

    Args:
        app: App instance owning the sensitivity data.
        parent: Container frame for the sensitivity tab.
    """
    ttk.Label(
        parent,
        text="Sensitivity: Breakeven by New Rate",
        font=("Segoe UI", 10, "bold"),
    ).pack(anchor=tk.W, pady=(0, 10))

    columns = ("rate", "savings", "simple_be", "npv_be", "npv_5yr")
    app.sens_tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)

    app.sens_tree.heading("rate", text="New Rate")
    app.sens_tree.heading("savings", text="Monthly Savings")
    app.sens_tree.heading("simple_be", text="Simple BE")
    app.sens_tree.heading("npv_be", text="NPV BE")
    app.sens_tree.heading("npv_5yr", text="5-Yr NPV")

    for col in columns:
        app.sens_tree.column(col, width=90, anchor=tk.CENTER)

    app.sens_tree.pack(fill=tk.BOTH, expand=True)
    ttk.Button(
        parent,
        text="Export Sensitivity CSV",
        command=app._export_sensitivity_csv,
    ).pack(pady=10)


def build_holding_period_tab(
    app: RefinanceCalculatorApp,
    parent: ttk.Frame,
) -> None:
    """Build the holding period analysis tree.

    Args:
        app: App instance owning the holding period data.
        parent: Container frame for the holding period tab.
    """
    ttk.Label(parent, text="NPV by Holding Period", font=("Segoe UI", 10, "bold")).pack(
        anchor=tk.W,
        pady=(0, 10),
    )

    columns = ("years", "nominal_savings", "npv", "npv_after_tax", "recommendation")
    app.holding_tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)

    app.holding_tree.heading("years", text="Hold (Years)")
    app.holding_tree.heading("nominal_savings", text="Nominal Savings")
    app.holding_tree.heading("npv", text="NPV")
    app.holding_tree.heading("npv_after_tax", text="NPV (After-Tax)")
    app.holding_tree.heading("recommendation", text="Recommendation")

    app.holding_tree.column("years", width=80, anchor=tk.CENTER)
    app.holding_tree.column("nominal_savings", width=100, anchor=tk.CENTER)
    app.holding_tree.column("npv", width=90, anchor=tk.CENTER)
    app.holding_tree.column("npv_after_tax", width=100, anchor=tk.CENTER)
    app.holding_tree.column("recommendation", width=110, anchor=tk.CENTER)

    app.holding_tree.pack(fill=tk.BOTH, expand=True)
    ttk.Button(parent, text="Export Holding Period CSV", command=app._export_holding_csv).pack(
        pady=10,
    )


__all__ = [
    "build_sensitivity_tab",
    "build_holding_period_tab",
]

__description__ = """
Constructors for the analysis sub-tabs.
"""
