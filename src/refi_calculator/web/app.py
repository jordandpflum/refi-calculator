"""Streamlit web interface for the refinance calculator."""

from __future__ import annotations

from logging import getLogger

import streamlit as st

from refi_calculator.core.models import RefinanceAnalysis
from refi_calculator.web.calculator import (
    CalculatorInputs,
    collect_inputs,
    prepare_auxiliary_data,
    run_analysis,
)
from refi_calculator.web.info import render_info_tab
from refi_calculator.web.market import render_market_tab
from refi_calculator.web.results import (
    render_analysis_tab,
    render_options_tab,
    render_results,
    render_visuals_tab,
)

logger = getLogger(__name__)


def main() -> None:
    """Render the refinance calculator Streamlit application."""
    logger.debug("Rendering Streamlit refinance calculator main screen.")
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
        inputs = collect_inputs()
        analysis = run_analysis(inputs)
        render_results(inputs, analysis)

    if inputs is None or analysis is None:
        return

    sensitivity_data, holding_period_data, amortization_data = prepare_auxiliary_data(inputs)

    with analysis_tab:
        render_analysis_tab(inputs, sensitivity_data, holding_period_data)

    with visuals_tab:
        render_visuals_tab(analysis, amortization_data)

    with market_tab:
        render_market_tab()

    with options_tab:
        render_options_tab(inputs)

    with info_tab:
        render_info_tab()


if __name__ == "__main__":
    main()


__all__ = ["main"]

__description__ = """
Streamlit app wiring that mirrors the desktop refinance calculator experience.
"""
