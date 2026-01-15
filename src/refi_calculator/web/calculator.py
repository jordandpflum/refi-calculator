"""Helpers for gathering calculator inputs and orchestrating core analysis."""

from __future__ import annotations

from dataclasses import dataclass
from logging import getLogger

import streamlit as st

from refi_calculator.core.calculations import (
    analyze_refinance,
    generate_comparison_schedule,
    run_holding_period_analysis,
    run_sensitivity,
)
from refi_calculator.core.models import RefinanceAnalysis

logger = getLogger(__name__)

DEFAULT_CURRENT_BALANCE = 400_000.0
DEFAULT_CURRENT_RATE = 6.5
DEFAULT_CURRENT_REMAINING = 25.0
DEFAULT_NEW_RATE = 5.75
DEFAULT_NEW_TERM = 30.0
DEFAULT_CLOSING_COSTS = 8_000.0
DEFAULT_CASH_OUT = 0.0
DEFAULT_OPPORTUNITY_RATE = 5.0
DEFAULT_MARGINAL_TAX_RATE = 0.0
DEFAULT_NPV_WINDOW_YEARS = 5
DEFAULT_CHART_HORIZON_YEARS = 10
DEFAULT_SENSITIVITY_MAX_REDUCTION = 2.5
DEFAULT_SENSITIVITY_STEP = 0.125

OPTION_STATE_DEFAULTS: dict[str, float] = {
    "chart_horizon_years": DEFAULT_CHART_HORIZON_YEARS,
    "sensitivity_max_reduction": DEFAULT_SENSITIVITY_MAX_REDUCTION,
    "sensitivity_step": DEFAULT_SENSITIVITY_STEP,
}
ADVANCED_STATE_DEFAULTS: dict[str, float | bool] = {
    "opportunity_rate": DEFAULT_OPPORTUNITY_RATE,
    "marginal_tax_rate": DEFAULT_MARGINAL_TAX_RATE,
    "npv_window_years": DEFAULT_NPV_WINDOW_YEARS,
    "maintain_payment": False,
}

HOLDING_PERIODS = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20]


@dataclass
class CalculatorInputs:
    """Inputs collected from the Streamlit UI.

    Attributes:
        current_balance: Current loan balance.
        current_rate: Current percentage rate on the existing loan.
        current_remaining_years: Remaining years on the current mortgage.
        new_rate: Candidate refinance rate percentage.
        new_term_years: Term for the new loan in years.
        closing_costs: Expected closing costs for the refinance.
        cash_out: Cash out amount requested with the refinance.
        opportunity_rate: Discount rate for NPV computations (percent).
        marginal_tax_rate: Marginal tax rate for after-tax calculations (percent).
        npv_window_years: Horizon used to compute NPV savings.
        chart_horizon_years: Years displayed on the cumulative savings chart.
        maintain_payment: Whether the borrower maintains the current payment level.
        sensitivity_max_reduction: Max reduction below the current rate for sensitivity scenarios.
        sensitivity_step: Step size between successive sensitivity scenarios.
    """

    current_balance: float
    current_rate: float
    current_remaining_years: float
    new_rate: float
    new_term_years: float
    closing_costs: float
    cash_out: float
    opportunity_rate: float
    marginal_tax_rate: float
    npv_window_years: int
    chart_horizon_years: int
    maintain_payment: bool
    sensitivity_max_reduction: float
    sensitivity_step: float


def collect_inputs() -> CalculatorInputs:
    """Gather user inputs from Streamlit widgets.

    Returns:
        CalculatorInputs populated with the current values.
    """
    st.subheader("Loan Inputs")
    current_col, new_col = st.columns(2)

    with current_col:
        current_balance = st.number_input(
            "Balance ($)",
            min_value=0.0,
            value=DEFAULT_CURRENT_BALANCE,
            step=1_000.0,
        )
        current_rate = st.number_input(
            "Rate (%):",
            min_value=0.0,
            value=DEFAULT_CURRENT_RATE,
            step=0.01,
        )
        current_remaining_years = st.number_input(
            "Years Remaining",
            min_value=0.5,
            value=DEFAULT_CURRENT_REMAINING,
            step=0.5,
        )

    with new_col:
        new_rate = st.number_input(
            "New Rate (%):",
            min_value=0.0,
            value=DEFAULT_NEW_RATE,
            step=0.01,
        )
        new_term_years = st.number_input(
            "Term (years)",
            min_value=1.0,
            value=DEFAULT_NEW_TERM,
            step=0.5,
        )
        closing_costs = st.number_input(
            "Closing Costs ($)",
            min_value=0.0,
            value=DEFAULT_CLOSING_COSTS,
            step=500.0,
        )
        cash_out = st.number_input(
            "Cash Out ($)",
            min_value=0.0,
            value=DEFAULT_CASH_OUT,
            step=500.0,
        )

    with st.expander("Advanced options", expanded=False):
        opportunity_rate = st.number_input(
            "Opportunity Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state["opportunity_rate"],
            step=0.1,
            key="opportunity_rate",
        )
        marginal_tax_rate = st.number_input(
            "Marginal Tax Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state["marginal_tax_rate"],
            step=0.1,
            key="marginal_tax_rate",
        )
        npv_window_years = int(
            st.number_input(
                "NPV Window (years)",
                min_value=1,
                max_value=30,
                value=st.session_state["npv_window_years"],
                step=1,
                key="npv_window_years",
            ),
        )
        maintain_payment = st.checkbox(
            "Maintain current payment (extra → principal)",
            value=st.session_state["maintain_payment"],
            key="maintain_payment",
        )
        st.caption("Opportunity cost and tax rate feed into the NPV and savings dashboard.")

    chart_horizon_years = int(st.session_state["chart_horizon_years"])
    sensitivity_max_reduction = float(st.session_state["sensitivity_max_reduction"])
    sensitivity_step = float(st.session_state["sensitivity_step"])

    return CalculatorInputs(
        current_balance=current_balance,
        current_rate=current_rate,
        current_remaining_years=current_remaining_years,
        new_rate=new_rate,
        new_term_years=new_term_years,
        closing_costs=closing_costs,
        cash_out=cash_out,
        opportunity_rate=opportunity_rate,
        marginal_tax_rate=marginal_tax_rate,
        npv_window_years=npv_window_years,
        chart_horizon_years=chart_horizon_years,
        maintain_payment=maintain_payment,
        sensitivity_max_reduction=sensitivity_max_reduction,
        sensitivity_step=sensitivity_step,
    )


def run_analysis(inputs: CalculatorInputs) -> RefinanceAnalysis:
    """Run the refinance analysis calculations.

    Args:
        inputs: Inputs captured from the UI.

    Returns:
        Analysis results for the provided scenario.
    """
    return analyze_refinance(
        current_balance=inputs.current_balance,
        current_rate=inputs.current_rate / 100,
        current_remaining_years=inputs.current_remaining_years,
        new_rate=inputs.new_rate / 100,
        new_term_years=inputs.new_term_years,
        closing_costs=inputs.closing_costs,
        cash_out=inputs.cash_out,
        opportunity_rate=inputs.opportunity_rate / 100,
        npv_window_years=inputs.npv_window_years,
        chart_horizon_years=inputs.chart_horizon_years,
        marginal_tax_rate=inputs.marginal_tax_rate / 100,
        maintain_payment=inputs.maintain_payment,
    )


def _build_rate_steps(
    current_rate_pct: float,
    max_reduction: float,
    step: float,
) -> list[float]:
    """Build new-rate steps for sensitivity analysis loops.

    Args:
        current_rate_pct: Current rate in percent.
        max_reduction: Max percent reduction to explore.
        step: Step between subsequent rows (percent).

    Returns:
        List of new rates expressed as decimals.
    """
    if step <= 0:
        return []

    rate_steps: list[float] = []
    reduction = step
    max_steps = 20
    while reduction <= max_reduction + 0.001 and len(rate_steps) < max_steps:
        new_rate_pct = current_rate_pct - reduction
        if new_rate_pct > 0:
            rate_steps.append(new_rate_pct / 100)
        reduction += step
    return rate_steps


def ensure_option_state() -> None:
    """Restore default option values in Streamlit session state."""
    for key, default in OPTION_STATE_DEFAULTS.items():
        st.session_state.setdefault(key, default)
    for key, default in ADVANCED_STATE_DEFAULTS.items():
        st.session_state.setdefault(key, default)


def prepare_auxiliary_data(
    inputs: CalculatorInputs,
) -> tuple[list[dict], list[dict], list[dict]]:
    """Compute supporting tables for the analysis tab.

    Args:
        inputs: Combination of all UI parameters.

    Returns:
        Tuple of sensitivity, holding period, and amortization data.
    """
    rate_steps = _build_rate_steps(
        inputs.current_rate,
        inputs.sensitivity_max_reduction,
        inputs.sensitivity_step,
    )
    sensitivity_data = run_sensitivity(
        inputs.current_balance,
        inputs.current_rate / 100,
        inputs.current_remaining_years,
        inputs.new_term_years,
        inputs.closing_costs,
        inputs.opportunity_rate / 100,
        rate_steps,
        inputs.npv_window_years,
    )
    holding_period_data = run_holding_period_analysis(
        inputs.current_balance,
        inputs.current_rate / 100,
        inputs.current_remaining_years,
        inputs.new_rate / 100,
        inputs.new_term_years,
        inputs.closing_costs,
        inputs.opportunity_rate / 100,
        inputs.marginal_tax_rate / 100,
        HOLDING_PERIODS,
        cash_out=inputs.cash_out,
    )
    amortization_data = generate_comparison_schedule(
        inputs.current_balance,
        inputs.current_rate / 100,
        inputs.current_remaining_years,
        inputs.new_rate / 100,
        inputs.new_term_years,
        inputs.closing_costs,
        cash_out=inputs.cash_out,
        maintain_payment=inputs.maintain_payment,
    )
    return sensitivity_data, holding_period_data, amortization_data


logger.debug("Calculator helpers module initialized.")


__all__ = ["CalculatorInputs", "collect_inputs", "run_analysis", "prepare_auxiliary_data"]

__description__ = """
Helpers for collecting inputs and driving core refinance calculations.
"""
