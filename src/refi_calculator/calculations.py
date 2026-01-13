"""Financial calculations for refinance analysis."""

from __future__ import annotations

from .models import LoanParams, RefinanceAnalysis


def calculate_accelerated_payoff(
    balance: float,
    rate: float,
    payment: float,
) -> tuple[int | None, float | None]:
    """Calculate months to payoff and total interest when paying more than minimum.

    Args:
        balance: Loan balance
        rate: Annual interest rate (as a decimal)
        payment: Monthly payment amount

    Returns:
        Tuple of (months to payoff, total interest paid)
    """
    if rate == 0:
        months = int(balance / payment) + 1
        return months, 0.0

    monthly_rate = rate / 12
    months = 0
    total_interest = 0.0
    remaining = balance

    min_term_in_months = 0
    max_term_in_months = 50 * 12  # Cap at 50 years
    while remaining > min_term_in_months and months < max_term_in_months:
        interest = remaining * monthly_rate
        principal = min(payment - interest, remaining)
        if principal <= 0:  # Payment doesn't cover interest - would never pay off
            return None, None
        remaining -= principal
        total_interest += interest
        months += 1

    return months, total_interest


def calculate_total_cost_npv(
    balance: float,
    rate: float,
    term_years: float,
    opportunity_rate: float,
    payment_override: float | None = None,
) -> float:
    """Calculate NPV of total loan cost (all payments discounted to present).

    Args:
        balance: Loan balance
        rate: Annual interest rate (as a decimal)
        term_years: Loan term in years
        opportunity_rate: Annual opportunity cost rate (as a decimal)
        payment_override: Optional monthly payment to use instead of standard

    Returns:
        NPV of total loan cost
    """
    loan = LoanParams(
        balance=balance,
        rate=rate,
        term_years=term_years,
    )
    payment = payment_override if payment_override else loan.monthly_payment
    monthly_opp_rate = opportunity_rate / 12

    if payment_override and payment_override > loan.monthly_payment:
        # Accelerated payoff
        months, _ = calculate_accelerated_payoff(
            balance=balance,
            rate=rate,
            payment=payment_override,
        )
        if months is None:
            months = loan.num_payments
    else:
        months = loan.num_payments

    npv = 0.0
    remaining = balance
    monthly_rate = rate / 12

    for month in range(1, months + 1):
        if remaining <= 0:
            break
        interest = remaining * monthly_rate
        actual_payment = min(payment, remaining + interest)
        principal = actual_payment - interest
        remaining -= principal
        npv += actual_payment / ((1 + monthly_opp_rate) ** month)

    return npv


def _build_cumulative_savings(
    monthly_savings: float,
    closing_costs: float,
    monthly_opp_rate: float,
    chart_months: int,
    schedule_months: int,
) -> tuple[list[tuple[int, float, float]], int | None]:
    """Build cumulative savings timeline for charting.

    Args:
        monthly_savings: Monthly savings amount
        closing_costs: Closing costs for refinance
        monthly_opp_rate: Monthly opportunity cost rate (as a decimal)
        chart_months: Number of months to show on chart
        schedule_months: Total months in loan schedule

    Returns:
        Tuple of (list of (month, nominal savings, NPV savings), NPV breakeven month)
    """
    cumulative_savings: list[tuple[int, float, float]] = [(0, -closing_costs, -closing_costs)]
    cum_pv = 0.0
    cum_nominal = -closing_costs
    npv_breakeven: int | None = None

    for month in range(1, min(chart_months, schedule_months) + 1):
        cum_pv += monthly_savings / ((1 + monthly_opp_rate) ** month)
        cum_nominal += monthly_savings
        cumulative_savings.append((month, cum_nominal, cum_pv - closing_costs))
        if npv_breakeven is None and cum_pv >= closing_costs:
            npv_breakeven = month

    return cumulative_savings, npv_breakeven


def _calculate_npv_window(
    monthly_savings: float,
    monthly_opp_rate: float,
    closing_costs: float,
    window_months: int,
) -> float:
    """Calculate NPV over a fixed window.

    Args:
        monthly_savings: Monthly savings amount
        monthly_opp_rate: Monthly opportunity cost rate (as a decimal)
        closing_costs: Closing costs for refinance
        window_months: Number of months in NPV window

    Returns:
        NPV over the specified window
    """
    npv = -closing_costs
    for month in range(1, window_months + 1):
        npv += monthly_savings / ((1 + monthly_opp_rate) ** month)
    return npv


def _find_npv_breakeven(
    monthly_savings: float,
    monthly_opp_rate: float,
    closing_costs: float,
    schedule_months: int,
) -> int | None:
    """Find NPV breakeven month within a schedule.

    Args:
        monthly_savings: Monthly savings amount
        monthly_opp_rate: Monthly opportunity cost rate (as a decimal)
        closing_costs: Closing costs for refinance
        schedule_months: Total months in loan schedule

    Returns:
        NPV breakeven month, or None if not reached within schedule
    """
    cum_pv = 0.0
    for month in range(1, schedule_months + 1):
        cum_pv += monthly_savings / ((1 + monthly_opp_rate) ** month)
        if cum_pv >= closing_costs:
            return month
    return None


def analyze_refinance(
    current_balance: float,
    current_rate: float,
    current_remaining_years: float,
    new_rate: float,
    new_term_years: float,
    closing_costs: float,
    opportunity_rate: float = 0.05,
    npv_window_years: int = 5,
    chart_horizon_years: int = 10,
    marginal_tax_rate: float = 0.0,
    cash_out: float = 0.0,
    maintain_payment: bool = False,
) -> RefinanceAnalysis:
    """Analyze refinance scenario.

    Args:
        current_balance: Current loan balance
        current_rate: Current loan interest rate (as a decimal)
        current_remaining_years: Current loan remaining term in years
        new_rate: New loan interest rate (as a decimal)
        new_term_years: New loan term in years
        closing_costs: Closing costs for refinance
        opportunity_rate: Opportunity cost rate (as a decimal). Default is 5%.
        npv_window_years: Years to calculate NPV over. Default is 5 years.
        chart_horizon_years: Years to show in cumulative savings chart. Default is 10 years.
        marginal_tax_rate: Marginal tax rate (as a decimal). Default is 0%.
        cash_out: Cash out amount from refinance. Default is 0.
        maintain_payment: Whether to maintain current payment amount. Default is False.

    Returns:
        RefinanceAnalysis object with results
    """
    current_loan = LoanParams(
        balance=current_balance,
        rate=current_rate,
        term_years=current_remaining_years,
    )

    new_balance = current_balance + closing_costs + cash_out
    new_loan = LoanParams(
        balance=new_balance,
        rate=new_rate,
        term_years=new_term_years,
    )

    monthly_savings = current_loan.monthly_payment - new_loan.monthly_payment

    simple_breakeven: float | None = None
    if monthly_savings > 0:
        simple_breakeven = closing_costs / monthly_savings

    monthly_opp_rate = opportunity_rate / 12
    chart_months = chart_horizon_years * 12
    cumulative_savings, npv_breakeven = _build_cumulative_savings(
        monthly_savings,
        closing_costs,
        monthly_opp_rate,
        chart_months,
        new_loan.num_payments,
    )

    npv_window_months = npv_window_years * 12
    window_npv = _calculate_npv_window(
        monthly_savings,
        monthly_opp_rate,
        closing_costs,
        npv_window_months,
    )

    current_avg_monthly_interest = current_loan.total_interest / current_loan.num_payments
    new_avg_monthly_interest = new_loan.total_interest / new_loan.num_payments
    current_monthly_tax_benefit = current_avg_monthly_interest * marginal_tax_rate
    new_monthly_tax_benefit = new_avg_monthly_interest * marginal_tax_rate

    current_after_tax_payment = current_loan.monthly_payment - current_monthly_tax_benefit
    new_after_tax_payment = new_loan.monthly_payment - new_monthly_tax_benefit
    after_tax_monthly_savings = current_after_tax_payment - new_after_tax_payment

    after_tax_simple_breakeven = None
    if after_tax_monthly_savings > 0:
        after_tax_simple_breakeven = closing_costs / after_tax_monthly_savings

    after_tax_npv_breakeven = _find_npv_breakeven(
        after_tax_monthly_savings,
        monthly_opp_rate,
        closing_costs,
        new_loan.num_payments,
    )

    after_tax_npv = _calculate_npv_window(
        after_tax_monthly_savings,
        monthly_opp_rate,
        closing_costs,
        npv_window_months,
    )

    current_after_tax_total_interest = current_loan.total_interest * (1 - marginal_tax_rate)
    new_after_tax_total_interest = new_loan.total_interest * (1 - marginal_tax_rate)

    accelerated_months: int | None = None
    accelerated_total_interest: float | None = None
    accelerated_interest_savings: float | None = None
    accelerated_time_savings_months: int | None = None

    # Accelerated payoff calculations (if maintaining current payment)
    if maintain_payment and current_loan.monthly_payment > new_loan.monthly_payment:
        # User wants to keep paying the old (higher) amount
        acc_months, acc_interest = calculate_accelerated_payoff(
            new_balance,
            new_rate,
            current_loan.monthly_payment,
        )
        if acc_months:
            accelerated_months = acc_months
            accelerated_total_interest = acc_interest
            if acc_interest is not None:
                accelerated_interest_savings = new_loan.total_interest - acc_interest
            accelerated_time_savings_months = new_loan.num_payments - acc_months

    # Total cost NPV calculations
    current_total_cost_npv = (
        calculate_total_cost_npv(
            current_balance,
            current_rate,
            current_remaining_years,
            opportunity_rate,
        )
        + closing_costs
    )  # Include closing costs in current scenario as sunk cost comparison

    if maintain_payment and current_loan.monthly_payment > new_loan.monthly_payment:
        new_total_cost_npv = calculate_total_cost_npv(
            new_balance,
            new_rate,
            new_term_years,
            opportunity_rate,
            payment_override=current_loan.monthly_payment,
        )
    else:
        new_total_cost_npv = calculate_total_cost_npv(
            new_balance,
            new_rate,
            new_term_years,
            opportunity_rate,
        )

    # Positive = refinancing is cheaper in NPV terms
    total_cost_npv_advantage = current_total_cost_npv - new_total_cost_npv - closing_costs

    return RefinanceAnalysis(
        current_payment=current_loan.monthly_payment,
        new_payment=new_loan.monthly_payment,
        monthly_savings=monthly_savings,
        simple_breakeven_months=simple_breakeven,
        npv_breakeven_months=npv_breakeven,
        current_total_interest=current_loan.total_interest,
        new_total_interest=new_loan.total_interest,
        interest_delta=new_loan.total_interest - current_loan.total_interest,
        five_year_npv=window_npv,
        cumulative_savings=cumulative_savings,
        current_after_tax_payment=current_after_tax_payment,
        new_after_tax_payment=new_after_tax_payment,
        after_tax_monthly_savings=after_tax_monthly_savings,
        after_tax_simple_breakeven_months=after_tax_simple_breakeven,
        after_tax_npv_breakeven_months=after_tax_npv_breakeven,
        after_tax_npv=after_tax_npv,
        current_after_tax_total_interest=current_after_tax_total_interest,
        new_after_tax_total_interest=new_after_tax_total_interest,
        after_tax_interest_delta=new_after_tax_total_interest - current_after_tax_total_interest,
        new_loan_balance=new_balance,
        cash_out_amount=cash_out,
        accelerated_months=accelerated_months,
        accelerated_total_interest=accelerated_total_interest,
        accelerated_interest_savings=accelerated_interest_savings,
        accelerated_time_savings_months=accelerated_time_savings_months,
        current_total_cost_npv=current_total_cost_npv,
        new_total_cost_npv=new_total_cost_npv,
        total_cost_npv_advantage=total_cost_npv_advantage,
    )


def generate_amortization_schedule(
    loan: LoanParams,
    label: str,
) -> list[dict]:
    """Generate Amortization Schedule.

    Args:
        loan: LoanParams object
        label: Label for the loan (e.g., "Current" or "New")

    Returns:
        List of dictionaries with amortization schedule details. Each dictionary contains:
            - loan: Loan label
            - month: Month number
            - year: Year number
            - payment: Monthly payment amount
            - principal: Principal portion of payment
            - interest: Interest portion of payment
            - balance: Remaining balance after payment
    """
    schedule = []
    balance = loan.balance
    monthly_payment = loan.monthly_payment
    monthly_rate = loan.monthly_rate

    for month in range(1, loan.num_payments + 1):
        interest_payment = balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        balance -= principal_payment
        if balance < 0:
            principal_payment += balance
            balance = 0
        schedule.append(
            {
                "loan": label,
                "month": month,
                "year": (month - 1) // 12 + 1,
                "payment": monthly_payment,
                "principal": principal_payment,
                "interest": interest_payment,
                "balance": max(0, balance),
            },
        )
    return schedule


def generate_amortization_schedule_pair(
    current_balance: float,
    current_rate: float,
    current_remaining_years: float,
    new_rate: float,
    new_term_years: float,
    closing_costs: float,
    cash_out: float = 0.0,
    maintain_payment: bool = False,
) -> tuple[list[dict], list[dict]]:
    """Produce monthly amortization schedules for the current and new loans.

    Args:
        current_balance: Current loan balance.
        current_rate: Current loan interest rate (as a decimal).
        current_remaining_years: Remaining term of the current loan.
        new_rate: Proposed refinance rate (as a decimal).
        new_term_years: Term for the new loan.
        closing_costs: Closing cost amount for the refinance.
        cash_out: Cash out amount applied to the refinance.
        maintain_payment: Whether the new loan should use the current payment.

    Returns:
        Tuple of (current_schedule, new_schedule), where each schedule is a list of
        monthly dictionaries matching the structure produced by ``generate_amortization_schedule``.
    """
    current_loan = LoanParams(current_balance, current_rate, current_remaining_years)
    new_balance = current_balance + closing_costs + cash_out
    new_loan = LoanParams(new_balance, new_rate, new_term_years)

    current_schedule = generate_amortization_schedule(current_loan, "Current")

    if maintain_payment and current_loan.monthly_payment > new_loan.monthly_payment:
        schedule: list[dict] = []
        balance = new_balance
        monthly_payment = current_loan.monthly_payment
        monthly_rate = new_rate / 12

        month = 0
        max_months = 600
        while balance > 0 and month < max_months:
            month += 1
            interest_payment = balance * monthly_rate
            principal_payment = monthly_payment - interest_payment
            balance -= principal_payment
            if balance < 0:
                principal_payment += balance
                balance = 0
            schedule.append(
                {
                    "loan": "New",
                    "month": month,
                    "year": (month - 1) // 12 + 1,
                    "payment": monthly_payment,
                    "principal": principal_payment,
                    "interest": interest_payment,
                    "balance": max(0, balance),
                },
            )
        new_schedule = schedule
    else:
        new_schedule = generate_amortization_schedule(new_loan, "New")

    return current_schedule, new_schedule


def generate_comparison_schedule(
    current_balance: float,
    current_rate: float,
    current_remaining_years: float,
    new_rate: float,
    new_term_years: float,
    closing_costs: float,
    cash_out: float = 0.0,
    maintain_payment: bool = False,
) -> list[dict]:
    """Generate Comparison Amortization Schedule between current and new loan.

    Args:
        current_balance: Current loan balance
        current_rate: Current loan interest rate (as a decimal)
        current_remaining_years: Current loan remaining term in years
        new_rate: New loan interest rate (as a decimal)
        new_term_years: New loan term in years
        closing_costs: Closing costs for refinance
        cash_out: Cash out amount from refinance. Default is 0.
        maintain_payment: Whether to maintain current payment amount. Default is False.

    Returns:
        List of dictionaries comparing current and new loan amortization schedules by year.
        Each dictionary contains:
            - year: Year number
            - current_principal: Total principal paid in current loan that year
            - current_interest: Total interest paid in current loan that year
            - current_balance: Remaining balance on current loan at year end
            - new_principal: Total principal paid in new loan that year
            - new_interest: Total interest paid in new loan that year
            - new_balance: Remaining balance on new loan at year end
            - principal_diff: Difference in principal paid (new - current)
            - interest_diff: Difference in interest paid (new - current)
            - balance_diff: Difference in balance (new - current)
    """
    current_schedule, new_schedule = generate_amortization_schedule_pair(
        current_balance=current_balance,
        current_rate=current_rate,
        current_remaining_years=current_remaining_years,
        new_rate=new_rate,
        new_term_years=new_term_years,
        closing_costs=closing_costs,
        cash_out=cash_out,
        maintain_payment=maintain_payment,
    )

    # Determine the number of years to show based on the actual schedules
    max_years = max(
        max((s["year"] for s in current_schedule), default=0),
        max((s["year"] for s in new_schedule), default=0),
    )
    comparison = []

    for year in range(1, max_years + 1):
        current_year_data = [s for s in current_schedule if s["year"] == year]
        new_year_data = [s for s in new_schedule if s["year"] == year]

        current_principal = sum(s["principal"] for s in current_year_data)
        current_interest = sum(s["interest"] for s in current_year_data)
        current_end_balance = current_year_data[-1]["balance"] if current_year_data else 0

        new_principal = sum(s["principal"] for s in new_year_data)
        new_interest = sum(s["interest"] for s in new_year_data)
        new_end_balance = new_year_data[-1]["balance"] if new_year_data else 0

        comparison.append(
            {
                "year": year,
                "current_principal": current_principal,
                "current_interest": current_interest,
                "current_balance": current_end_balance,
                "new_principal": new_principal,
                "new_interest": new_interest,
                "new_balance": new_end_balance,
                "principal_diff": new_principal - current_principal,
                "interest_diff": new_interest - current_interest,
                "balance_diff": new_end_balance - current_end_balance,
            },
        )
    return comparison


def run_holding_period_analysis(
    current_balance: float,
    current_rate: float,
    current_remaining_years: float,
    new_rate: float,
    new_term_years: float,
    closing_costs: float,
    opportunity_rate: float,
    marginal_tax_rate: float,
    holding_periods: list[int],
    cash_out: float = 0.0,
) -> list[dict]:
    """Run holding period analysis for various time frames.

    Args:
        current_balance: Current loan balance
        current_rate: Current loan interest rate (as a decimal)
        current_remaining_years: Current loan remaining term in years
        new_rate: New loan interest rate (as a decimal)
        new_term_years: New loan term in years
        closing_costs: Closing costs for refinance
        opportunity_rate: Opportunity cost rate (as a decimal)
        marginal_tax_rate: Marginal tax rate (as a decimal)
        holding_periods: List of holding periods in years to analyze
        cash_out: Cash out amount from refinance. Default is 0.

    Returns:
        List of dictionaries with analysis results for each holding period.
        Each dictionary contains:
            - years: Holding period in years
            - nominal_savings: Nominal savings over holding period
            - npv: NPV of savings over holding period
            - npv_after_tax: NPV of savings after tax adjustment
            - recommendation: Recommendation string based on NPV
    """
    results = []
    current_loan = LoanParams(current_balance, current_rate, current_remaining_years)
    new_balance = current_balance + closing_costs + cash_out
    new_loan = LoanParams(new_balance, new_rate, new_term_years)

    monthly_savings = current_loan.monthly_payment - new_loan.monthly_payment
    monthly_opp_rate = opportunity_rate / 12

    current_avg_monthly_interest = current_loan.total_interest / current_loan.num_payments
    new_avg_monthly_interest = new_loan.total_interest / new_loan.num_payments
    current_monthly_tax_benefit = current_avg_monthly_interest * marginal_tax_rate
    new_monthly_tax_benefit = new_avg_monthly_interest * marginal_tax_rate
    after_tax_monthly_savings = (current_loan.monthly_payment - current_monthly_tax_benefit) - (
        new_loan.monthly_payment - new_monthly_tax_benefit
    )

    for years in holding_periods:
        months = years * 12
        nominal_savings = (monthly_savings * months) - closing_costs
        npv = -closing_costs
        for m in range(1, months + 1):
            npv += monthly_savings / ((1 + monthly_opp_rate) ** m)
        npv_after_tax = -closing_costs
        for m in range(1, months + 1):
            npv_after_tax += after_tax_monthly_savings / ((1 + monthly_opp_rate) ** m)

        strong_yes_threshold = 5000
        yes_threshold = 0
        marginal_threshold = -2000
        if npv > strong_yes_threshold:
            recommendation = "Strong Yes"
        elif npv > yes_threshold:
            recommendation = "Yes"
        elif npv > -marginal_threshold:
            recommendation = "Marginal"
        else:
            recommendation = "No"

        results.append(
            {
                "years": years,
                "nominal_savings": nominal_savings,
                "npv": npv,
                "npv_after_tax": npv_after_tax,
                "recommendation": recommendation,
            },
        )
    return results


def run_sensitivity(
    current_balance: float,
    current_rate: float,
    current_remaining_years: float,
    new_term_years: float,
    closing_costs: float,
    opportunity_rate: float,
    rate_steps: list[float],
    npv_window_years: int = 5,
) -> list[dict]:
    """Run sensitivity analysis over a range of new interest rates.

    Args:
        current_balance: Current loan balance
        current_rate: Current loan interest rate (as a decimal)
        current_remaining_years: Current loan remaining term in years
        new_term_years: New loan term in years
        closing_costs: Closing costs for refinance
        opportunity_rate: Opportunity cost rate (as a decimal)
        rate_steps: List of new interest rates (as decimals) to analyze
        npv_window_years: Years to calculate NPV over. Default is 5 years.

    Returns:
        List of dictionaries with sensitivity analysis results for each new rate.
        Each dictionary contains:
            - new_rate: New interest rate (as a percentage)
            - monthly_savings: Monthly savings from refinancing
            - simple_be: Months to simple breakeven
            - npv_be: Months to NPV breakeven
            - five_yr_npv: NPV of savings over 5 years
    """
    results = []
    for new_rate in rate_steps:
        a = analyze_refinance(
            current_balance,
            current_rate,
            current_remaining_years,
            new_rate,
            new_term_years,
            closing_costs,
            opportunity_rate,
            npv_window_years=npv_window_years,
        )
        results.append(
            {
                "new_rate": new_rate * 100,
                "monthly_savings": a.monthly_savings,
                "simple_be": a.simple_breakeven_months,
                "npv_be": a.npv_breakeven_months,
                "five_yr_npv": a.five_year_npv,
            },
        )
    return results


__all__ = [
    "calculate_accelerated_payoff",
    "calculate_total_cost_npv",
    "analyze_refinance",
    "generate_amortization_schedule",
    "generate_amortization_schedule_pair",
    "generate_comparison_schedule",
    "run_holding_period_analysis",
    "run_sensitivity",
]

__description__ = """
Reusable calculations for the refinance calculator app.
"""
