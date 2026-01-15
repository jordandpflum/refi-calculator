"""Render refinance analysis output, visuals, and supporting tables."""

from __future__ import annotations

from logging import getLogger
from typing import cast

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from pandas.io.formats.style import Styler

from refi_calculator.core.models import RefinanceAnalysis
from refi_calculator.web.calculator import CalculatorInputs
from refi_calculator.web.formatting import (
    format_currency,
    format_months,
    format_optional_currency,
    format_savings_delta,
    format_signed_currency,
)

logger = getLogger(__name__)


def render_results(
    inputs: CalculatorInputs,
    analysis: RefinanceAnalysis,
) -> None:
    """Render the calculator summary metrics for the provided analysis.

    Args:
        inputs: Inputs used to drive the calculations.
        analysis: Computed refinance analysis.
    """
    st.subheader("Analysis Results")

    payments = st.columns(3)
    payments[0].metric("Current Payment", format_currency(analysis.current_payment))
    payments[1].metric("New Payment", format_currency(analysis.new_payment))
    payments[2].metric("Monthly Δ", format_savings_delta(analysis.monthly_savings))

    st.divider()

    balances = st.columns(2)
    balances[0].metric("New Loan Balance", format_currency(analysis.new_loan_balance))
    balances[1].metric("Cash Out", format_currency(analysis.cash_out_amount))

    st.divider()

    breakeven = st.columns(2)
    breakeven[0].metric(
        "Simple Breakeven",
        format_months(analysis.simple_breakeven_months),
    )
    breakeven[1].metric(
        "NPV Breakeven",
        format_months(analysis.npv_breakeven_months),
    )

    st.divider()

    interest = st.columns(3)
    interest[0].metric(
        "Current Total Interest",
        format_currency(analysis.current_total_interest),
    )
    interest[1].metric(
        "New Total Interest",
        format_currency(analysis.new_total_interest),
    )
    interest[2].metric(
        "Interest Δ",
        format_signed_currency(analysis.interest_delta),
    )

    st.divider()

    st.subheader("After-Tax Analysis")
    after_tax_payments = st.columns(3)
    after_tax_payments[0].metric(
        "Current (After-Tax)",
        format_currency(analysis.current_after_tax_payment),
    )
    after_tax_payments[1].metric(
        "New (After-Tax)",
        format_currency(analysis.new_after_tax_payment),
    )
    after_tax_payments[2].metric(
        "Monthly Δ (A-T)",
        format_savings_delta(analysis.after_tax_monthly_savings),
    )

    after_tax_breakeven = st.columns(3)
    after_tax_breakeven[0].metric(
        "Simple BE (A-T)",
        format_months(analysis.after_tax_simple_breakeven_months),
    )
    after_tax_breakeven[1].metric(
        "NPV BE (A-T)",
        format_months(analysis.after_tax_npv_breakeven_months),
    )
    after_tax_breakeven[2].metric(
        "Interest Δ (A-T)",
        format_signed_currency(analysis.after_tax_interest_delta),
    )

    st.divider()

    if inputs.maintain_payment and analysis.accelerated_months:
        st.subheader("Accelerated Payoff (Maintain Payment)")
        accel = st.columns(3)
        accel[0].metric("Payoff Time", format_months(analysis.accelerated_months))
        accel[1].metric(
            "Time Saved",
            format_months(analysis.accelerated_time_savings_months),
        )
        accel[2].metric(
            "Interest Saved",
            format_optional_currency(analysis.accelerated_interest_savings),
        )
        st.divider()

    st.subheader("Total Cost NPV Analysis")
    cost = st.columns(3)
    cost[0].metric("Current Loan NPV", format_currency(analysis.current_total_cost_npv))
    cost[1].metric("New Loan NPV", format_currency(analysis.new_total_cost_npv))
    cost[2].metric(
        "NPV Advantage",
        format_signed_currency(analysis.total_cost_npv_advantage),
    )

    st.divider()

    st.metric(
        f"{inputs.npv_window_years}-Year NPV of Refinancing",
        format_signed_currency(analysis.five_year_npv),
    )


def render_cumulative_chart(analysis: RefinanceAnalysis) -> None:
    """Render the cumulative savings chart for the current scenario.

    Args:
        analysis: Analysis output that contains the savings timeline.
    """
    if not analysis.cumulative_savings:
        st.info("Savings chart is not available yet.")
        return

    chart_df = pd.DataFrame(
        [
            {
                "Month": month,
                "Nominal": nominal,
                "NPV": npv_value,
            }
            for month, nominal, npv_value in analysis.cumulative_savings
        ],
    ).set_index("Month")

    st.line_chart(chart_df, width="stretch")

    if analysis.npv_breakeven_months:
        st.caption(
            f"NPV breakeven occurs at {analysis.npv_breakeven_months:.0f} months.",
        )


def render_balance_comparison_chart(amortization_data: list[dict]) -> None:
    """Plot loan balance comparison lines for current and new schedules."""
    if not amortization_data:
        st.info("Loan balance comparison will appear after running the calculator.")
        return

    df = pd.DataFrame(amortization_data)
    if df.empty:
        st.info("Loan balance comparison will appear after running the calculator.")
        return

    df = df[["year", "current_balance", "new_balance"]]
    df.columns = ["Year", "Current Balance", "New Balance"]
    df["Year"] = df["Year"].astype(int)

    colors = {
        "Current Balance": "#ef4444",
        "New Balance": "#16a34a",
    }
    fig = go.Figure()
    for loan in ["Current Balance", "New Balance"]:
        fig.add_trace(
            go.Scatter(
                x=df["Year"],
                y=df[loan],
                mode="lines",
                name=loan,
                line=dict(color=colors[loan], width=3),
                hovertemplate="Year=%{x}<br>Loan=%{text}<br>Balance=$%{y:,.0f}<extra></extra>",
                text=[loan] * len(df),
            ),
        )

    fig.update_layout(
        xaxis=dict(
            title="Year",
            tickmode="linear",
            dtick=1,
            tickformat="d",
            showgrid=False,
        ),
        yaxis=dict(
            title="Loan Balance ($)",
            tickprefix="$",
            tickformat=",",
        ),
        legend=dict(title="Loan"),
        margin=dict(t=5, b=30, l=60, r=10),
        hovermode="x",
    )

    st.plotly_chart(fig, use_container_width=True)


def _interest_delta_style(value: str | float) -> str:
    """Color interest delta values based on savings/costs."""
    text = str(value).strip()
    if text.startswith("-"):
        return "color: green"
    if text.startswith("+"):
        return "color: red"
    return ""


def build_sensitivity_display(
    data: list[dict],
    npv_years: int,
) -> pd.DataFrame:
    """Produce a display frame for rate sensitivity scenarios.

    Args:
        data: Raw sensitivity scenario data.
        npv_years: Years window used for NPV calculations.

    Returns:
        Formatted DataFrame for display.
    """
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    return pd.DataFrame(
        {
            "New Rate": df["new_rate"].map("{:.2f}%".format),
            "Monthly Δ": df["monthly_savings"].map(format_savings_delta),
            "Simple Breakeven": df["simple_be"].map(format_months),
            "NPV Breakeven": df["npv_be"].map(format_months),
            f"{npv_years}-Yr NPV": df["five_yr_npv"].map(format_signed_currency),
        },
    )


def build_holding_display(data: list[dict]) -> pd.DataFrame:
    """Create a holding-period display DataFrame.

    Args:
        data: Raw holding period analysis data.

    Returns:
        Formatted DataFrame for the holding period tab.
    """
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    return pd.DataFrame(
        {
            "Years": df["years"].map("{:.0f}".format),
            "Nominal Savings": df["nominal_savings"].map(format_signed_currency),
            "NPV": df["npv"].map(format_signed_currency),
            "NPV (A-T)": df["npv_after_tax"].map(format_signed_currency),
            "Recommendation": df["recommendation"],
        },
    )


RECOMMENDATION_COLORS = {
    "Strong Yes": "green",
    "Yes": "darkgreen",
    "Marginal": "orange",
    "No": "red",
}


def _recommendation_style(value: str) -> str:
    """Return CSS style string for recommendation text."""
    color = RECOMMENDATION_COLORS.get(value, "inherit")
    return f"color: {color}"


def render_analysis_tab(
    inputs: CalculatorInputs,
    sensitivity_data: list[dict],
    holding_period_data: list[dict],
) -> None:
    """Render the tables shown in the Analysis tab.

    Args:
        inputs: Inputs used to drive the scenario.
        sensitivity_data: Precomputed sensitivity data.
        holding_period_data: Precomputed holding period data.
    """
    st.subheader("Analysis Tables")
    rate_tab, holding_tab = st.tabs(["Rate Sensitivity", "Holding Period"])

    with rate_tab:
        display = build_sensitivity_display(sensitivity_data, inputs.npv_window_years)
        if display.empty:
            st.info("Adjust the sensitivity controls to generate scenarios.")
        else:
            st.dataframe(display.style.hide(axis="index"), width="stretch")

    with holding_tab:
        display = build_holding_display(holding_period_data)
        if display.empty:
            st.info("Holding period analysis will populate once inputs are available.")
        else:
            styled = display.style.hide(axis="index").applymap(
                _recommendation_style,
                subset=["Recommendation"],
            )
            st.dataframe(styled, width="stretch")


def render_loan_visualizations_tab(
    analysis: RefinanceAnalysis,
    amortization_data: list[dict],
) -> None:
    """Render the loan visualization subtabs for charts and tables.

    Args:
        analysis: Analysis output for the current inputs.
        amortization_data: Comparison schedule data.
    """
    st.subheader("Loan Visualizations")
    chart_tab, amort_tab = st.tabs(["Chart", "Amortization"])

    with chart_tab:
        st.subheader("Cumulative Savings")
        render_cumulative_chart(analysis)
        st.subheader("Loan Balance Comparison")
        render_balance_comparison_chart(amortization_data)

    with amort_tab:
        st.subheader("Amortization Comparison")
        if not amortization_data:
            st.info("Amortization data will appear after running the calculator.")
            return

        amort_df = pd.DataFrame(amortization_data)
        display_df = amort_df.rename(
            columns={
                "year": "Year",
                "current_principal": "Current Principal",
                "current_interest": "Current Interest",
                "current_balance": "Current Balance",
                "new_principal": "New Principal",
                "new_interest": "New Interest",
                "new_balance": "New Balance",
                "principal_diff": "Principal Δ",
                "interest_diff": "Interest Δ",
                "balance_diff": "Balance Δ",
            },
        )
        display_df = display_df.reset_index(drop=True)

        primary_columns = [
            "Current Principal",
            "Current Interest",
            "Current Balance",
            "New Principal",
            "New Interest",
            "New Balance",
        ]
        delta_columns = ["Principal Δ", "Interest Δ", "Balance Δ"]

        styler = Styler(display_df)
        styled = styler.format("${:,.0f}", subset=primary_columns).format(
            "${:+,.0f}",
            subset=delta_columns,
        )
        styled = cast(Styler, styled)
        styled = styled.applymap(_interest_delta_style, subset=["Interest Δ"])
        st.dataframe(styled, width="stretch")


def render_options_tab(inputs: CalculatorInputs) -> None:
    """Render controls that affect chart and sensitivity behavior.

    Args:
        inputs: Inputs used to drive the scenario.
    """
    st.subheader("Application Options")
    st.number_input(
        "Chart Horizon (years)",
        min_value=1,
        max_value=30,
        step=1,
        value=int(st.session_state["chart_horizon_years"]),
        key="chart_horizon_years",
    )
    st.number_input(
        "Max Rate Reduction (%)",
        min_value=0.0,
        max_value=5.0,
        step=0.1,
        value=float(st.session_state["sensitivity_max_reduction"]),
        key="sensitivity_max_reduction",
    )
    st.number_input(
        "Rate Step (%)",
        min_value=0.01,
        max_value=1.0,
        step=0.01,
        value=float(st.session_state["sensitivity_step"]),
        key="sensitivity_step",
    )
    st.caption(
        "Adjust settings here to explore chart horizons and sensitivity detail; changes "
        "take effect on the next calculation.",
    )

    st.divider()

    st.subheader("Active Parameters")
    cols = st.columns(3)
    cols[0].metric("Opportunity Rate", f"{inputs.opportunity_rate:.2f}%")
    cols[1].metric("Marginal Tax Rate", f"{inputs.marginal_tax_rate:.2f}%")
    cols[2].metric("NPV Window", f"{inputs.npv_window_years} years")


logger.debug("Results rendering module initialized.")

__all__ = [
    "render_results",
    "render_analysis_tab",
    "render_loan_visualizations_tab",
    "render_options_tab",
    "render_cumulative_chart",
    "build_sensitivity_display",
    "build_holding_display",
]

__description__ = """
Functions responsible for rendering calculator results, tables, and visuals.
"""
