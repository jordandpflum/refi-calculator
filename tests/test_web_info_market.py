"""Tests for the web info and market helpers."""

from __future__ import annotations

import pandas as pd
import pytest


def test_render_info_tab_emits_sections(reload_web_module: callable, streamlit_stub) -> None:
    """Info tab rendering writes every section via Streamlit markdown."""

    module = reload_web_module("refi_calculator.web.info")
    streamlit_stub.calls.clear()

    module.render_info_tab()

    assert any(call[0] == "markdown" for call in streamlit_stub.calls)
    assert any(call[0] == "divider" for call in streamlit_stub.calls)


def test_segment_months_converts_values() -> None:
    """Tab selector values convert to month counts."""

    from refi_calculator.web.market import _segment_months

    assert _segment_months("0") is None
    assert _segment_months("12") == 12


def test_build_market_dataframe_combines_series() -> None:
    """Raw series data merge into a single DataFrame."""

    from refi_calculator.web.market import _build_market_dataframe

    raw_series = {
        "Series A": [("2024-01-01", 3.0)],
        "Series B": [("2024-01-01", 4.0)],
    }
    frame = _build_market_dataframe(raw_series)

    assert "Series A" in frame.columns
    assert "Series B" in frame.columns
    assert not frame.empty
    assert frame.index[0] == pd.Timestamp("2024-01-01")


def test_filter_market_dataframe_truncates_months() -> None:
    """Filtered views only include the most recent months when requested."""

    from refi_calculator.web.market import _filter_market_dataframe

    dates = pd.date_range("2023-01-01", periods=6, freq="MS")
    df = pd.DataFrame({"Series": range(6)}, index=dates)

    filtered = _filter_market_dataframe(df, months=3)

    assert len(filtered) == 4


def test_fetch_all_series_handles_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """When fetching fails, errors are collected and observations default to empty."""

    from refi_calculator.web.market import fetch_all_series

    def fake_fetch(series_id: str, api_key: str) -> list[tuple[str, float]]:
        if series_id.endswith("ZERO"):
            raise RuntimeError("boom")
        return [("2024-01-01", 3.5)]

    monkeypatch.setattr("refi_calculator.web.market.MARKET_SERIES", [("Good", "GOOD"), ("Bad", "ZERO")])
    monkeypatch.setattr("refi_calculator.web.market._fetch_series", fake_fetch)
    data, errors = fetch_all_series("key")

    assert isinstance(data, dict)
    assert errors
    assert any("boom" in err for err in errors)


def test_render_market_chart_calls_plotly(reload_web_module: callable, streamlit_stub) -> None:
    """Rendering the market chart pushes a Plotly figure to Streamlit.

    Args:
        reload_web_module: Fixture to load the web module with stubbed Streamlit.
        streamlit_stub: Stub used to capture Plotly/chart calls.
    """

    module = reload_web_module("refi_calculator.web.market")
    dates = pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01"])
    df = pd.DataFrame(
        {"Series": [1.0, 2.0, 3.0]},
        index=dates,
    )
    df.index.name = "Date"
    streamlit_stub.calls.clear()

    module._render_market_chart(df)

    assert any(call[0] == "plotly_chart" for call in streamlit_stub.calls)
