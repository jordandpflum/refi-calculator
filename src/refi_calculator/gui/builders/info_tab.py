"""Background and help info tab builders."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import RefinanceCalculatorApp


def build_background_tab(
    app: RefinanceCalculatorApp,
    parent: ttk.Frame,
) -> None:
    """Build background information scroll area.

    Args:
        app: Application instance that displays the background text.
        parent: Frame that hosts the scrollable background content.
    """
    canvas = tk.Canvas(parent, highlightthickness=0)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scroll_frame = ttk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
    )
    canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)

    canvas.bind("<Configure>", on_canvas_configure)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    app._background_canvas = canvas
    content = scroll_frame

    ttk.Label(
        content,
        text="Refinancing: Background & Concepts",
        font=("Segoe UI", 12, "bold"),
    ).pack(anchor=tk.W, pady=(0, 15))

    sections = [
        (
            "What is Refinancing?",
            "Refinancing replaces your existing mortgage with a new loan, typically to secure a lower interest rate, change the loan term, or access home equity (cash-out refinance). The new loan pays off your old mortgage, and you begin making payments on the new terms.\n\nCommon reasons to refinance:\n• Lower your interest rate and monthly payment\n• Shorten your loan term to pay off faster\n• Switch from adjustable-rate to fixed-rate (or vice versa)\n• Access equity for major expenses (cash-out refi)\n• Remove private mortgage insurance (PMI)",
        ),
        (
            "Key Costs to Consider",
            "Refinancing isn't free. Typical closing costs run 2-5% of the loan amount and may include:\n\n• Origination fees (lender charges)\n• Appraisal fee ($300-$700)\n• Title search and insurance\n• Recording fees\n• Credit report fee\n• Prepaid interest, taxes, and insurance\n\nThese costs can be paid upfront, rolled into the loan balance, or covered by accepting a slightly higher rate (\"no-cost\" refi). Rolling costs into the loan means you'll pay interest on them over time.",
        ),
        (
            "The Breakeven Concept",
            "The fundamental question: How long until your monthly savings recoup the closing costs?\n\nSimple Breakeven = Closing Costs ÷ Monthly Savings\n\nExample: $6,000 in costs with $200/month savings = 30 months to breakeven.\n\nIf you plan to stay in the home longer than the breakeven period, refinancing likely makes sense. If you might move or refinance again before breakeven, you'll lose money on the transaction.\n\nImportant caveat: Simple breakeven ignores the time value of money. A dollar saved three years from now is worth less than a dollar today.",
        ),
        (
            "Net Present Value (NPV)",
            'NPV provides a more sophisticated analysis by discounting future savings to today\'s dollars. It accounts for the "opportunity cost" of your closing costs — what you could have earned by investing that money instead.\n\nNPV = -Closing Costs + Σ (Monthly Savings / (1 + r)^n)\n\nWhere r is the monthly discount rate and n is the month number.\n\nA positive NPV means refinancing creates value even after accounting for opportunity cost. The higher the NPV, the more clearly beneficial the refinance.',
        ),
        (
            "The Term Reset Problem",
            "A critical nuance many borrowers miss: refinancing often resets your amortization clock.\n\nExample: You're 5 years into a 30-year mortgage (25 years remaining). If you refinance into a new 30-year loan, you've added 5 years to your payoff timeline — even if your rate dropped.\n\nThis can dramatically increase total interest paid over the life of the loan, even with a lower rate. Solutions:\n• Refinance into a shorter term (e.g., 20 or 15 years)\n• Make extra principal payments to maintain your original payoff date\n• Compare total interest paid, not just monthly payment",
        ),
        (
            "Tax Implications",
            "Mortgage interest is tax-deductible if you itemize deductions. This effectively reduces your true interest rate:\n\nAfter-Tax Rate = Nominal Rate × (1 - Marginal Tax Rate)\n\nExample: 6% rate with 24% marginal bracket = 4.56% effective rate\n\nNote: The 2017 tax law changes increased the standard deduction significantly, meaning fewer homeowners now itemize. If you take the standard deduction, there's no mortgage interest tax benefit.",
        ),
        (
            "Cash-Out Refinancing",
            "A cash-out refi lets you borrow against your home equity, receiving the difference as cash. Your new loan balance equals your old balance plus the cash withdrawn plus closing costs.\n\nConsiderations:\n• You're converting home equity into debt\n• Monthly payment will likely increase even with a lower rate\n• Interest on cash-out amounts above original loan may not be tax-deductible\n• Good for consolidating high-interest debt or funding investments\n• Risky if used for consumption or if home values decline",
        ),
        (
            "When NOT to Refinance",
            "Refinancing isn't always beneficial:\n\n• Short holding period: If you'll move before breakeven\n• Small rate reduction: Less than 0.5-0.75% often doesn't justify costs\n• Extended payoff: If resetting to 30 years significantly increases total interest\n• High closing costs: Some lenders charge excessive fees\n• Credit issues: Poor credit may mean higher rates or denial\n• Equity constraints: Most lenders require 20%+ equity for best rates\n\nRule of thumb: A 1% rate reduction with typical costs usually breaks even in 2-3 years.",
        ),
    ]

    for title, text in sections:
        ttk.Label(content, text=title, font=("Segoe UI", 10, "bold")).pack(
            anchor=tk.W,
            pady=(10, 5),
        )
        ttk.Label(
            content,
            text=text,
            wraplength=450,
            justify=tk.LEFT,
            font=("Segoe UI", 9),
        ).pack(anchor=tk.W, padx=(10, 0), pady=(0, 5))


def build_help_tab(
    app: RefinanceCalculatorApp,
    parent: ttk.Frame,
) -> None:
    """Build help info tab UI.

    Args:
        app: Application instance that displays the help text.
        parent: Frame that hosts the scrollable help content.
    """
    canvas = tk.Canvas(parent, highlightthickness=0)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scroll_frame = ttk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
    )
    canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)

    canvas.bind("<Configure>", on_canvas_configure)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    app._help_canvas = canvas
    content = scroll_frame

    ttk.Label(content, text="Application Help", font=("Segoe UI", 12, "bold")).pack(
        anchor=tk.W,
        pady=(0, 15),
    )

    sections = [
        (
            "Overview",
            "This calculator helps you analyze whether refinancing your mortgage makes financial sense. It goes beyond simple breakeven calculations to provide NPV analysis, tax-adjusted figures, sensitivity tables, and visualizations.\n\nAll calculations update automatically when you change inputs or press Enter.",
        ),
        (
            "Calculator Tab",
            "The main analysis screen with inputs and results.\n\nINPUTS - Current Loan:\n• Balance ($): Your remaining mortgage principal\n• Rate (%): Current annual interest rate\n• Years Remaining: Time left on your current loan\n\nINPUTS - New Loan:\n• Rate (%): Proposed new interest rate\n• Term (years): Length of new loan (typically 15, 20, or 30)\n• Closing Costs ($): Total refinance fees\n• Cash Out ($): Additional amount to borrow (0 for rate-only refi)\n• Opportunity Rate (%): Expected return on alternative investments\n• Marginal Tax Rate (%): Your tax bracket (0 if you don't itemize)",
        ),
        (
            "Rate Sensitivity Tab",
            'Shows how breakeven and NPV change at different new interest rates.\n\nThe table displays scenarios from your current rate down to the maximum reduction specified in Options (default: 2% in 0.25% steps).\n\nUse this to answer questions like:\n• "Should I wait for rates to drop further?"\n• "How much does each 0.25% reduction improve my outcome?"',
        ),
        (
            "Holding Period Tab",
            "Shows NPV at various holding periods (1-20 years).\n\nThis helps when you're uncertain how long you'll stay in the home. The recommendation column provides guidance:\n• Strong Yes (green): NPV > $5,000\n• Yes (dark green): NPV > $0\n• Marginal (orange): NPV between -$2,000 and $0\n• No (red): NPV < -$2,000",
        ),
        (
            "Loan Visualizations Tab",
            "The Loan Visualizations tab contains the annual amortization comparison table, which now includes a cumulative interest Δ column alongside colored savings/cost indicators so you can track how the refinance affects total interest year over year.",
        ),
        (
            "Charts within Loan Visualizations",
            "Two charts live on the Loan Visualizations tab:\n\n"
            "1. Cumulative Savings Chart — shows nominal (blue) and NPV-adjusted (green) savings with monthly ticks, a labeled zero line, and a dashed vertical line marking the NPV breakeven point.\n"
            "2. Loan Balance Comparison Chart — plots the remaining balances for the current (red) and new (blue) loans so you can see how the term reset or accelerated payoff affects your timeline.",
        ),
        (
            "Options Tab",
            "Customize calculation parameters:\n\n• NPV Window (years): Time horizon for NPV calculation displayed on main tab\n• Chart Horizon (years): How many years shown on the chart\n• Max Rate Reduction (%): How far below current rate to show in sensitivity table\n• Rate Step (%): Increment between rows in sensitivity table",
        ),
        (
            "Exporting Data",
            "Export buttons are available on Calculator, Rate Sensitivity, Holding Period, and Amortization tabs. Files are saved with timestamps to avoid overwriting.",
        ),
    ]

    for title, text in sections:
        ttk.Label(content, text=title, font=("Segoe UI", 10, "bold")).pack(
            anchor=tk.W,
            pady=(10, 5),
        )
        ttk.Label(
            content,
            text=text,
            wraplength=450,
            justify=tk.LEFT,
            font=("Segoe UI", 9),
        ).pack(anchor=tk.W, padx=(10, 0), pady=(0, 5))


__all__ = [
    "build_background_tab",
    "build_help_tab",
]

__description__ = """
Builders for the background and help tabs.
"""
