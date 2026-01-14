"""Visual tab builders for amortization and chart views."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from ..chart import AmortizationChart, SavingsChart
from .helpers import result_block

if TYPE_CHECKING:
    from ..app import RefinanceCalculatorApp


def build_amortization_tab(
    app: RefinanceCalculatorApp,
    parent: ttk.Frame,
) -> None:
    """Build amortization comparison tree and summary.

    Args:
        app: Application instance owning the amortization data.
        parent: Frame that contains amortization widgets.
    """
    ttk.Label(
        parent,
        text="Amortization Schedule Comparison (Annual)",
        font=("Segoe UI", 10, "bold"),
    ).pack(anchor=tk.W, pady=(0, 10))

    tree_frame = ttk.Frame(parent)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    columns = (
        "year",
        "curr_principal",
        "curr_interest",
        "curr_balance",
        "new_principal",
        "new_interest",
        "new_balance",
        "int_diff",
        "cum_interest_diff",
    )
    app.amort_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

    app.amort_tree.heading("year", text="Year")
    app.amort_tree.heading("curr_principal", text="Curr Principal")
    app.amort_tree.heading("curr_interest", text="Curr Interest")
    app.amort_tree.heading("curr_balance", text="Curr Balance")
    app.amort_tree.heading("new_principal", text="New Principal")
    app.amort_tree.heading("new_interest", text="New Interest")
    app.amort_tree.heading("new_balance", text="New Balance")
    app.amort_tree.heading("int_diff", text="Interest Δ")
    app.amort_tree.heading("cum_interest_diff", text="Cumulative Interest Δ")

    app.amort_tree.column("year", width=45, anchor=tk.CENTER)
    app.amort_tree.column("curr_principal", width=85, anchor=tk.E)
    app.amort_tree.column("curr_interest", width=80, anchor=tk.E)
    app.amort_tree.column("curr_balance", width=85, anchor=tk.E)
    app.amort_tree.column("new_principal", width=85, anchor=tk.E)
    app.amort_tree.column("new_interest", width=80, anchor=tk.E)
    app.amort_tree.column("new_balance", width=85, anchor=tk.E)
    app.amort_tree.column("int_diff", width=70, anchor=tk.E)
    app.amort_tree.column("cum_interest_diff", width=105, anchor=tk.E)

    y_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=app.amort_tree.yview)
    app.amort_tree.configure(yscrollcommand=y_scroll.set)

    app.amort_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    y_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    summary_frame = ttk.LabelFrame(parent, text="Cumulative Totals", padding=10)
    summary_frame.pack(fill=tk.X, pady=(10, 5))

    summary_cols = ttk.Frame(summary_frame)
    summary_cols.pack(fill=tk.X)

    app.amort_curr_total_int = result_block(summary_cols, "Current Total Interest", 0)
    app.amort_new_total_int = result_block(summary_cols, "New Total Interest", 1)
    app.amort_int_savings = result_block(summary_cols, "Interest Savings", 2)

    ttk.Button(
        parent,
        text="Export Amortization CSV",
        command=app._export_amortization_csv,
    ).pack(pady=10)


def build_chart_tab(
    app: RefinanceCalculatorApp,
    parent: ttk.Frame,
) -> None:
    """Build cumulative savings chart tab.

    Args:
        app: App instance providing chart parameters.
        parent: Frame used for the chart canvas.
    """
    chart_years = int(float(app.chart_horizon_years.get() or 10))
    ttk.Label(
        parent,
        text=f"Cumulative Savings Over Time ({chart_years} Years)",
        font=("Segoe UI", 10, "bold"),
    ).pack(anchor=tk.W, pady=(0, 10))

    app.chart = SavingsChart(parent, width=480, height=280)
    app.chart.pack(fill=tk.BOTH, expand=True)

    ttk.Label(
        parent,
        text="Loan Balance Comparison",
        font=("Segoe UI", 10, "bold"),
    ).pack(anchor=tk.W, pady=(18, 6))

    app.amortization_balance_chart = AmortizationChart(parent, width=480, height=240)
    app.amortization_balance_chart.pack(fill=tk.BOTH, expand=True)


__all__ = [
    "build_amortization_tab",
    "build_chart_tab",
]

__description__ = """
Builders for the visuals sub-tabs.
"""
