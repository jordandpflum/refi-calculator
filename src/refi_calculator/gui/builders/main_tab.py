"""Main calculator tab builder."""

# ruff: noqa: PLR0915

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from .helpers import add_input, result_block

if TYPE_CHECKING:
    from ..app import RefinanceCalculatorApp


def build_main_tab(
    app: RefinanceCalculatorApp,
    parent: ttk.Frame,
) -> None:
    """Build the calculator tab inputs and result panels.

    Args:
        app: Application instance that owns the tab data.
        parent: Frame that hosts the calculator elements.
    """
    input_frame = ttk.Frame(parent)
    input_frame.pack(fill=tk.X, pady=(0, 10))

    current_frame = ttk.LabelFrame(input_frame, text="Current Loan", padding=10)
    current_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

    add_input(current_frame, "Balance ($):", app.current_balance, 0, app._calculate)
    add_input(current_frame, "Rate (%):", app.current_rate, 1, app._calculate)
    add_input(current_frame, "Years Remaining:", app.current_remaining, 2, app._calculate)

    new_frame = ttk.LabelFrame(input_frame, text="New Loan", padding=10)
    new_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

    add_input(new_frame, "Rate (%):", app.new_rate, 0, app._calculate)
    add_input(new_frame, "Term (years):", app.new_term, 1, app._calculate)
    add_input(new_frame, "Closing Costs ($):", app.closing_costs, 2, app._calculate)
    add_input(new_frame, "Cash Out ($):", app.cash_out, 3, app._calculate)
    add_input(new_frame, "Opportunity Rate (%):", app.opportunity_rate, 4, app._calculate)
    add_input(new_frame, "Marginal Tax Rate (%):", app.marginal_tax_rate, 5, app._calculate)

    maintain_frame = ttk.Frame(new_frame)
    maintain_frame.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(8, 0))
    ttk.Checkbutton(
        maintain_frame,
        text="Maintain current payment (extra → principal)",
        variable=app.maintain_payment,
        command=app._calculate,
    ).pack(anchor=tk.W)

    btn_frame = ttk.Frame(parent)
    btn_frame.pack(pady=8)
    ttk.Button(btn_frame, text="Calculate", command=app._calculate).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Export CSV", command=app._export_csv).pack(
        side=tk.LEFT,
        padx=5,
    )

    results_frame = ttk.LabelFrame(parent, text="Analysis Results", padding=12)
    results_frame.pack(fill=tk.BOTH, expand=True)

    style = ttk.Style()
    style.configure("Header.TLabel", font=("Segoe UI", 9, "bold"))
    style.configure("Result.TLabel", font=("Segoe UI", 10))
    style.configure("Big.TLabel", font=("Segoe UI", 13, "bold"))

    app.pay_frame = ttk.Frame(results_frame)
    app.pay_frame.pack(fill=tk.X, pady=(0, 8))
    app.current_pmt_label = result_block(app.pay_frame, "Current Payment", 0)
    app.new_pmt_label = result_block(app.pay_frame, "New Payment", 1)
    app.savings_label = result_block(app.pay_frame, "Monthly Δ", 2)

    app.balance_frame = ttk.Frame(results_frame)
    app.balance_frame.pack(fill=tk.X, pady=(0, 8))
    app.new_balance_label = result_block(app.balance_frame, "New Loan Balance", 0)
    app.cash_out_label = result_block(app.balance_frame, "Cash Out", 1)
    result_block(app.balance_frame, "", 2)
    app.balance_frame.pack_forget()

    ttk.Separator(results_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)

    be_frame = ttk.Frame(results_frame)
    be_frame.pack(fill=tk.X, pady=(0, 8))
    app.simple_be_label = result_block(be_frame, "Simple Breakeven", 0)
    app.npv_be_label = result_block(be_frame, "NPV Breakeven", 1)

    ttk.Separator(results_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)

    int_frame = ttk.Frame(results_frame)
    int_frame.pack(fill=tk.X, pady=(0, 8))
    app.curr_int_label = result_block(int_frame, "Current Total Interest", 0)
    app.new_int_label = result_block(int_frame, "New Total Interest", 1)
    app.int_delta_label = result_block(int_frame, "Interest Δ", 2)

    ttk.Separator(results_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)

    app.tax_section_label = ttk.Label(
        results_frame,
        text="After-Tax Analysis (0% marginal rate)",
        style="Header.TLabel",
    )
    app.tax_section_label.pack(anchor=tk.W, pady=(0, 6))

    tax_pay_frame = ttk.Frame(results_frame)
    tax_pay_frame.pack(fill=tk.X, pady=(0, 8))
    app.at_current_pmt_label = result_block(tax_pay_frame, "Current (After-Tax)", 0)
    app.at_new_pmt_label = result_block(tax_pay_frame, "New (After-Tax)", 1)
    app.at_savings_label = result_block(tax_pay_frame, "Monthly Δ (A-T)", 2)

    tax_be_frame = ttk.Frame(results_frame)
    tax_be_frame.pack(fill=tk.X, pady=(0, 8))
    app.at_simple_be_label = result_block(tax_be_frame, "Simple BE (A-T)", 0)
    app.at_npv_be_label = result_block(tax_be_frame, "NPV BE (A-T)", 1)
    app.at_int_delta_label = result_block(tax_be_frame, "Interest Δ (A-T)", 2)

    ttk.Separator(results_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)

    app.accel_section_frame = ttk.Frame(results_frame)
    app.accel_section_label = ttk.Label(
        app.accel_section_frame,
        text="Accelerated Payoff (Maintain Payment)",
        style="Header.TLabel",
    )
    app.accel_section_label.pack(anchor=tk.W, pady=(0, 6))

    accel_row1 = ttk.Frame(app.accel_section_frame)
    accel_row1.pack(fill=tk.X, pady=(0, 8))
    app.accel_months_label = result_block(accel_row1, "Payoff Time", 0)
    app.accel_time_saved_label = result_block(accel_row1, "Time Saved", 1)
    app.accel_interest_saved_label = result_block(accel_row1, "Interest Saved", 2)

    ttk.Separator(app.accel_section_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)

    npv_cost_frame = ttk.Frame(results_frame)
    npv_cost_frame.pack(fill=tk.X, pady=(0, 8))

    ttk.Label(results_frame, text="Total Cost NPV Analysis", style="Header.TLabel").pack(
        anchor=tk.W,
        pady=(0, 6),
    )

    npv_cost_row = ttk.Frame(results_frame)
    npv_cost_row.pack(fill=tk.X, pady=(0, 8))
    app.current_cost_npv_label = result_block(npv_cost_row, "Current Loan NPV", 0)
    app.new_cost_npv_label = result_block(npv_cost_row, "New Loan NPV", 1)
    app.cost_npv_advantage_label = result_block(npv_cost_row, "NPV Advantage", 2)

    ttk.Separator(results_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)

    npv_frame = ttk.Frame(results_frame)
    npv_frame.pack(fill=tk.X)
    app.npv_title_label = ttk.Label(
        npv_frame,
        text="5-Year NPV of Refinancing",
        style="Header.TLabel",
    )
    app.npv_title_label.pack()
    app.five_yr_npv_label = ttk.Label(npv_frame, text="$0", style="Big.TLabel")
    app.five_yr_npv_label.pack(pady=3)


__all__ = [
    "build_main_tab",
]

__description__ = """
Builder for the primary calculator tab.
"""
