"""Tests for GUI builder helpers using tkinter stubs."""

from __future__ import annotations

from tests.gui_stubs import (
    DummyButton,
    DummyTreeview,
    DummyTtkWidget,
)


class DummyVar:
    """Minimal stand-in for Tk variable objects that exposes get/set semantics."""

    def __init__(self, value: object | None = None) -> None:
        self._value = value

    def get(self) -> object | None:
        return self._value

    def set(self, value: object) -> None:
        self._value = value


class DummyApp:
    """Minimal RefIner app surface required by builder helpers."""

    def __init__(self) -> None:
        self.sens_tree: DummyTreeview | None = None
        self.holding_tree: DummyTreeview | None = None
        self.current_balance = DummyVar("100000")
        self.current_rate = DummyVar("5.0")
        self.current_remaining = DummyVar("20")
        self.new_rate = DummyVar("4.5")
        self.new_term = DummyVar("30")
        self.closing_costs = DummyVar("3000")
        self.cash_out = DummyVar("0")
        self.market_period_var = DummyVar("1")
        self.chart_horizon_years = DummyVar("10")
        self.npv_window_years = DummyVar("5")
        self.sensitivity_max_reduction = DummyVar("2.0")
        self.sensitivity_step = DummyVar("0.25")
        self.opportunity_rate = DummyVar("5.0")
        self.marginal_tax_rate = DummyVar("0.0")
        self.maintain_payment = DummyVar(False)
        self.chart = None
        self.amortization_balance_chart = None
        self.amort_tree = None
        self.market_tree = None
        self.market_chart = None
        self._background_canvas = None
        self._help_canvas = None
        self._market_status_label = None
        self._market_cache_indicator = None
        self.call_log: list[str] = []

    def _calculate(self) -> None:
        self.call_log.append("calculate")

    def _export_csv(self) -> None:
        self.call_log.append("export_csv")

    def _populate_market_tab(self) -> None:
        self.call_log.append("populate_market_tab")

    def _refresh_market_data(self) -> None:
        self.call_log.append("refresh_market_data")

    def _export_amortization_csv(self) -> None:
        self.call_log.append("export_amortization_csv")

    def _export_sensitivity_csv(self) -> None:
        self.call_log.append("export_sensitivity_csv")

    def _export_holding_csv(self) -> None:
        self.call_log.append("export_holding_csv")


def test_build_sensitivity_tab_configures_tree(reload_gui_module: callable) -> None:
    """Sensitivity tab builder wires the tree columns and export button."""

    module = reload_gui_module("refi_calculator.gui.builders.analysis_tab")
    app = DummyApp()
    parent = object()
    DummyButton.instances.clear()

    module.build_sensitivity_tab(app, parent)

    tree = app.sens_tree
    assert tree is not None
    assert tree.columns == ("rate", "savings", "simple_be", "npv_be", "npv_5yr")
    assert tree.headings["rate"] == "New Rate"
    assert tree.headings["npv_5yr"] == "5-Yr NPV"
    assert tree.column_configs["rate"]["anchor"] == "center"
    assert DummyButton.instances[-1].command == app._export_sensitivity_csv


def test_build_holding_period_tab_populates_columns(reload_gui_module: callable) -> None:
    """Holding tab builder sets up columns and hooks the export button."""

    module = reload_gui_module("refi_calculator.gui.builders.analysis_tab")
    app = DummyApp()
    parent = object()
    DummyButton.instances.clear()

    module.build_holding_period_tab(app, parent)

    tree = app.holding_tree
    assert tree is not None
    assert tree.columns[0] == "years"
    assert tree.headings["recommendation"] == "Recommendation"
    assert "width" in tree.column_configs["recommendation"]
    assert DummyButton.instances[-1].command == app._export_holding_csv


def test_build_background_and_help_tabs_initialize_scrollable_canvases(
    reload_gui_module: callable,
) -> None:
    """Background/help tabs create scrollable canvases with bindings."""

    module = reload_gui_module("refi_calculator.gui.builders.info_tab")
    app = DummyApp()
    parent = DummyTtkWidget()

    module.build_background_tab(app, parent)
    module.build_help_tab(app, parent)

    assert app._background_canvas is not None
    assert app._help_canvas is not None
    assert any(op[0] == "create_window" for op in app._background_canvas.operations)
    assert any(op[0] == "bind" for op in app._background_canvas.operations)
    assert any(op[0] == "create_window" for op in app._help_canvas.operations)


def test_build_main_tab_sets_results_and_buttons(reload_gui_module: callable) -> None:
    """Main calculator tab populates result labels and connects the buttons."""

    module = reload_gui_module("refi_calculator.gui.builders.main_tab")
    app = DummyApp()
    parent = DummyTtkWidget()

    module.build_main_tab(app, parent)

    assert app.current_pmt_label is not None
    assert app.simple_be_label is not None
    assert app.pay_frame is not None
    assert DummyButton.instances[-2].command == app._calculate
    assert DummyButton.instances[-1].command == app._export_csv


def test_build_market_tab_populates_tree_and_chart(reload_gui_module: callable) -> None:
    """Market tab registers chart/tree widgets and refresh command."""

    module = reload_gui_module("refi_calculator.gui.builders.market_tab")
    app = DummyApp()
    parent = DummyTtkWidget()

    module.build_market_tab(app, parent)

    assert app.market_chart is not None
    assert app.market_tree is not None
    assert "date" in app.market_tree.columns
    assert DummyButton.instances[-1].command == app._refresh_market_data
    assert isinstance(app._market_status_label, DummyTtkWidget)
    assert isinstance(app._market_cache_indicator, DummyTtkWidget)


def test_build_options_tab_attaches_apply_button(reload_gui_module: callable) -> None:
    """Options builder wires default entries and the recalculate button."""

    module = reload_gui_module("refi_calculator.gui.builders.options_tab")
    app = DummyApp()
    parent = DummyTtkWidget()
    DummyButton.instances.clear()

    module.build_options_tab(app, parent)

    assert DummyButton.instances[-1].command == app._calculate
    assert any(
        isinstance(widget, DummyTtkWidget) and widget.kwargs.get("text") == "Application Options"
        for widget in DummyTtkWidget.instances
    )


def test_build_visuals_tab_sets_tree_and_charts(reload_gui_module: callable) -> None:
    """Visuals tab creates amortization tree, summary, and chart canvases."""

    module = reload_gui_module("refi_calculator.gui.builders.visuals_tab")
    app = DummyApp()
    parent = DummyTtkWidget()
    DummyButton.instances.clear()

    module.build_amortization_tab(app, parent)

    assert app.amort_tree is not None
    assert "curr_balance" in app.amort_tree.columns
    assert DummyButton.instances[-1].command == app._export_amortization_csv

    module.build_chart_tab(app, parent)

    assert getattr(app, "chart", None) is not None
    assert getattr(app, "amortization_balance_chart", None) is not None
    assert DummyTtkWidget.instances[-1].operations


__all__ = [
    "test_build_sensitivity_tab_configures_tree",
    "test_build_holding_period_tab_populates_columns",
]
