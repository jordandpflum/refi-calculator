"""Loan and analysis data models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LoanParams:
    """Parameters for a mortgage loan.

    Attributes:
        balance: Loan balance.
        rate: Annual interest rate as a decimal.
        term_years: Loan term in years.
    """

    balance: float
    rate: float
    term_years: float

    @property
    def monthly_rate(self) -> float:
        """Monthly interest rate.

        Returns:
            Monthly interest rate as a decimal.
        """
        return self.rate / 12

    @property
    def num_payments(self) -> int:
        """Total number of monthly payments.

        Returns:
            Total number of payments.
        """
        return int(self.term_years * 12)

    @property
    def monthly_payment(self) -> float:
        """Monthly payment using the standard amortization formula.

        Returns:
            Monthly payment amount.
        """
        r = self.monthly_rate
        n = self.num_payments
        if r == 0:
            return self.balance / n
        return self.balance * (r * (1 + r) ** n) / ((1 + r) ** n - 1)

    @property
    def total_interest(self) -> float:
        """Total interest paid over the life of the loan."""
        return (self.monthly_payment * self.num_payments) - self.balance


@dataclass
class RefinanceAnalysis:
    """Results of refinance breakeven analysis.

    Attributes:
        current_payment: Current monthly payment.
        new_payment: New monthly payment.
        monthly_savings: Monthly savings from refinancing.
        simple_breakeven_months: Months to simple breakeven (nominal).
        npv_breakeven_months: Months to NPV breakeven.
        current_total_interest: Total interest of the current loan.
        new_total_interest: Total interest of the new loan.
        interest_delta: Interest difference between new and current loans.
        five_year_npv: NPV of savings over five years.
        cumulative_savings: Cumulative savings timeline.
        current_after_tax_payment: Current payment after tax benefit.
        new_after_tax_payment: New payment after tax benefit.
        after_tax_monthly_savings: After-tax monthly savings.
        after_tax_simple_breakeven_months: After-tax simple breakeven.
        after_tax_npv_breakeven_months: After-tax NPV breakeven.
        after_tax_npv: After-tax NPV of savings.
        current_after_tax_total_interest: Current loan interest after tax.
        new_after_tax_total_interest: New loan interest after tax.
        after_tax_interest_delta: Interest delta after tax.
        new_loan_balance: Balance of the new loan.
        cash_out_amount: Cash out amount included in the refinance.
        accelerated_months: Months to payoff when maintaining payment.
        accelerated_total_interest: Total interest when accelerating payoff.
        accelerated_interest_savings: Interest savings from acceleration.
        accelerated_time_savings_months: Months saved by accelerating payoff.
        current_total_cost_npv: NPV of the current loan total cost.
        new_total_cost_npv: NPV of the new loan total cost.
        total_cost_npv_advantage: NPV advantage of refinancing.
    """

    current_payment: float
    new_payment: float
    monthly_savings: float
    simple_breakeven_months: float | None
    npv_breakeven_months: int | None
    current_total_interest: float
    new_total_interest: float
    interest_delta: float
    five_year_npv: float
    cumulative_savings: list[tuple[int, float, float]]
    current_after_tax_payment: float
    new_after_tax_payment: float
    after_tax_monthly_savings: float
    after_tax_simple_breakeven_months: float | None
    after_tax_npv_breakeven_months: int | None
    after_tax_npv: float
    current_after_tax_total_interest: float
    new_after_tax_total_interest: float
    after_tax_interest_delta: float
    new_loan_balance: float
    cash_out_amount: float
    accelerated_months: int | None
    accelerated_total_interest: float | None
    accelerated_interest_savings: float | None
    accelerated_time_savings_months: int | None
    current_total_cost_npv: float
    new_total_cost_npv: float
    total_cost_npv_advantage: float


__all__ = [
    "LoanParams",
    "RefinanceAnalysis",
]

__description__ = """
Data models for refinance calculation results.
"""
