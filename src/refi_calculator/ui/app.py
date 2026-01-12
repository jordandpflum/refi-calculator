"""Refinance breakeven GUI components."""

from __future__ import annotations

import csv
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from ..calculations import (
    analyze_refinance,
    generate_comparison_schedule,
    run_holding_period_analysis,
    run_sensitivity,
)
from ..models import RefinanceAnalysis
from .builders.analysis_tab import build_holding_period_tab, build_sensitivity_tab
from .builders.info_tab import build_background_tab, build_help_tab
from .builders.main_tab import build_main_tab
from .builders.options_tab import build_options_tab
from .builders.visuals_tab import build_amortization_tab, build_chart_tab

# ruff: noqa: PLR0915, PLR0912

CALCULATOR_TAB_INDEX = 0
ANALYSIS_TAB_INDEX = 1
VISUALS_TAB_INDEX = 2
INFO_TAB_INDEX = 4


class RefinanceCalculatorApp:
    """Refinance Calculator Application."""

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
        self.sensitivity_max_reduction = tk.StringVar(value="2.0")
        self.sensitivity_step = tk.StringVar(value="0.25")
        self.maintain_payment = tk.BooleanVar(value=False)

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
        self.notebook.add(visuals_tab, text="Visuals")
        self.visuals_notebook = ttk.Notebook(visuals_tab)
        self.visuals_notebook.pack(fill=tk.BOTH, expand=True)
        amort_tab = ttk.Frame(self.visuals_notebook, padding=10)
        chart_tab = ttk.Frame(self.visuals_notebook, padding=10)
        self.visuals_notebook.add(amort_tab, text="Amortization")
        self.visuals_notebook.add(chart_tab, text="Chart")

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
            elif top_index == INFO_TAB_INDEX and hasattr(self, "info_notebook"):
                # Info tab
                sub_index = self.info_notebook.index(self.info_notebook.select())
                if sub_index == 0 and hasattr(self, "_background_canvas"):
                    self._background_canvas.yview_scroll(delta, "units")
                elif sub_index == 1 and hasattr(self, "_help_canvas"):
                    self._help_canvas.yview_scroll(delta, "units")

        self.root.bind_all("<MouseWheel>", on_mousewheel)

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
            while r <= sens_max + 0.001:
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

            self.chart.plot(
                self.current_analysis.cumulative_savings,
                self.current_analysis.npv_breakeven_months,
            )

        except ValueError:
            pass

    def _update_results(self, a: RefinanceAnalysis, npv_years: int = 5) -> None:
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

        for row in self.amortization_data:
            cumulative_curr_interest += row["current_interest"]
            cumulative_new_interest += row["new_interest"]

            int_diff = row["interest_diff"]
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
    root.geometry("640x840")
    root.resizable(True, True)
    root.minsize(560, 720)
    RefinanceCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

__all__ = ["RefinanceCalculatorApp", "main"]

__description__ = """
Tkinter UI for the refinance calculator application.
"""
