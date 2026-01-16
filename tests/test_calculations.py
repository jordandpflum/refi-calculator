"""Tests for the refinance calculation helpers."""

from __future__ import annotations

import pytest

from refi_calculator.core import calculations, models


def test_calculate_accelerated_payoff_zero_rate() -> None:
    """Zero interest loans pay off in the expected number of payments."""

    balance = 12_000.0
    payment = 500.0

    months, total_interest = calculations.calculate_accelerated_payoff(
        balance=balance,
        rate=0.0,
        payment=payment,
    )

    assert months == int(balance / payment) + 1
    assert total_interest == 0.0


def test_calculate_accelerated_payoff_insufficient_payment() -> None:
    """Payments that do not cover interest never pay the loan down."""

    result = calculations.calculate_accelerated_payoff(
        balance=1_000.0,
        rate=0.12,
        payment=10.0,
    )

    assert result == (None, None)


def test_calculate_total_cost_npv_zero_rate_matches_total_payments() -> None:
    """Zero-rate loans have an NPV equal to the total undiscounted payments."""

    loan = models.LoanParams(balance=100_000.0, rate=0.0, term_years=30.0)
    total_payments = loan.monthly_payment * loan.num_payments

    npv = calculations.calculate_total_cost_npv(
        balance=loan.balance,
        rate=loan.rate,
        term_years=loan.term_years,
        opportunity_rate=0.0,
    )

    assert npv == pytest.approx(total_payments)


def test_calculate_total_cost_npv_discounted_returns_lower_value() -> None:
    """Introducing an opportunity cost yields a discounted NPV."""

    loan = models.LoanParams(balance=240_000.0, rate=0.045, term_years=30.0)
    undiscounted = loan.monthly_payment * loan.num_payments

    discounted = calculations.calculate_total_cost_npv(
        balance=loan.balance,
        rate=loan.rate,
        term_years=loan.term_years,
        opportunity_rate=0.05,
    )

    assert discounted < undiscounted


def test_analyze_refinance_returns_expected_fields() -> None:
    """The analysis surface reflects the underwriting inputs."""

    current_balance = 250_000.0
    closing_costs = 2_500.0
    analysis = calculations.analyze_refinance(
        current_balance=current_balance,
        current_rate=0.06,
        current_remaining_years=25.0,
        new_rate=0.045,
        new_term_years=30.0,
        closing_costs=closing_costs,
        marginal_tax_rate=0.25,
        maintain_payment=True,
    )

    assert analysis.monthly_savings > 0
    assert analysis.simple_breakeven_months == pytest.approx(
        closing_costs / analysis.monthly_savings,
    )
    assert analysis.cumulative_savings[0] == (0, -closing_costs, -closing_costs)
    assert analysis.total_cost_npv_advantage == pytest.approx(
        analysis.current_total_cost_npv - analysis.new_total_cost_npv - closing_costs,
    )

    new_balance = current_balance + closing_costs
    expected_months, expected_interest = calculations.calculate_accelerated_payoff(
        balance=new_balance,
        rate=0.045,
        payment=analysis.current_payment,
    )
    assert analysis.accelerated_months == expected_months

    if expected_months is not None and expected_interest is not None:
        new_loan = models.LoanParams(
            balance=new_balance,
            rate=0.045,
            term_years=30.0,
        )
        assert analysis.accelerated_total_interest == expected_interest
        assert analysis.accelerated_interest_savings == pytest.approx(
            new_loan.total_interest - expected_interest,
        )
        assert analysis.accelerated_time_savings_months == (
            new_loan.num_payments - expected_months
        )


def test_generate_amortization_schedule_pair_maintain_payment() -> None:
    """Maintaining payment uses the higher current payment for the new loan."""

    current_balance = 5_000.0
    current_loan = models.LoanParams(
        balance=current_balance,
        rate=0.05,
        term_years=1.0,
    )

    _, new_schedule = calculations.generate_amortization_schedule_pair(
        current_balance=current_balance,
        current_rate=0.05,
        current_remaining_years=1.0,
        new_rate=0.04,
        new_term_years=1.0,
        closing_costs=0.0,
        maintain_payment=True,
    )

    assert new_schedule[0]["payment"] == pytest.approx(current_loan.monthly_payment)
    assert new_schedule[-1]["balance"] == 0


def test_generate_comparison_schedule_matches_max_years() -> None:
    """Comparison schedule covers every year present in the amortization history."""

    params = dict(
        current_balance=10_000.0,
        current_rate=0.05,
        current_remaining_years=2.0,
        new_rate=0.045,
        new_term_years=2.0,
        closing_costs=0.0,
    )

    current_schedule, new_schedule = calculations.generate_amortization_schedule_pair(
        **params,
        cash_out=0.0,
        maintain_payment=False,
    )
    comparison = calculations.generate_comparison_schedule(**params)

    max_years = max(
        current_schedule[-1]["year"],
        new_schedule[-1]["year"],
    )

    assert len(comparison) == max_years
    assert comparison[-1]["year"] == max_years
    assert comparison[0]["principal_diff"] == pytest.approx(
        comparison[0]["new_principal"] - comparison[0]["current_principal"],
    )


def test_run_holding_period_analysis_recommendations() -> None:
    """Recommendations follow the defined thresholds for positive and negative NPVs."""

    positive = calculations.run_holding_period_analysis(
        current_balance=200_000.0,
        current_rate=0.04,
        current_remaining_years=30.0,
        new_rate=0.02,
        new_term_years=30.0,
        closing_costs=1_000.0,
        opportunity_rate=0.02,
        marginal_tax_rate=0.25,
        holding_periods=[5],
    )

    negative = calculations.run_holding_period_analysis(
        current_balance=200_000.0,
        current_rate=0.04,
        current_remaining_years=30.0,
        new_rate=0.07,
        new_term_years=30.0,
        closing_costs=1_000.0,
        opportunity_rate=0.02,
        marginal_tax_rate=0.25,
        holding_periods=[5],
    )

    assert positive[0]["recommendation"] == "Strong Yes"
    assert negative[0]["recommendation"] == "No"


def test_run_sensitivity_delegates_to_analysis() -> None:
    """Sensitivity results mirror values returned by the refinance analysis."""

    params = dict(
        current_balance=180_000.0,
        current_rate=0.045,
        current_remaining_years=30.0,
        new_term_years=30.0,
        closing_costs=2_000.0,
        opportunity_rate=0.03,
    )
    rate_steps = [0.04, 0.05]

    sensitivity = calculations.run_sensitivity(
        **params,
        rate_steps=rate_steps,
    )

    assert len(sensitivity) == len(rate_steps)

    for step, entry in zip(rate_steps, sensitivity):
        analysis = calculations.analyze_refinance(
            **params,
            new_rate=step,
        )
        assert entry["new_rate"] == pytest.approx(step * 100)
        assert entry["monthly_savings"] == pytest.approx(analysis.monthly_savings)
        assert entry["five_yr_npv"] == pytest.approx(analysis.five_year_npv)
