"""Refinance calculator package exports."""

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
from .models import LoanParams, RefinanceAnalysis
from .ui import RefinanceCalculatorApp, SavingsChart, main

__all__ = [
    "analyze_refinance",
    "calculate_accelerated_payoff",
    "calculate_total_cost_npv",
    "generate_amortization_schedule_pair",
    "generate_amortization_schedule",
    "generate_comparison_schedule",
    "run_holding_period_analysis",
    "run_sensitivity",
    "LoanParams",
    "RefinanceAnalysis",
    "RefinanceCalculatorApp",
    "SavingsChart",
    "main",
]

__description__ = """
Root package for the refinance calculator application.
"""
