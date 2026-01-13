"""Options tab builder."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from .helpers import add_option

if TYPE_CHECKING:
    from ..app import RefinanceCalculatorApp


def build_options_tab(
    app: RefinanceCalculatorApp,
    parent: ttk.Frame,
) -> None:
    """Build the options tab for NPV/chart settings.

    Args:
        app: Application instance with option state.
        parent: Frame that hosts the options controls.
    """
    ttk.Label(parent, text="Application Options", font=("Segoe UI", 10, "bold")).pack(
        anchor=tk.W,
        pady=(0, 15),
    )

    options_frame = ttk.LabelFrame(parent, text="NPV & Chart Settings", padding=15)
    options_frame.pack(fill=tk.X, pady=(0, 10))

    add_option(
        options_frame,
        "NPV Window (years):",
        app.npv_window_years,
        0,
        "Time horizon for NPV calculation (e.g., 5 = 5-Year NPV)",
    )
    add_option(
        options_frame,
        "Chart Horizon (years):",
        app.chart_horizon_years,
        1,
        "How many years to display on the cumulative savings chart",
    )

    sens_frame = ttk.LabelFrame(parent, text="Sensitivity Analysis", padding=15)
    sens_frame.pack(fill=tk.X, pady=(0, 10))

    add_option(
        sens_frame,
        "Max Rate Reduction (%):",
        app.sensitivity_max_reduction,
        0,
        "How far below current rate to analyze (e.g., 2.0 = current - 2%)",
    )
    add_option(
        sens_frame,
        "Rate Step (%):",
        app.sensitivity_step,
        1,
        "Increment between rate scenarios (e.g., 0.25)",
    )

    ttk.Button(parent, text="Apply & Recalculate", command=app._calculate).pack(pady=15)
    ttk.Label(
        parent,
        text="Changes take effect after clicking 'Apply & Recalculate' or running a new calculation.",
        font=("Segoe UI", 8),
        foreground="#666",
    ).pack(anchor=tk.W)


__all__ = [
    "build_options_tab",
]

__description__ = """
Constructs the options tab controls.
"""
