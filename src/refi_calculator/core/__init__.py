"""Shared core library for the refinance calculator package."""

from __future__ import annotations

from .calculations import (
    analyze_refinance,
    calculate_accelerated_payoff,
    calculate_total_cost_npv,
    generate_amortization_schedule,
    generate_amortization_schedule_pair,
    generate_comparison_schedule,
    run_holding_period_analysis,
    run_sensitivity,
)
from .charts import MIN_LINEAR_TICKS, build_linear_ticks, build_month_ticks
from .models import LoanParams, RefinanceAnalysis

__all__: list[str] = [
    "analyze_refinance",
    "calculate_accelerated_payoff",
    "calculate_total_cost_npv",
    "generate_amortization_schedule",
    "generate_amortization_schedule_pair",
    "generate_comparison_schedule",
    "run_holding_period_analysis",
    "run_sensitivity",
    "LoanParams",
    "RefinanceAnalysis",
    "MIN_LINEAR_TICKS",
    "build_month_ticks",
    "build_linear_ticks",
]

__description__ = """
Common calculations, models, and chart helpers that can be shared across interfaces.
"""
