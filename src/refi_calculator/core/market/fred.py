"""FRED API helpers for borrowing-rate data."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request


def fetch_fred_series(
    series_id: str,
    api_key: str,
    limit: int | None = None,
) -> list[tuple[str, float]]:
    """Fetch a stationary FRED series and return (date, value) pairs.

    Args:
        series_id: FRED series identifier (e.g., "MORTGAGE30US").
        api_key: Your FRED API key.
        limit: Maximum number of observations to fetch. Defaults to the service limit.

    Returns:
        Observations sorted newest-first, (date, float value).
    """
    params: dict[str, str] = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "desc",
    }
    if limit:
        params["limit"] = str(limit)

    url = f"https://api.stlouisfed.org/fred/series/observations?{urllib.parse.urlencode(params)}"

    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            payload = json.load(resp)
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as exc:
        raise RuntimeError("Failed to fetch FRED series") from exc

    observations = payload.get("observations", [])
    results: list[tuple[str, float]] = []
    for obs in observations:
        date = obs.get("date")
        value = obs.get("value")
        if date is None or value is None or value == ".":
            continue
        try:
            parsed = float(value)
        except ValueError:
            continue
        results.append((date, parsed))
    return results


__all__ = ["fetch_fred_series"]

__description__ = """
Helpers for retrieving FRED economic series.
"""
