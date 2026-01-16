"""Tests for the web calculator helper functions."""

from __future__ import annotations

import pytest

from refi_calculator.web import calculator as calculator_module
from refi_calculator.web.calculator import (
    CalculatorInputs,
    _build_rate_steps,
    prepare_auxiliary_data,
    run_analysis,
)
from tests.streamlit_stubs import StreamlitStub


def test_build_rate_steps_generates_expected_decimal_list() -> None:
    """Rate steps decrease from the current rate using the supplied step size."""

    steps = _build_rate_steps(current_rate_pct=6.0, max_reduction=0.5, step=0.25)
    assert steps == [0.0575, 0.055]  # 6.0% - 0.25% and 6.0% - 0.5%

    assert _build_rate_steps(current_rate_pct=5.0, max_reduction=0.0, step=0.5) == []
    assert _build_rate_steps(current_rate_pct=5.0, max_reduction=1.0, step=0) == []


def test_run_analysis_converts_percentages(monkeypatch: pytest.MonkeyPatch) -> None:
    """Percent inputs are converted into decimals before passing to the calculator.

    Args:
        monkeypatch: Fixture used to trap the core analyze_refinance call.
    """

    recorded: dict[str, object] = {}

    def fake_analyze(**kwargs: object) -> object:
        recorded.update(kwargs)
        return "analysis"

    monkeypatch.setattr(calculator_module, "analyze_refinance", fake_analyze)

    inputs = CalculatorInputs(
        current_balance=100_000.0,
        current_rate=6.0,
        current_remaining_years=20.0,
        new_rate=5.0,
        new_term_years=30.0,
        closing_costs=3_000.0,
        cash_out=0.0,
        opportunity_rate=4.0,
        marginal_tax_rate=25.0,
        npv_window_years=5,
        chart_horizon_years=10,
        maintain_payment=True,
        sensitivity_max_reduction=2.5,
        sensitivity_step=0.125,
    )

    assert run_analysis(inputs) == "analysis"
    assert recorded["current_rate"] == pytest.approx(0.06)
    assert recorded["new_rate"] == pytest.approx(0.05)
    assert recorded["opportunity_rate"] == pytest.approx(0.04)
    assert recorded["marginal_tax_rate"] == pytest.approx(0.25)


def test_prepare_auxiliary_data_delegates(monkeypatch: pytest.MonkeyPatch) -> None:
    """Auxiliary data helpers delegate to the core analysis routines."""

    monkeypatch.setattr(calculator_module, "run_sensitivity", lambda *args, **kwargs: ["sensitivity"])
    monkeypatch.setattr(
        calculator_module,
        "run_holding_period_analysis",
        lambda *args, **kwargs: ["holding"],
    )
    monkeypatch.setattr(
        calculator_module,
        "generate_comparison_schedule",
        lambda *args, **kwargs: ["amort"],
    )

    inputs = CalculatorInputs(
        current_balance=100_000.0,
        current_rate=5.0,
        current_remaining_years=20.0,
        new_rate=4.5,
        new_term_years=30.0,
        closing_costs=3_000.0,
        cash_out=0.0,
        opportunity_rate=4.0,
        marginal_tax_rate=25.0,
        npv_window_years=5,
        chart_horizon_years=10,
        maintain_payment=False,
        sensitivity_max_reduction=2.0,
        sensitivity_step=0.25,
    )

    sensitivity, holding, amort = prepare_auxiliary_data(inputs)
    assert sensitivity == ["sensitivity"]
    assert holding == ["holding"]
    assert amort == ["amort"]


def test_ensure_option_state_populates_defaults(reload_web_module: callable, streamlit_stub: StreamlitStub) -> None:
    """Session state defaults are restored when missing."""

    module = reload_web_module("refi_calculator.web.calculator")
    streamlit_stub.session_state.clear()

    module.ensure_option_state()

    assert streamlit_stub.session_state["chart_horizon_years"] == module.DEFAULT_CHART_HORIZON_YEARS
    assert streamlit_stub.session_state["npv_window_years"] == module.DEFAULT_NPV_WINDOW_YEARS
