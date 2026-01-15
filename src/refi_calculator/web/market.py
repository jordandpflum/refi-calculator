"""Market data helpers for the refinance calculator interface."""

from __future__ import annotations

from logging import getLogger
from typing import cast

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from refi_calculator.core.market.constants import MARKET_PERIOD_OPTIONS, MARKET_SERIES
from refi_calculator.core.market.fred import fetch_fred_series

logger = getLogger(__name__)

MARKET_CACHE_TTL_SECONDS = 15 * 60
MARKET_AXIS_YEAR_THRESHOLD_MONTHS = 24


def get_api_key() -> str | None:
    """Retrieve the FRED API key stored in Streamlit secrets."""
    return st.secrets.get("FRED_API_KEY")


@st.cache_data(ttl=MARKET_CACHE_TTL_SECONDS)
def _fetch_series(series_id: str, api_key: str) -> list[tuple[str, float]]:
    """Fetch a single series from FRED with caching.

    Args:
        series_id: FRED series identifier.
        api_key: API key to authenticate with FRED.

    Returns:
        List of (date, value) observations.
    """
    return fetch_fred_series(series_id, api_key)


def fetch_all_series(api_key: str) -> tuple[dict[str, list[tuple[str, float]]], list[str]]:
    """Retrieve all configured market series from FRED.

    Args:
        api_key: API key to authenticate with FRED.

    Returns:
        Tuple of raw series data and collection of error messages.
    """
    raw_series: dict[str, list[tuple[str, float]]] = {}
    errors: list[str] = []
    for label, series_id in MARKET_SERIES:
        try:
            observations = _fetch_series(series_id, api_key)
        except RuntimeError as exc:
            logger.exception("Failed to fetch %s series", label)
            errors.append(f"{label}: {exc}")
            observations = []
        raw_series[label] = observations
    return raw_series, errors


def _build_market_dataframe(
    raw_series: dict[str, list[tuple[str, float]]],
) -> pd.DataFrame:
    """Combine multiple FRED series into a Date-indexed DataFrame.

    Args:
        raw_series: Mapping of series labels to raw (date, value) observations.

    Returns:
        Combined DataFrame with Date index and one column per series.
    """
    frames: list[pd.DataFrame] = []
    for label, observations in raw_series.items():
        if not observations:
            continue
        df = pd.DataFrame(observations, columns=pd.Index(["Date", label]))
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)
        frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, axis=1).sort_index()


def _filter_market_dataframe(
    data: pd.DataFrame,
    months: int | None,
) -> pd.DataFrame:
    """Restrict the provided series to the most recent `months`.

    Args:
        data: Date-indexed DataFrame with market series.
        months: Number of trailing months to keep or None for full history.

    Returns:
        Filtered DataFrame.
    """
    if months is None or data.empty:
        return data

    last_date_raw = data.index.max()
    if last_date_raw is pd.NaT:
        return data
    last_date = cast(pd.Timestamp, last_date_raw)
    cutoff = last_date - pd.DateOffset(months=months)
    return data.loc[data.index >= cutoff]


def _segment_months(value: str) -> int | None:
    """Convert the UI option value into a number of months.

    Args:
        value: Selected option value.

    Returns:
        Number of months or None for full history.
    """
    if value == "0":
        return None
    return int(value)


def _render_market_chart(data: pd.DataFrame) -> None:
    """Render the market series chart with optimized axes.

    Args:
        data: Date-indexed DataFrame with market series.
    """
    if data.empty:
        return

    melted = data.reset_index().melt("Date", var_name="Series", value_name="Rate")
    min_rate = melted["Rate"].min()
    max_rate = melted["Rate"].max()
    span = max_rate - min_rate
    padding = max(span * 0.05, 0.1)
    lower = max(min_rate - padding, 0)
    upper = max_rate + padding

    first_date_raw = data.index.min()
    last_date_raw = data.index.max()
    if first_date_raw is pd.NaT or last_date_raw is pd.NaT:
        return
    first_date = cast(pd.Timestamp, first_date_raw)
    last_date = cast(pd.Timestamp, last_date_raw)
    date_span = cast(pd.Timedelta, last_date - first_date)
    months = date_span.days / 30
    use_year_only = months >= MARKET_AXIS_YEAR_THRESHOLD_MONTHS
    date_format = "%Y" if use_year_only else "%b %Y"

    fig = go.Figure()
    for label, group in melted.groupby("Series"):
        fig.add_trace(
            go.Scatter(
                x=group["Date"],
                y=group["Rate"],
                mode="lines",
                name=label,
                hovertemplate="Date=%{x|%b %Y}<br>Series=%{text}<br>Rate=%{y:.2f}%<extra></extra>",
                text=[label] * len(group),
            ),
        )

    xaxis_kwargs: dict[str, object] = {
        "title": "Date",
        "tickformat": date_format,
        "tickangle": 0 if use_year_only else -45,
    }
    if use_year_only:
        start_year = int(first_date.year)
        end_year = int(last_date.year)
        xaxis_kwargs.update(
            {
                "tickmode": "array",
                "tickvals": [
                    pd.Timestamp(year=y, month=1, day=1) for y in range(start_year, end_year + 1)
                ],
            },
        )
    else:
        xaxis_kwargs["tickmode"] = "auto"

    fig.update_layout(
        xaxis=xaxis_kwargs,
        yaxis=dict(
            title="Rate (%)",
            range=[lower, upper],
        ),
        legend=dict(title="Series"),
        margin=dict(t=5, b=30, l=50, r=10),
        hovermode="x",
    )

    st.plotly_chart(fig, use_container_width=True)


def render_market_tab() -> None:
    """Render the market data tab with metrics, range selector, chart, and table."""
    st.subheader("Market Data")

    api_key = get_api_key()
    if not api_key:
        st.warning(
            "Add your FRED API key to `st.secrets['FRED_API_KEY']` to view mortgage rate history.",
        )
        return

    raw_series, errors = fetch_all_series(api_key)
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
    latest_timestamp_raw = latest_valid.index.max()
    if latest_timestamp_raw is pd.NaT:
        st.info("Market data lacks recent observations.")
        return
    latest_date = cast(pd.Timestamp, latest_timestamp_raw).date()
    st.markdown(
        f"**Current rates (latest available as of {latest_date:%Y-%m-%d})**",
    )
    if not latest.empty:
        metric_cols = st.columns(len(latest))
        for col, (label, value) in zip(metric_cols, latest.items()):
            col.metric(label, f"{value:.2f}%")

    options = [label for label, _ in MARKET_PERIOD_OPTIONS]
    option_mapping = {label: value for label, value in MARKET_PERIOD_OPTIONS}
    period_label = st.radio(
        "Range",
        options,
        horizontal=True,
        key="market_period",
    )
    period_months = _segment_months(option_mapping[period_label])

    market_df = _filter_market_dataframe(market_df_all, period_months)
    if market_df.empty:
        st.info("Filtered market data is not available for the selected range.")
        return

    _render_market_chart(market_df)

    table = market_df.sort_index(ascending=False).head(12).reset_index()
    table["Date"] = table["Date"].dt.date
    st.dataframe(table, width="stretch")


logger.debug("Market helpers module initialized.")

__all__ = [
    "render_market_tab",
    "get_api_key",
]

__description__ = """
Helpers for fetching FRED data, rendering the market chart, and displaying latest rates.
"""
