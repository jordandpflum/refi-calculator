"""Refinance breakeven GUI components."""

from __future__ import annotations

import csv
import os
import tkinter as tk
from datetime import datetime, timedelta
from logging import getLogger
from tkinter import filedialog, messagebox, ttk

from ..core.calculations import (
    analyze_refinance,
    generate_amortization_schedule_pair,
    generate_comparison_schedule,
    run_holding_period_analysis,
    run_sensitivity,
)
from ..core.market.constants import MARKET_DEFAULT_PERIOD, MARKET_SERIES
from ..core.market.fred import fetch_fred_series
from ..core.models import RefinanceAnalysis
from ..environment import load_dotenv
from .builders.analysis_tab import build_holding_period_tab, build_sensitivity_tab
from .builders.info_tab import build_background_tab, build_help_tab
from .builders.main_tab import build_main_tab
from .builders.market_tab import build_market_tab
from .builders.options_tab import build_options_tab
from .builders.visuals_tab import build_amortization_tab, build_chart_tab
from .chart import AmortizationChart, SavingsChart
from .market_chart import MarketChart

logger = getLogger(__name__)
load_dotenv()

# ruff: noqa: PLR0915, PLR0912

CALCULATOR_TAB_INDEX = 0
ANALYSIS_TAB_INDEX = 1
VISUALS_TAB_INDEX = 2
MARKET_TAB_INDEX = 3
OPTIONS_TAB_INDEX = 4
INFO_TAB_INDEX = 5

MARKET_CACHE_TTL = timedelta(minutes=15)


class RefinanceCalculatorApp:
    """Refinance Calculator Application.

    Attributes:
        root: Root Tkinter window
        current_analysis: Current refinance analysis results
        sensitivity_data: Sensitivity analysis data
        holding_period_data: Holding period analysis data
        amortization_data: Amortization comparison data
        amortization_balance_chart: Amortization chart comparing loan balances
        current_amortization_schedule: Monthly schedule for the current loan
        new_amortization_schedule: Monthly schedule for the new loan
        current_balance: Current loan balance input
        current_rate: Current loan interest rate input
        current_remaining: Current loan remaining term input
        new_rate: New loan interest rate input
        new_term: New loan term input
        closing_costs: Closing costs input
        cash_out: Cash-out amount input
        opportunity_rate: Opportunity cost rate input
        marginal_tax_rate: Marginal tax rate input
        npv_window_years: NPV calculation window input
        chart_horizon_years: Chart horizon years input
        sensitivity_max_reduction: Sensitivity max rate reduction input
        sensitivity_step: Sensitivity rate step input
        maintain_payment: Maintain current payment option
        fred_api_key: FRED API key for market data (if available)
        market_series_data: Historical rate observations keyed by series id
        market_series_errors: Load errors keyed by series id
        market_cache_timestamps: Cache timestamps keyed by series id
        market_period_var: Selected history window (months)
        market_chart: Chart widget displaying all series
        market_tree: Table showing side-by-side tenor values
        _market_status_label: Label describing market data status
        _market_cache_indicator: Cache freshness badge
        _calc_canvas: Canvas for the calculator tab
        sens_tree: Treeview for sensitivity analysis
        holding_tree: Treeview for holding period analysis
        amort_tree: Treeview for amortization comparison
        _background_canvas: Canvas for background info tab
        _help_canvas: Canvas for help info tab
        chart: Savings chart component
        pay_frame: Frame for payment results
        balance_frame: Frame for balance results
        current_pmt_label: Label for current payment result
        new_pmt_label: Label for new payment result
        savings_label: Label for monthly savings result
        new_balance_label: Label for new loan balance result
        cash_out_label: Label for cash-out amount result
        simple_be_label: Label for simple breakeven result
        npv_be_label: Label for NPV breakeven result
        curr_int_label: Label for current total interest result
        new_int_label: Label for new total interest result
        int_delta_label: Label for interest delta result
        tax_section_label: Label for after-tax section title
        at_current_pmt_label: Label for after-tax current payment result
        at_new_pmt_label: Label for after-tax new payment result
        at_savings_label: Label for after-tax monthly savings result
        at_simple_be_label: Label for after-tax simple breakeven result
        at_npv_be_label: Label for after-tax NPV breakeven result
        at_int_delta_label: Label for after-tax interest delta result
        npv_title_label: Label for NPV title
        five_yr_npv_label: Label for 5-year NPV result
        accel_section_frame: Frame for accelerated payoff section
        accel_section_label: Label for accelerated payoff section title
        accel_months_label: Label for accelerated months result
        accel_time_saved_label: Label for accelerated time saved result
        accel_interest_saved_label: Label for accelerated interest saved result
        current_cost_npv_label: Label for current total cost NPV result
        new_cost_npv_label: Label for new total cost NPV result
        cost_npv_advantage_label: Label for total cost NPV advantage result
        amort_curr_total_int: Label for amortization current total interest
        amort_new_total_int: Label for amortization new total interest
        amort_int_savings: Label for amortization interest savings
    """

    root: tk.Tk
    current_analysis: RefinanceAnalysis | None
    sensitivity_data: list[dict]
    holding_period_data: list[dict]
    amortization_data: list[dict]
    amortization_balance_chart: AmortizationChart | None
    current_amortization_schedule: list[dict]
    new_amortization_schedule: list[dict]
    current_balance: tk.StringVar
    current_rate: tk.StringVar
    current_remaining: tk.StringVar
    new_rate: tk.StringVar
    new_term: tk.StringVar
    closing_costs: tk.StringVar
    cash_out: tk.StringVar
    opportunity_rate: tk.StringVar
    marginal_tax_rate: tk.StringVar
    npv_window_years: tk.StringVar
    chart_horizon_years: tk.StringVar
    sensitivity_max_reduction: tk.StringVar
    sensitivity_step: tk.StringVar
    maintain_payment: tk.BooleanVar
    fred_api_key: str | None
    market_series_data: dict[str, list[tuple[datetime, float]]]
    market_series_errors: dict[str, str | None]
    market_cache_timestamps: dict[str, datetime | None]
    market_period_var: tk.StringVar
    market_chart: MarketChart | None
    market_tree: ttk.Treeview | None
    _market_status_label: ttk.Label | None
    _market_cache_indicator: ttk.Label | None
    _calc_canvas: tk.Canvas
    sens_tree: ttk.Treeview
    holding_tree: ttk.Treeview
    amort_tree: ttk.Treeview
    _background_canvas: tk.Canvas
    _help_canvas: tk.Canvas
    chart: SavingsChart
    pay_frame: ttk.Frame
    balance_frame: ttk.Frame
    current_pmt_label: ttk.Label
    new_pmt_label: ttk.Label
    savings_label: ttk.Label
    new_balance_label: ttk.Label
    cash_out_label: ttk.Label
    simple_be_label: ttk.Label
    npv_be_label: ttk.Label
    curr_int_label: ttk.Label
    new_int_label: ttk.Label
    int_delta_label: ttk.Label
    tax_section_label: ttk.Label
    at_current_pmt_label: ttk.Label
    at_new_pmt_label: ttk.Label
    at_savings_label: ttk.Label
    at_simple_be_label: ttk.Label
    at_npv_be_label: ttk.Label
    at_int_delta_label: ttk.Label
    npv_title_label: ttk.Label
    five_yr_npv_label: ttk.Label
    accel_section_frame: ttk.Frame
    accel_section_label: ttk.Label
    accel_months_label: ttk.Label
    accel_time_saved_label: ttk.Label
    accel_interest_saved_label: ttk.Label
    current_cost_npv_label: ttk.Label
    new_cost_npv_label: ttk.Label
    cost_npv_advantage_label: ttk.Label
    amort_curr_total_int: ttk.Label
    amort_new_total_int: ttk.Label
    amort_int_savings: ttk.Label

    def __init__(
        self,
        root: tk.Tk,
    ):
        """Initialize RefinanceCalculatorApp.

        Args:
            root: Root Tkinter window
        """
        self.root = root
        self.root.title("Refinance Breakeven Calculator")
        self.root.configure(bg="#f5f5f5")

        self.current_analysis: RefinanceAnalysis | None = None
        self.sensitivity_data: list[dict] = []
        self.holding_period_data: list[dict] = []
        self.amortization_data: list[dict] = []
        self.current_amortization_schedule: list[dict] = []
        self.new_amortization_schedule: list[dict] = []
        self.amortization_balance_chart: AmortizationChart | None = None

        self.current_balance = tk.StringVar(value="400000")
        self.current_rate = tk.StringVar(value="6.5")
        self.current_remaining = tk.StringVar(value="25")
        self.new_rate = tk.StringVar(value="5.75")
        self.new_term = tk.StringVar(value="30")
        self.closing_costs = tk.StringVar(value="8000")
        self.cash_out = tk.StringVar(value="0")
        self.opportunity_rate = tk.StringVar(value="5.0")
        self.marginal_tax_rate = tk.StringVar(value="0")

        self.npv_window_years = tk.StringVar(value="5")
        self.chart_horizon_years = tk.StringVar(value="10")
        self.sensitivity_max_reduction = tk.StringVar(value="2.5")
        self.sensitivity_step = tk.StringVar(value="0.125")
        self.maintain_payment = tk.BooleanVar(value=False)

        self.fred_api_key = os.getenv("FRED_API_KEY")
        self.market_series_data: dict[str, list[tuple[datetime, float]]] = {
            series_id: [] for _, series_id in MARKET_SERIES
        }
        self.market_series_errors: dict[str, str | None] = {
            series_id: None for _, series_id in MARKET_SERIES
        }
        self.market_cache_timestamps: dict[str, datetime | None] = {
            series_id: None for _, series_id in MARKET_SERIES
        }
        self.market_chart: MarketChart | None = None
        self.market_tree: ttk.Treeview | None = None
        self._market_status_label: ttk.Label | None = None
        self._market_cache_indicator: ttk.Label | None = None
        self.market_period_var = tk.StringVar(value=MARKET_DEFAULT_PERIOD)

        self._load_all_market_data(force=True)
        self._build_ui()
        self._calculate()

    def _build_ui(self):
        """Build the main UI components."""
        # Style notebook tabs so the active one stands out
        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=(12, 6))
        style.map("TNotebook.Tab", font=[("selected", ("Segoe UI", 9, "bold"))])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Main calculator (scrollable)
        main_tab = ttk.Frame(self.notebook, padding=0)
        self.notebook.add(main_tab, text="Calculator")

        self._calc_canvas = tk.Canvas(main_tab, highlightthickness=0)
        calc_scrollbar = ttk.Scrollbar(main_tab, orient="vertical", command=self._calc_canvas.yview)
        calc_scroll_frame = ttk.Frame(self._calc_canvas, padding=10)

        calc_scroll_frame.bind(
            "<Configure>",
            lambda e: self._calc_canvas.configure(scrollregion=self._calc_canvas.bbox("all")),
        )
        calc_canvas_window = self._calc_canvas.create_window(
            (0, 0),
            window=calc_scroll_frame,
            anchor="nw",
        )
        self._calc_canvas.configure(yscrollcommand=calc_scrollbar.set)

        def on_calc_canvas_configure(event):
            self._calc_canvas.itemconfig(calc_canvas_window, width=event.width)

        self._calc_canvas.bind("<Configure>", on_calc_canvas_configure)

        self._calc_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        calc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Analysis group: sensitivity + holding period
        analysis_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(analysis_tab, text="Analysis")
        self.analysis_notebook = ttk.Notebook(analysis_tab)
        self.analysis_notebook.pack(fill=tk.BOTH, expand=True)
        sens_tab = ttk.Frame(self.analysis_notebook, padding=10)
        holding_tab = ttk.Frame(self.analysis_notebook, padding=10)
        self.analysis_notebook.add(sens_tab, text="Rate Sensitivity")
        self.analysis_notebook.add(holding_tab, text="Holding Period")

        # Visuals group: amortization + chart
        visuals_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(visuals_tab, text="Loan Visualizations")
        self.visuals_notebook = ttk.Notebook(visuals_tab)
        self.visuals_notebook.pack(fill=tk.BOTH, expand=True)
        amort_tab = ttk.Frame(self.visuals_notebook, padding=10)
        chart_tab = ttk.Frame(self.visuals_notebook, padding=10)
        self.visuals_notebook.add(amort_tab, text="Amortization")
        self.visuals_notebook.add(chart_tab, text="Chart")

        # Market data tab
        market_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(market_tab, text="Market")
        build_market_tab(self, market_tab)
        self._populate_market_tab()

        # Options remain a top-level tab
        options_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(options_tab, text="Options")

        # Info group: background + help
        info_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(info_tab, text="Info")
        self.info_notebook = ttk.Notebook(info_tab)
        self.info_notebook.pack(fill=tk.BOTH, expand=True)
        background_tab = ttk.Frame(self.info_notebook, padding=10)
        help_tab = ttk.Frame(self.info_notebook, padding=10)
        self.info_notebook.add(background_tab, text="Background")
        self.info_notebook.add(help_tab, text="Help")

        build_main_tab(self, calc_scroll_frame)
        build_sensitivity_tab(self, sens_tab)
        build_holding_period_tab(self, holding_tab)
        build_amortization_tab(self, amort_tab)
        build_chart_tab(self, chart_tab)
        build_options_tab(self, options_tab)
        build_background_tab(self, background_tab)
        build_help_tab(self, help_tab)

        # Global mouse wheel handler that routes scrolling based on active tab
        def on_mousewheel(event):
            delta = int(-1 * (event.delta / 120))
            top_index = self.notebook.index(self.notebook.select())

            # Calculator tab
            if top_index == CALCULATOR_TAB_INDEX and hasattr(self, "_calc_canvas"):
                self._calc_canvas.yview_scroll(delta, "units")
            elif top_index == ANALYSIS_TAB_INDEX and hasattr(self, "analysis_notebook"):
                # Analysis tab
                sub_index = self.analysis_notebook.index(self.analysis_notebook.select())
                if sub_index == 0 and hasattr(self, "sens_tree"):
                    self.sens_tree.yview_scroll(delta, "units")
                elif sub_index == 1 and hasattr(self, "holding_tree"):
                    self.holding_tree.yview_scroll(delta, "units")
            elif top_index == VISUALS_TAB_INDEX and hasattr(self, "visuals_notebook"):
                # Visuals tab
                sub_index = self.visuals_notebook.index(self.visuals_notebook.select())
                if sub_index == 0 and hasattr(self, "amort_tree"):
                    self.amort_tree.yview_scroll(delta, "units")
                # Chart tab has no vertical scroll
            elif top_index == MARKET_TAB_INDEX and self.market_tree:
                self.market_tree.yview_scroll(delta, "units")
            elif top_index == INFO_TAB_INDEX and hasattr(self, "info_notebook"):
                # Info tab
                sub_index = self.info_notebook.index(self.info_notebook.select())
                if sub_index == 0 and hasattr(self, "_background_canvas"):
                    self._background_canvas.yview_scroll(delta, "units")
                elif sub_index == 1 and hasattr(self, "_help_canvas"):
                    self._help_canvas.yview_scroll(delta, "units")

        self.root.bind_all("<MouseWheel>", on_mousewheel)

    def _load_market_series(self, series_id: str, *, force: bool = False) -> None:
        """Fetch a named FRED series, reusing cache if it is still fresh."""
        now = datetime.now()
        cache_timestamp = self.market_cache_timestamps.get(series_id)
        cached_values = self.market_series_data.get(series_id)
        if (
            not force
            and cached_values
            and cache_timestamp
            and now - cache_timestamp < MARKET_CACHE_TTL
        ):
            logger.debug("Using cached market observation data for %s", series_id)
            self.market_series_errors[series_id] = None
            return

        if not self.fred_api_key:
            self.market_series_errors[series_id] = (
                "FRED_API_KEY is not configured; market history is disabled."
            )
            logger.info(
                "Skipping market fetch for %s: %s",
                series_id,
                self.market_series_errors[series_id],
            )
            return

        try:
            observations = fetch_fred_series(series_id, self.fred_api_key, limit=600)
        except RuntimeError as exc:
            logger.exception("Failed to fetch market rates from FRED for %s", series_id)
            self.market_series_errors[series_id] = f"Unable to load mortgage rate data: {exc}"
            return

        if not observations:
            self.market_series_errors[series_id] = (
                "FRED returned no observations for the selected series."
            )
            logger.warning(self.market_series_errors[series_id])
            return

        processed: list[tuple[datetime, float]] = []
        for date_str, value in observations:
            try:
                parsed = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue
            processed.append((parsed, value))

        self.market_series_data[series_id] = processed
        self.market_cache_timestamps[series_id] = now
        self.market_series_errors[series_id] = None

        if series_id == "MORTGAGE30US" and processed:
            latest_rate = processed[0][1]
            self.new_rate.set(f"{latest_rate:.3f}")

    def _load_all_market_data(self, *, force: bool = False) -> None:
        """Ensure every configured series has fresh data."""
        for _, series_id in MARKET_SERIES:
            self._load_market_series(series_id, force=force)

    def _refresh_market_data(self) -> None:
        """Refresh market rates and update the corresponding tab."""
        self._load_all_market_data(force=True)
        self._populate_market_tab()
        if self.market_series_data.get("MORTGAGE30US"):
            self._calculate()

    def _populate_market_tab(self) -> None:
        """Update the market tab tree with the latest observations."""
        if not self._market_status_label:
            return

        if self.market_tree:
            for row in self.market_tree.get_children():
                self.market_tree.delete(row)

            merged = self._merged_market_rows()
            for row in merged:
                self.market_tree.insert("", tk.END, values=row)

        if self.market_chart:
            chart_data = {
                label: self._filtered_series_data(series_id) for label, series_id in MARKET_SERIES
            }
            self.market_chart.plot(chart_data)

        self._update_market_status_display()

    def _market_period_months(self) -> int | None:
        """Return the selected period in months, using None for 'All'."""
        value = self.market_period_var.get()
        try:
            months = int(value)
        except (TypeError, ValueError):
            return None
        return None if months <= 0 else months

    def _filtered_series_data(self, series_id: str) -> list[tuple[datetime, float]]:
        """Return the rate observations truncated to the selected period."""
        rows = self.market_series_data.get(series_id, [])
        months = self._market_period_months()
        if not rows or months is None:
            return rows

        latest = rows[0][0]
        threshold = latest - timedelta(days=months * 30)
        return [row for row in rows if row[0] >= threshold]

    def _merged_market_rows(self) -> list[tuple[str, ...]]:
        """Combine each series into a table-ready row."""
        filtered_map = {
            series_id: self._filtered_series_data(series_id) for _, series_id in MARKET_SERIES
        }
        series_value_map: dict[str, dict[datetime, float]] = {
            series_id: {dt: rate for dt, rate in rows} for series_id, rows in filtered_map.items()
        }

        all_dates = sorted(
            {dt for rates in series_value_map.values() for dt in rates},
            reverse=True,
        )
        result: list[tuple[str, ...]] = []
        for dt in all_dates:
            row = [dt.strftime("%Y-%m-%d")]
            for _, series_id in MARKET_SERIES:
                rate = series_value_map.get(series_id, {}).get(dt)
                row.append(f"{rate:.3f}%" if rate is not None else "—")
            result.append(tuple(row))
        return result

    def _update_market_status_display(self) -> None:
        """Refresh the market status text and cache indicator for the selected series."""
        if not self._market_status_label:
            return

        parts: list[str] = []
        timestamps: list[datetime] = []
        for label, series_id in MARKET_SERIES:
            rows = self._filtered_series_data(series_id)
            error = self.market_series_errors.get(series_id)

            if not rows:
                parts.append(f"{label}: {error or 'unavailable'}")
                continue

            latest_date, latest_rate = rows[0]
            parts.append(f"{label}: {latest_rate:.3f}% ({latest_date:%Y-%m-%d})")
            timestamp = self.market_cache_timestamps.get(series_id)
            if timestamp:
                timestamps.append(timestamp)

        status_text = " | ".join(parts) if parts else "Market data is not available."
        if timestamps:
            latest_ts = max(timestamps)
            status_text += f" - refreshed {latest_ts:%Y-%m-%d %H:%M}"

        self._market_status_label.config(
            text=status_text,
            foreground="black" if parts else "red",
        )
        self._update_market_cache_indicator(max(timestamps) if timestamps else None)

    def _update_market_cache_indicator(self, timestamp: datetime | None = None) -> None:
        """Update the cache status indicator label below the Market tab header."""
        if not self._market_cache_indicator:
            return

        if timestamp is None:
            timestamps = [ts for ts in self.market_cache_timestamps.values() if ts is not None]
            timestamp = max(timestamps) if timestamps else None
        if not timestamp:
            self._market_cache_indicator.config(
                text="Cache: not populated",
                foreground="#666",
            )
            return

        age = datetime.now() - timestamp
        status = "fresh" if age < MARKET_CACHE_TTL else "stale"
        minutes = int(age.total_seconds() / 60)
        suffix = "just now" if minutes == 0 else f"{minutes} min ago"
        color = "green" if status == "fresh" else "orange"
        self._market_cache_indicator.config(
            text=f"Cache ({status}): {suffix}",
            foreground=color,
        )

    def _calculate(self) -> None:
        """Perform refinance analysis and update all results and charts."""
        try:
            npv_years = int(float(self.npv_window_years.get() or 5))
            chart_years = int(float(self.chart_horizon_years.get() or 10))
            sens_max = float(self.sensitivity_max_reduction.get() or 2.0)
            sens_step = float(self.sensitivity_step.get() or 0.25)

            params = {
                "current_balance": float(self.current_balance.get()),
                "current_rate": float(self.current_rate.get()) / 100,
                "current_remaining_years": float(self.current_remaining.get()),
                "new_rate": float(self.new_rate.get()) / 100,
                "new_term_years": float(self.new_term.get()),
                "closing_costs": float(self.closing_costs.get()),
                "cash_out": float(self.cash_out.get() or 0),
                "opportunity_rate": float(self.opportunity_rate.get()) / 100,
                "npv_window_years": npv_years,
                "chart_horizon_years": chart_years,
                "marginal_tax_rate": float(self.marginal_tax_rate.get() or 0) / 100,
                "maintain_payment": self.maintain_payment.get(),
            }

            self.current_analysis = analyze_refinance(**params)
            self._update_results(self.current_analysis, npv_years)

            current_rate_pct = float(self.current_rate.get())
            rate_steps = []
            r = sens_step
            max_scenarios = 20
            while r <= sens_max + 0.001 and len(rate_steps) < max_scenarios:
                new_rate = current_rate_pct - r
                if new_rate > 0:
                    rate_steps.append(new_rate / 100)
                r += sens_step

            self.sensitivity_data = run_sensitivity(
                params["current_balance"],
                params["current_rate"],
                params["current_remaining_years"],
                params["new_term_years"],
                params["closing_costs"],
                params["opportunity_rate"],
                rate_steps,
                npv_years,
            )
            self._update_sensitivity(npv_years)

            holding_periods = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20]
            self.holding_period_data = run_holding_period_analysis(
                params["current_balance"],
                params["current_rate"],
                params["current_remaining_years"],
                params["new_rate"],
                params["new_term_years"],
                params["closing_costs"],
                params["opportunity_rate"],
                params["marginal_tax_rate"],
                holding_periods,
                params["cash_out"],
            )
            self._update_holding_period()

            (
                current_schedule,
                new_schedule,
            ) = generate_amortization_schedule_pair(
                current_balance=params["current_balance"],
                current_rate=params["current_rate"],
                current_remaining_years=params["current_remaining_years"],
                new_rate=params["new_rate"],
                new_term_years=params["new_term_years"],
                closing_costs=params["closing_costs"],
                cash_out=params["cash_out"],
                maintain_payment=params["maintain_payment"],
            )
            self.current_amortization_schedule = current_schedule
            self.new_amortization_schedule = new_schedule

            self.amortization_data = generate_comparison_schedule(
                current_balance=params["current_balance"],
                current_rate=params["current_rate"],
                current_remaining_years=params["current_remaining_years"],
                new_rate=params["new_rate"],
                new_term_years=params["new_term_years"],
                closing_costs=params["closing_costs"],
                cash_out=params["cash_out"],
                maintain_payment=params["maintain_payment"],
            )
            self._update_amortization()
            self._update_amortization_balance_chart()

            self.chart.plot(
                self.current_analysis.cumulative_savings,
                self.current_analysis.npv_breakeven_months,
            )

        except ValueError:
            pass

    def _update_results(
        self,
        a: RefinanceAnalysis,
        npv_years: int = 5,
    ) -> None:
        """Update result labels based on the given analysis.

        Args:
            a: RefinanceAnalysis object with calculation results
            npv_years: NPV time horizon in years
        """

        def fmt(v: float) -> str:
            return f"${v:,.0f}"

        def fmt_months(m: float | None) -> str:
            if m is None:
                return "N/A"
            return f"{m:.0f} mo ({m / 12:.1f} yr)"

        self.current_pmt_label.config(text=fmt(a.current_payment))
        self.new_pmt_label.config(text=fmt(a.new_payment))

        savings_text = fmt(abs(a.monthly_savings))
        if a.monthly_savings >= 0:
            self.savings_label.config(text=f"-{savings_text}", foreground="green")
        else:
            self.savings_label.config(text=f"+{savings_text}", foreground="red")

        if a.cash_out_amount > 0:
            self.balance_frame.pack(fill=tk.X, pady=(0, 8), after=self.pay_frame)
            self.new_balance_label.config(text=fmt(a.new_loan_balance))
            self.cash_out_label.config(text=fmt(a.cash_out_amount), foreground="blue")
        else:
            self.balance_frame.pack_forget()

        self.simple_be_label.config(text=fmt_months(a.simple_breakeven_months))
        self.npv_be_label.config(text=fmt_months(a.npv_breakeven_months))

        self.curr_int_label.config(text=fmt(a.current_total_interest))
        self.new_int_label.config(text=fmt(a.new_total_interest))

        delta_text = fmt(abs(a.interest_delta))
        if a.interest_delta < 0:
            self.int_delta_label.config(text=f"-{delta_text}", foreground="green")
        else:
            self.int_delta_label.config(text=f"+{delta_text}", foreground="red")

        self.npv_title_label.config(text=f"{npv_years}-Year NPV of Refinancing")

        tax_rate_pct = float(self.marginal_tax_rate.get() or 0)
        self.tax_section_label.config(
            text=f"After-Tax Analysis ({tax_rate_pct:.0f}% marginal rate)",
        )

        self.at_current_pmt_label.config(text=fmt(a.current_after_tax_payment))
        self.at_new_pmt_label.config(text=fmt(a.new_after_tax_payment))

        at_savings_text = fmt(abs(a.after_tax_monthly_savings))
        if a.after_tax_monthly_savings >= 0:
            self.at_savings_label.config(text=f"-{at_savings_text}", foreground="green")
        else:
            self.at_savings_label.config(text=f"+{at_savings_text}", foreground="red")

        self.at_simple_be_label.config(text=fmt_months(a.after_tax_simple_breakeven_months))
        self.at_npv_be_label.config(text=fmt_months(a.after_tax_npv_breakeven_months))

        at_int_delta_text = fmt(abs(a.after_tax_interest_delta))
        if a.after_tax_interest_delta < 0:
            self.at_int_delta_label.config(text=f"-{at_int_delta_text}", foreground="green")
        else:
            self.at_int_delta_label.config(text=f"+{at_int_delta_text}", foreground="red")

        npv_text = fmt(abs(a.five_year_npv))
        if a.five_year_npv >= 0:
            self.five_yr_npv_label.config(text=f"+{npv_text}", foreground="green")
        else:
            self.five_yr_npv_label.config(text=f"-{npv_text}", foreground="red")

        # Accelerated payoff section
        if self.maintain_payment.get() and a.accelerated_months:
            self.accel_section_frame.pack(
                fill=tk.X,
                pady=(0, 8),
                before=self.npv_title_label.master,
            )

            years = a.accelerated_months / 12
            self.accel_months_label.config(text=f"{a.accelerated_months} mo ({years:.1f} yr)")

            if a.accelerated_time_savings_months:
                saved_years = a.accelerated_time_savings_months / 12
                self.accel_time_saved_label.config(
                    text=f"{a.accelerated_time_savings_months} mo ({saved_years:.1f} yr)",
                    foreground="green",
                )

            if a.accelerated_interest_savings:
                self.accel_interest_saved_label.config(
                    text=fmt(a.accelerated_interest_savings),
                    foreground="green",
                )
        else:
            self.accel_section_frame.pack_forget()

        # Total Cost NPV
        self.current_cost_npv_label.config(text=fmt(a.current_total_cost_npv))
        self.new_cost_npv_label.config(text=fmt(a.new_total_cost_npv))

        adv_text = fmt(abs(a.total_cost_npv_advantage))
        if a.total_cost_npv_advantage >= 0:
            self.cost_npv_advantage_label.config(text=f"+{adv_text}", foreground="green")
        else:
            self.cost_npv_advantage_label.config(text=f"-{adv_text}", foreground="red")

    def _update_sensitivity(
        self,
        npv_years: int = 5,
    ) -> None:
        """Update sensitivity analysis table.

        Args:
            npv_years: NPV time horizon in years
        """
        self.sens_tree.heading("npv_5yr", text=f"{npv_years}-Yr NPV")

        for row in self.sens_tree.get_children():
            self.sens_tree.delete(row)

        for row in self.sensitivity_data:
            simple = f"{row['simple_be']:.0f} mo" if row["simple_be"] else "N/A"
            npv = f"{row['npv_be']} mo" if row["npv_be"] else "N/A"
            self.sens_tree.insert(
                "",
                tk.END,
                values=(
                    f"{row['new_rate']:.2f}%",
                    f"${row['monthly_savings']:,.0f}",
                    simple,
                    npv,
                    f"${row['five_yr_npv']:,.0f}",
                ),
            )

    def _update_holding_period(self) -> None:
        """Update holding period analysis table."""
        for row in self.holding_tree.get_children():
            self.holding_tree.delete(row)

        for row in self.holding_period_data:
            tag = row["recommendation"].lower().replace(" ", "_")
            self.holding_tree.insert(
                "",
                tk.END,
                values=(
                    f"{row['years']} yr",
                    f"${row['nominal_savings']:,.0f}",
                    f"${row['npv']:,.0f}",
                    f"${row['npv_after_tax']:,.0f}",
                    row["recommendation"],
                ),
                tags=(tag,),
            )

        self.holding_tree.tag_configure("strong_yes", foreground="green")
        self.holding_tree.tag_configure("yes", foreground="darkgreen")
        self.holding_tree.tag_configure("marginal", foreground="orange")
        self.holding_tree.tag_configure("no", foreground="red")

    def _update_amortization(self) -> None:
        """Update amortization comparison table."""
        for row in self.amort_tree.get_children():
            self.amort_tree.delete(row)

        cumulative_curr_interest = 0
        cumulative_new_interest = 0
        cumulative_interest_diff = 0

        for row in self.amortization_data:
            cumulative_curr_interest += row["current_interest"]
            cumulative_new_interest += row["new_interest"]

            int_diff = row["interest_diff"]
            cumulative_interest_diff += int_diff
            tag = "savings" if int_diff < 0 else "cost"

            self.amort_tree.insert(
                "",
                tk.END,
                values=(
                    row["year"],
                    f"${row['current_principal']:,.0f}",
                    f"${row['current_interest']:,.0f}",
                    f"${row['current_balance']:,.0f}",
                    f"${row['new_principal']:,.0f}",
                    f"${row['new_interest']:,.0f}",
                    f"${row['new_balance']:,.0f}",
                    f"${int_diff:+,.0f}",
                    f"${cumulative_interest_diff:+,.0f}",
                ),
                tags=(tag,),
            )

        self.amort_tree.tag_configure("savings", foreground="green")
        self.amort_tree.tag_configure("cost", foreground="red")

        total_savings = cumulative_curr_interest - cumulative_new_interest

        self.amort_curr_total_int.config(text=f"${cumulative_curr_interest:,.0f}")
        self.amort_new_total_int.config(text=f"${cumulative_new_interest:,.0f}")

        if total_savings >= 0:
            self.amort_int_savings.config(text=f"${total_savings:,.0f}", foreground="green")
        else:
            self.amort_int_savings.config(text=f"-${abs(total_savings):,.0f}", foreground="red")

    def _update_amortization_balance_chart(self) -> None:
        """Update loan balance comparison chart."""
        if not self.amortization_balance_chart:
            return
        self.amortization_balance_chart.plot(
            self.current_amortization_schedule,
            self.new_amortization_schedule,
        )

    def _export_csv(self) -> None:
        """Export main analysis data to CSV file."""
        if not self.current_analysis:
            messagebox.showwarning("No Data", "Run a calculation first.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"refi_analysis_{datetime.now():%Y%m%d_%H%M%S}.csv",
        )
        if not filepath:
            return

        with open(filepath, "w", newline="") as f:
            w = csv.DictWriter(
                f,
                fieldnames=["new_rate", "monthly_savings", "simple_be", "npv_be", "five_yr_npv"],
            )
            w.writeheader()
            w.writerows(self.sensitivity_data)

        messagebox.showinfo("Exported", f"Saved to {filepath}")

    def _export_sensitivity_csv(self) -> None:
        """Export sensitivity analysis data to CSV file."""
        if not self.sensitivity_data:
            messagebox.showwarning("No Data", "Run a calculation first.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"refi_sensitivity_{datetime.now():%Y%m%d_%H%M%S}.csv",
        )
        if not filepath:
            return

        with open(filepath, "w", newline="") as f:
            w = csv.DictWriter(
                f,
                fieldnames=["new_rate", "monthly_savings", "simple_be", "npv_be", "five_yr_npv"],
            )
            w.writeheader()
            w.writerows(self.sensitivity_data)

        messagebox.showinfo("Exported", f"Saved to {filepath}")

    def _export_holding_csv(self) -> None:
        """Export holding period analysis data to CSV file."""
        if not self.holding_period_data:
            messagebox.showwarning("No Data", "Run a calculation first.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"refi_holding_period_{datetime.now():%Y%m%d_%H%M%S}.csv",
        )
        if not filepath:
            return

        with open(filepath, "w", newline="") as f:
            w = csv.DictWriter(
                f,
                fieldnames=["years", "nominal_savings", "npv", "npv_after_tax", "recommendation"],
            )
            w.writeheader()
            w.writerows(self.holding_period_data)

        messagebox.showinfo("Exported", f"Saved to {filepath}")

    def _export_amortization_csv(self) -> None:
        """Export amortization comparison data to CSV file."""
        if not self.amortization_data:
            messagebox.showwarning("No Data", "Run a calculation first.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"refi_amortization_{datetime.now():%Y%m%d_%H%M%S}.csv",
        )
        if not filepath:
            return

        with open(filepath, "w", newline="") as f:
            w = csv.DictWriter(
                f,
                fieldnames=[
                    "year",
                    "current_principal",
                    "current_interest",
                    "current_balance",
                    "new_principal",
                    "new_interest",
                    "new_balance",
                    "principal_diff",
                    "interest_diff",
                    "balance_diff",
                ],
            )
            w.writeheader()
            w.writerows(self.amortization_data)

        messagebox.showinfo("Exported", f"Saved to {filepath}")


def main() -> None:
    """Main driver function to run the refinance calculator app."""
    root = tk.Tk()
    root.geometry("1100x1040")
    root.resizable(True, True)
    root.minsize(940, 900)
    RefinanceCalculatorApp(root)
    root.mainloop()


__all__ = [
    "RefinanceCalculatorApp",
    "main",
]

__description__ = """
Tkinter UI for the refinance calculator application.
"""
