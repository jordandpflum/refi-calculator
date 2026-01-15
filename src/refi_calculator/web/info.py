"""Background and help content shared on the informational tab."""

from __future__ import annotations

from logging import getLogger

import streamlit as st

logger = getLogger(__name__)

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


def render_info_tab() -> None:
    """Render background and help guidance content."""
    st.subheader("Background")
    for title, text in BACKGROUND_SECTIONS:
        st.markdown(f"**{title}**")
        st.markdown(text)
    st.subheader("Help")
    for title, text in HELP_SECTIONS:
        st.markdown(f"**{title}**")
        st.markdown(text)


logger.debug("Info tab helpers initialized.")

__all__ = ["render_info_tab"]

__description__ = """
Background and help guidance for the refinance calculator experience.
"""
