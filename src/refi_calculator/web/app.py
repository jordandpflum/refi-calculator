"""Streamlit web interface for the refinance calculator."""

from __future__ import annotations

from dataclasses import dataclass

import altair as alt
import pandas as pd
import streamlit as st

from refi_calculator.core.calculations import (
    analyze_refinance,
    generate_comparison_schedule,
    run_holding_period_analysis,
    run_sensitivity,
)
from refi_calculator.core.market.fred import fetch_fred_series
from refi_calculator.core.models import RefinanceAnalysis
from refi_calculator.gui.market_constants import MARKET_PERIOD_OPTIONS, MARKET_SERIES

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

HOLDING_PERIODS = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20]

MARKET_CACHE_TTL_SECONDS = 15 * 60
MARKET_AXIS_YEAR_THRESHOLD_MONTHS = 24


def _get_fred_api_key() -> str | None:
    """Retrieve the FRED API key from Streamlit secrets, if set."""
    return st.secrets.get("FRED_API_KEY")


@st.cache_data(ttl=MARKET_CACHE_TTL_SECONDS)
def _fetch_market_series(
    series_id: str,
    api_key: str,
) -> list[tuple[str, float]]:
    """Fetch a series from FRED using cached data to minimize API calls.

    Args:
        series_id: FRED series identifier.
        api_key: FRED API key.

    Returns:
        List of (date, value) tuples for the requested series.
    """
    return fetch_fred_series(series_id, api_key)


@dataclass
class CalculatorInputs:
    """Inputs collected from the Streamlit UI.

    Attributes:
        current_balance: Current loan balance.
        current_rate: Current loan interest rate (percent).
        current_remaining_years: Remaining years on the current loan.
        new_rate: Candidate refinance rate (percent).
        new_term_years: Term for the new loan in years.
        closing_costs: Closing costs associated with the refinance.
        cash_out: Cash out amount requested with the refinance.
        opportunity_rate: Discount rate used for NPV computations (percent).
        marginal_tax_rate: Marginal tax rate applied to interest savings (percent).
        npv_window_years: Horizon used to evaluate the NPV savings window.
        chart_horizon_years: Years of cumulative savings shown on the chart.
        maintain_payment: Whether to keep paying the current payment amount.
        sensitivity_max_reduction: How far below current rate to run sensitivity scenarios (percent).
        sensitivity_step: Step between subsequent sensitivity rows (percent).
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


def _collect_inputs() -> CalculatorInputs:
    """Gather user inputs from Streamlit controls.

    Returns:
        CalculatorInputs populated from the interface widgets.
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

    maintain_payment = st.checkbox(
        "Maintain current payment (extra → principal)",
        value=False,
    )

    with st.expander("Advanced options", expanded=False):
        opportunity_rate = st.number_input(
            "Opportunity Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=DEFAULT_OPPORTUNITY_RATE,
            step=0.1,
        )
        marginal_tax_rate = st.number_input(
            "Marginal Tax Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=DEFAULT_MARGINAL_TAX_RATE,
            step=0.1,
        )
        npv_window_years = int(
            st.number_input(
                "NPV Window (years)",
                min_value=1,
                max_value=30,
                value=DEFAULT_NPV_WINDOW_YEARS,
                step=1,
            ),
        )
        chart_horizon_years = int(
            st.number_input(
                "Chart Horizon (years)",
                min_value=1,
                max_value=30,
                value=DEFAULT_CHART_HORIZON_YEARS,
                step=1,
            ),
        )
        sensitivity_max_reduction = st.number_input(
            "Max Rate Reduction (%)",
            min_value=0.0,
            max_value=5.0,
            value=DEFAULT_SENSITIVITY_MAX_REDUCTION,
            step=0.1,
        )
        sensitivity_step = st.number_input(
            "Rate Step (%)",
            min_value=0.01,
            max_value=1.0,
            value=DEFAULT_SENSITIVITY_STEP,
            step=0.01,
        )

        st.caption("Opportunity cost and tax rate feed into the NPV and savings dashboard.")

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


def _run_analysis(inputs: CalculatorInputs) -> RefinanceAnalysis:
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
    """Build the list of new interest rates for the sensitivity analysis.

    Args:
        current_rate_pct: Current loan interest rate (percent).
        max_reduction: Maximum reduction below current rate (percent).
        step: Step between subsequent sensitivity rows (percent).

    Returns:
        List of new interest rates (decimal) for sensitivity scenarios.
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


def _prepare_auxiliary_data(
    inputs: CalculatorInputs,
) -> tuple[list[dict], list[dict], list[dict]]:
    """Compute sensitivity, holding period, and amortization tables.

    Args:
        inputs: Inputs captured from the UI.

    Returns:
        Tuple of (sensitivity data, holding period data, amortization data).
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


def _format_currency(value: float) -> str:
    """Return a value formatted as whole-dollar currency.

    Args:
        value: Raw numeric value to format.

    Returns:
        The value with a dollar sign and comma separators.
    """
    return f"${value:,.0f}"


def _format_optional_currency(value: float | None) -> str:
    """Format optional currency values, falling back to "N/A" when missing.

    Args:
        value: Optional numeric value to display.

    Returns:
        Formatted currency string or "N/A" when no value is present.
    """
    if value is None:
        return "N/A"
    return _format_currency(value)


def _format_months(value: float | int | None) -> str:
    """Format month counts with an equivalent year representation.

    Args:
        value: Number of months to format.

    Returns:
        A string describing the months and equivalent years or "N/A".
    """
    if value is None:
        return "N/A"
    months = int(value)
    years = value / 12
    return f"{months} mo ({years:.1f} yr)"


def _format_signed_currency(value: float) -> str:
    """Format values with an explicit sign for positive/negative deltas.

    Args:
        value: Value that dictates the sign.

    Returns:
        Signed currency string.
    """
    prefix = "+" if value >= 0 else "-"
    return f"{prefix}{_format_currency(abs(value))}"


def _format_savings_delta(value: float) -> str:
    """Invert the sign on savings for the UX description used in the Tkinter app.

    Args:
        value: Savings value to invert.

    Returns:
        Signed currency string that highlights savings direction.
    """
    prefix = "-" if value >= 0 else "+"
    return f"{prefix}{_format_currency(abs(value))}"


def _render_results(inputs: CalculatorInputs, analysis: RefinanceAnalysis) -> None:
    """Render all result panels based on the provided analysis.

    Args:
        inputs: Inputs used to drive the scenario.
        analysis: Computed refinance metrics.
    """
    st.subheader("Analysis Results")

    payments = st.columns(3)
    payments[0].metric("Current Payment", _format_currency(analysis.current_payment))
    payments[1].metric("New Payment", _format_currency(analysis.new_payment))
    payments[2].metric("Monthly Δ", _format_savings_delta(analysis.monthly_savings))

    st.divider()

    balances = st.columns(2)
    balances[0].metric("New Loan Balance", _format_currency(analysis.new_loan_balance))
    balances[1].metric("Cash Out", _format_currency(analysis.cash_out_amount))

    st.divider()

    breakeven = st.columns(2)
    breakeven[0].metric("Simple Breakeven", _format_months(analysis.simple_breakeven_months))
    breakeven[1].metric("NPV Breakeven", _format_months(analysis.npv_breakeven_months))

    st.divider()

    interest = st.columns(3)
    interest[0].metric("Current Total Interest", _format_currency(analysis.current_total_interest))
    interest[1].metric("New Total Interest", _format_currency(analysis.new_total_interest))
    interest[2].metric("Interest Δ", _format_signed_currency(analysis.interest_delta))

    st.divider()

    st.subheader("After-Tax Analysis")
    after_tax_payments = st.columns(3)
    after_tax_payments[0].metric(
        "Current (After-Tax)",
        _format_currency(analysis.current_after_tax_payment),
    )
    after_tax_payments[1].metric(
        "New (After-Tax)",
        _format_currency(analysis.new_after_tax_payment),
    )
    after_tax_payments[2].metric(
        "Monthly Δ (A-T)",
        _format_savings_delta(analysis.after_tax_monthly_savings),
    )

    after_tax_breakeven = st.columns(3)
    after_tax_breakeven[0].metric(
        "Simple BE (A-T)",
        _format_months(analysis.after_tax_simple_breakeven_months),
    )
    after_tax_breakeven[1].metric(
        "NPV BE (A-T)",
        _format_months(analysis.after_tax_npv_breakeven_months),
    )
    after_tax_breakeven[2].metric(
        "Interest Δ (A-T)",
        _format_signed_currency(analysis.after_tax_interest_delta),
    )

    st.divider()

    if inputs.maintain_payment and analysis.accelerated_months:
        st.subheader("Accelerated Payoff (Maintain Payment)")
        accel = st.columns(3)
        accel[0].metric("Payoff Time", _format_months(analysis.accelerated_months))
        accel[1].metric(
            "Time Saved",
            _format_months(analysis.accelerated_time_savings_months),
        )
        accel[2].metric(
            "Interest Saved",
            _format_optional_currency(analysis.accelerated_interest_savings),
        )
        st.divider()

    st.subheader("Total Cost NPV Analysis")
    cost = st.columns(3)
    cost[0].metric("Current Loan NPV", _format_currency(analysis.current_total_cost_npv))
    cost[1].metric("New Loan NPV", _format_currency(analysis.new_total_cost_npv))
    cost[2].metric(
        "NPV Advantage",
        _format_signed_currency(analysis.total_cost_npv_advantage),
    )

    st.divider()

    st.metric(
        f"{inputs.npv_window_years}-Year NPV of Refinancing",
        _format_signed_currency(analysis.five_year_npv),
    )


def _render_cumulative_chart(analysis: RefinanceAnalysis) -> None:
    """Render the cumulative savings line chart.

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


def _build_sensitivity_display(
    data: list[dict],
    npv_years: int,
) -> pd.DataFrame:
    """Produce a display frame for rate sensitivity results.

    Args:
        data: Raw sensitivity scenario data.
        npv_years: Number of years used for NPV calculations.

    Returns:
        DataFrame formatted for display.
    """
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    return pd.DataFrame(
        {
            "New Rate": df["new_rate"].map("{:.2f}%".format),
            "Monthly Δ": df["monthly_savings"].map(_format_savings_delta),
            "Simple Breakeven": df["simple_be"].map(_format_months),
            "NPV Breakeven": df["npv_be"].map(_format_months),
            f"{npv_years}-Yr NPV": df["five_yr_npv"].map(_format_signed_currency),
        },
    )


def _build_holding_display(data: list[dict]) -> pd.DataFrame:
    """Create a display-friendly frame for holding period analysis.

    Args:
        data: Raw holding period scenario data.

    Returns:
        DataFrame formatted for display.
    """
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    return pd.DataFrame(
        {
            "Years": df["years"].map("{:.0f}".format),
            "Nominal Savings": df["nominal_savings"].map(_format_signed_currency),
            "NPV": df["npv"].map(_format_signed_currency),
            "NPV (A-T)": df["npv_after_tax"].map(_format_signed_currency),
            "Recommendation": df["recommendation"],
        },
    )


def _render_analysis_tab(
    inputs: CalculatorInputs,
    sensitivity_data: list[dict],
    holding_period_data: list[dict],
) -> None:
    """Render the Rate Sensitivity and Holding Period tabs.

    Args:
        inputs: Inputs used to drive the scenario.
        sensitivity_data: Precomputed sensitivity analysis data.
        holding_period_data: Precomputed holding period analysis data.
    """
    st.subheader("Analysis Tables")
    rate_tab, holding_tab = st.tabs(["Rate Sensitivity", "Holding Period"])

    with rate_tab:
        display = _build_sensitivity_display(sensitivity_data, inputs.npv_window_years)
        if display.empty:
            st.info("Adjust the sensitivity controls to generate scenarios.")
        else:
            st.dataframe(display, use_container_width=True)

    with holding_tab:
        display = _build_holding_display(holding_period_data)
        if display.empty:
            st.info("Holding period analysis will populate once inputs are available.")
        else:
            st.dataframe(display, use_container_width=True)


def _render_visuals_tab(
    analysis: RefinanceAnalysis,
    amortization_data: list[dict],
) -> None:
    """Render the visuals tab content.

    Args:
        analysis: Analysis output that contains the savings timeline.
        amortization_data: Precomputed amortization comparison data.
    """
    st.subheader("Cumulative Savings")
    _render_cumulative_chart(analysis)

    st.subheader("Amortization Comparison")
    if not amortization_data:
        st.info("Amortization data will appear after running the calculator.")
        return

    amort_df = pd.DataFrame(amortization_data)
    st.dataframe(
        amort_df.style.format(
            {
                "current_principal": "${:,.0f}",
                "current_interest": "${:,.0f}",
                "current_balance": "${:,.0f}",
                "new_principal": "${:,.0f}",
                "new_interest": "${:,.0f}",
                "new_balance": "${:,.0f}",
                "principal_diff": "${:,.0f}",
                "interest_diff": "${:,.0f}",
                "balance_diff": "${:,.0f}",
            },
        ),
        use_container_width=True,
    )


def _market_months_for_option(
    value: str,
) -> int | None:
    """Translate a period option value into a number of months.

    Args:
        value: Option value string.

    Returns:
        Number of months or None for all available data.
    """
    if value == "0":
        return None
    return int(value)


def _build_market_dataframe(
    raw_series: dict[str, list[tuple[str, float]]],
) -> pd.DataFrame:
    """Combine multiple FRED series into a single time-indexed frame.

    Args:
        raw_series: Mapping of series labels to raw (date, value) observations.

    Returns:
        DataFrame with a DateTime index and one column per series.
    """
    frames: list[pd.DataFrame] = []
    for label, observations in raw_series.items():
        if not observations:
            continue
        df = pd.DataFrame(observations, columns=["Date", label])
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)
        frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, axis=1).sort_index()


def _render_market_chart(data: pd.DataFrame) -> None:
    """Render the market series with controlled Y-axis domain.

    Args:
        data: DataFrame with Date index and one column per series.
    """
    if data.empty:
        return

    melted = data.reset_index().melt("Date", var_name="Series", value_name="Rate")

    min_rate = melted["Rate"].min()
    max_rate = melted["Rate"].max()
    span = max_rate - min_rate
    padding = max(span * 0.05, 0.25)
    lower = max(min_rate - padding, 0)
    upper = max_rate + padding

    date_span = data.index.max() - data.index.min()
    months = date_span.days / 30
    use_year_only = months >= MARKET_AXIS_YEAR_THRESHOLD_MONTHS
    date_format = "%Y" if use_year_only else "%b %Y"

    axis_kwargs: dict[str, object] = {
        "format": date_format,
        "labelAngle": -45,
        "labelFlush": True,
    }
    if use_year_only:
        start_year = data.index.min().year
        end_year = data.index.max().year
        axis_kwargs["values"] = [
            pd.Timestamp(year=y, month=1, day=1) for y in range(start_year, end_year + 1)
        ]
    else:
        axis_kwargs["tickCount"] = "month"

    chart = (
        alt.Chart(melted)
        .mark_line()
        .encode(
            x=alt.X("Date:T", title="Date", axis=alt.Axis(**axis_kwargs)),
            y=alt.Y(
                "Rate:Q",
                title="Rate (%)",
                scale=alt.Scale(domain=[lower, upper]),
            ),
            color=alt.Color("Series:N", legend=alt.Legend(title="Series")),
            tooltip=[
                alt.Tooltip("Date:T", title="Date"),
                alt.Tooltip("Series:N", title="Series"),
                alt.Tooltip("Rate:Q", title="Rate (%)", format=".2f"),
            ],
        )
        .interactive()
    )

    st.altair_chart(chart, use_container_width=True)


def _filter_market_df_by_months(
    data: pd.DataFrame,
    months: int | None,
) -> pd.DataFrame:
    """Return a view of the series restricted to the most recent `months`.

    Args:
        data: DataFrame with Date index and one column per series.
        months: Number of months to retain or None for all data.

    Returns:
        Filtered DataFrame.
    """
    if months is None or data.empty:
        return data

    last_date = data.index.max()
    cutoff = last_date - pd.DateOffset(months=months)
    return data.loc[data.index >= cutoff]


def _render_market_tab() -> None:
    """Render the market-rate tab with charts and tables."""
    st.subheader("Market Data")

    api_key = _get_fred_api_key()
    if not api_key:
        st.warning(
            "Add your FRED API key to `st.secrets['FRED_API_KEY']` to view mortgage rate history.",
        )
        return

    options = [label for label, _ in MARKET_PERIOD_OPTIONS]
    option_mapping = {label: value for label, value in MARKET_PERIOD_OPTIONS}
    period_label = st.radio("Range", options, horizontal=True, key="market_range")
    period_months = _market_months_for_option(option_mapping[period_label])

    raw_series: dict[str, list[tuple[str, float]]] = {}
    errors: list[str] = []
    for label, series_id in MARKET_SERIES:
        try:
            observations = _fetch_market_series(series_id, api_key)
        except RuntimeError as exc:
            errors.append(f"{label}: {exc}")
            observations = []
        raw_series[label] = observations

    if errors:
        for err in errors:
            st.error(err)

    market_df_all = _build_market_dataframe(raw_series)
    if market_df_all.empty:
        st.info("Market data is not available for the selected range.")
        return

    latest_valid = market_df_all.dropna(how="all")
    if latest_valid.empty:
        st.info("Market data lacks recent observations.")
        return

    latest = latest_valid.iloc[-1].dropna()
    latest_date = latest_valid.index.max().date()
    st.markdown(f"**Current Rates (latest available as of {latest_date:%Y-%m-%d})**")
    if not latest.empty:
        metric_cols = st.columns(len(latest))
        for col, (label, value) in zip(metric_cols, latest.items()):
            col.metric(label, f"{value:.2f}%")

    options = [label for label, _ in MARKET_PERIOD_OPTIONS]
    option_mapping = {label: value for label, value in MARKET_PERIOD_OPTIONS}
    period_label = st.radio("Range", options, horizontal=True)
    period_months = _market_months_for_option(option_mapping[period_label])

    market_df = _filter_market_df_by_months(market_df_all, period_months)
    if market_df.empty:
        st.info("Filtered market data is not available for the selected range.")
        return

    cache_minutes = MARKET_CACHE_TTL_SECONDS // 60
    st.caption(
        f"Cached for {cache_minutes} minutes; reload the app to refresh data.",
    )
    _render_market_chart(market_df)

    table = market_df.sort_index(ascending=False).head(12).reset_index()
    table["Date"] = table["Date"].dt.date
    st.dataframe(table, use_container_width=True)


def _render_options_tab(inputs: CalculatorInputs) -> None:
    """Show the calculation knobs that influence the analyses.

    Args:
        inputs: Inputs used to drive the scenario.
    """
    st.subheader("Active Parameters")
    cols = st.columns(3)
    cols[0].metric(
        "Opportunity Rate",
        f"{inputs.opportunity_rate:.2f}%",
    )
    cols[1].metric(
        "Marginal Tax Rate",
        f"{inputs.marginal_tax_rate:.2f}%",
    )
    cols[2].metric(
        "NPV Window",
        f"{inputs.npv_window_years} years",
    )
    cols = st.columns(3)
    cols[0].metric("Chart Horizon", f"{inputs.chart_horizon_years} years")
    cols[1].metric(
        "Sensitivity Max Reduction",
        f"{inputs.sensitivity_max_reduction:.2f}%",
    )
    cols[2].metric("Sensitivity Step", f"{inputs.sensitivity_step:.3f}%")
    st.caption("Use the calculator tab to change these values and rerun the analysis.")


BACKGROUND_SECTIONS = [
    (
        "What is Refinancing?",
        (
            "Refinancing replaces your existing mortgage with a new loan, typically to lock in a "
            "lower rate, change the term, or access equity. The new loan pays off your old mortgage "
            "and starts a fresh amortization schedule."
        ),
    ),
    (
        "Key Costs to Consider",
        (
            "Closing costs typically run 2-5% of the loan amount and may include origination "
            "fees, appraisal, title insurance, recording, and prepaid items. Rolling them into the "
            "new loan increases your balance and total interest."
        ),
    ),
    (
        "The Breakeven Concept",
        (
            "Simple breakeven equals closing costs divided by monthly savings. If you plan to leave "
            "the property before breakeven, the refinance loses money. NPV analysis discounts future "
            "savings to account for opportunity cost."
        ),
    ),
]

HELP_SECTIONS = [
    (
        "Overview",
        (
            "This calculator provides monthly payment comparisons, breakeven timelines, after-tax "
            "impact, and cumulative savings visualizations to help you decide whether refinancing "
            "creates value."
        ),
    ),
    (
        "Data Refresh",
        (
            "Every input change reruns the analysis instantly. Use Tab 1 to adjust loan terms and "
            "Tab 2 to explore sensitivity/holding period tables."
        ),
    ),
    (
        "Export Options",
        (
            "The desktop GUI supports CSV exports for calculator summaries, sensitivity, holding "
            "period, and amortization tables. On the web app, copy the figures you need or connect "
            "a backend export workflow."
        ),
    ),
]


def _render_info_tab() -> None:
    """Render background and guidance content."""
    st.subheader("Background")
    for title, text in BACKGROUND_SECTIONS:
        st.markdown(f"**{title}**")
        st.markdown(text)
    st.subheader("Help")
    for title, text in HELP_SECTIONS:
        st.markdown(f"**{title}**")
        st.markdown(text)


def main() -> None:
    """Render the refinance calculator Streamlit application."""
    st.set_page_config(
        page_title="Refinance Calculator",
        layout="wide",
    )

    st.title("Refinance Calculator")
    st.write(
        "Use the inputs below to compare refinancing scenarios, cash-out needs, "
        "and after-tax impacts before reviewing the cumulative savings timeline.",
    )

    calc_tab, analysis_tab, visuals_tab, market_tab, options_tab, info_tab = st.tabs(
        [
            "Calculator",
            "Analysis",
            "Visuals",
            "Market",
            "Options",
            "Info",
        ],
    )

    inputs: CalculatorInputs | None = None
    analysis: RefinanceAnalysis | None = None

    with calc_tab:
        inputs = _collect_inputs()
        analysis = _run_analysis(inputs)
        _render_results(inputs, analysis)

    if inputs is None or analysis is None:
        return

    sensitivity_data, holding_period_data, amortization_data = _prepare_auxiliary_data(inputs)

    with analysis_tab:
        _render_analysis_tab(inputs, sensitivity_data, holding_period_data)

    with visuals_tab:
        _render_visuals_tab(analysis, amortization_data)

    with market_tab:
        _render_market_tab()

    with options_tab:
        _render_options_tab(inputs)

    with info_tab:
        _render_info_tab()


if __name__ == "__main__":
    main()


__all__ = ["main"]

__description__ = """
Streamlit app that mirrors the desktop refinance calculator experience.
"""
