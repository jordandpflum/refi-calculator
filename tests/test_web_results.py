"""Tests for the Streamlit results rendering helpers."""

from __future__ import annotations

from refi_calculator.core.models import RefinanceAnalysis
from refi_calculator.web.calculator import CalculatorInputs


def _build_sample_analysis() -> RefinanceAnalysis:
    """Create a sample RefinanceAnalysis payload for UI tests."""

    return RefinanceAnalysis(
        current_payment=2_000.0,
        new_payment=1_800.0,
        monthly_savings=200.0,
        simple_breakeven_months=10.0,
        npv_breakeven_months=12,
        current_total_interest=60_000.0,
        new_total_interest=55_000.0,
        interest_delta=-5_000.0,
        five_year_npv=3_000.0,
        cumulative_savings=[(0, -1_000.0, -900.0), (6, 500.0, 450.0)],
        current_after_tax_payment=1_950.0,
        new_after_tax_payment=1_750.0,
        after_tax_monthly_savings=200.0,
        after_tax_simple_breakeven_months=9.0,
        after_tax_npv_breakeven_months=10,
        after_tax_npv=2_500.0,
        current_after_tax_total_interest=45_000.0,
        new_after_tax_total_interest=42_000.0,
        after_tax_interest_delta=-3_000.0,
        new_loan_balance=400_000.0,
        cash_out_amount=0.0,
        accelerated_months=100,
        accelerated_total_interest=5_000.0,
        accelerated_interest_savings=200.0,
        accelerated_time_savings_months=20,
        current_total_cost_npv=12_000.0,
        new_total_cost_npv=9_000.0,
        total_cost_npv_advantage=3_000.0,
    )


def _build_sample_inputs() -> CalculatorInputs:
    """Construct fake calculator inputs for rendering tests."""

    return CalculatorInputs(
        current_balance=100_000.0,
        current_rate=5.0,
        current_remaining_years=20.0,
        new_rate=4.5,
        new_term_years=30.0,
        closing_costs=3_000.0,
        cash_out=0.0,
        opportunity_rate=4.0,
        marginal_tax_rate=0.25,
        npv_window_years=5,
        chart_horizon_years=10,
        maintain_payment=True,
        sensitivity_max_reduction=2.0,
        sensitivity_step=0.25,
    )


def test_interest_delta_styles() -> None:
    """Styling utilities color-code positive vs. negative deltas."""

    from refi_calculator.web.results import (
        _interest_delta_style,
        _recommendation_style,
    )

    assert _interest_delta_style("-$1,000") == "color: green"
    assert _interest_delta_style("+$1,000") == "color: red"
    assert _interest_delta_style("$0") == ""
    assert _recommendation_style("Strong Yes") == "color: green"
    assert _recommendation_style("Unknown") == "color: inherit"


def test_build_display_dataframes_format_values() -> None:
    """Display builders format columns with user-friendly decorators."""

    from refi_calculator.web.results import build_holding_display, build_sensitivity_display

    sensitivity = build_sensitivity_display(
        [{"new_rate": 4.5, "monthly_savings": 200.0, "simple_be": 10, "npv_be": 12, "five_yr_npv": 3_000.0}],
        npv_years=5,
    )
    assert "New Rate" in sensitivity.columns
    assert "5-Yr NPV" in sensitivity.columns

    holding = build_holding_display(
        [{"years": 5, "nominal_savings": 500.0, "npv": 1_000.0, "npv_after_tax": 900.0, "recommendation": "Yes"}],
    )
    assert "NPV (A-T)" in holding.columns
    assert "Recommendation" in holding.columns


def test_render_cumulative_and_balance_charts(
    reload_web_module: callable,
    streamlit_stub,
) -> None:
    """Chart renderers push data to Streamlit with the correct callbacks."""

    module = reload_web_module("refi_calculator.web.results")
    analysis = _build_sample_analysis()
    streamlit_stub.calls.clear()

    module.render_cumulative_chart(analysis)
    assert any(call[0] == "line_chart" for call in streamlit_stub.calls)
    streamlit_stub.calls.clear()

    amortization_data = [
        {"year": 1, "current_balance": 200_000.0, "new_balance": 190_000.0},
        {"year": 2, "current_balance": 190_000.0, "new_balance": 180_000.0},
    ]
    module.render_balance_comparison_chart(amortization_data)
    assert any(call[0] == "plotly_chart" for call in streamlit_stub.calls)


def test_render_analysis_and_options_tabs_employ_dataframes_and_metrics(
    reload_web_module: callable,
    streamlit_stub,
) -> None:
    """Analysis and options builders write tables and metrics through Streamlit."""

    module = reload_web_module("refi_calculator.web.results")
    inputs = _build_sample_inputs()
    sensitivity_data = [
        {"new_rate": 4.5, "monthly_savings": 200.0, "simple_be": 10, "npv_be": 12, "five_yr_npv": 2_500.0},
    ]
    holding_period_data = [
        {"years": 5, "nominal_savings": 500.0, "npv": 1_000.0, "npv_after_tax": 900.0, "recommendation": "Yes"},
    ]

    streamlit_stub.calls.clear()
    module.render_analysis_tab(inputs, sensitivity_data, holding_period_data)
    assert any(call[0] == "dataframe" for call in streamlit_stub.calls)

    streamlit_stub.calls.clear()
    analysis = _build_sample_analysis()
    module.render_results(inputs, analysis)
    assert any(call[0] == "metric" for call in streamlit_stub.calls)

    streamlit_stub.calls.clear()
    module.render_options_tab(inputs)
    assert any("number_input" in call for call in streamlit_stub.calls)
