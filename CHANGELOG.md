# Changelog

## [Unreleased]

- Load configuration early by reading any `.env` file before spawning the UI so CLI scripts can
  inject runtime variables without touching the host environment.

## [0.3.0]

- Added a standard-library CLI launcher (`refi_calculator.cli`) that exposes `refi-calculator` with
  `argparse`, logging, and version reporting so the GUI is easier to start from shell scripts.
- Registered the console script through `[project.scripts]` and documented the new install/run flow
  so `poetry run refi-calculator` (or `pipx install refi-calculator`) launches the app directly.
- Switched the project metadata to the SPDX `Apache-2.0` expression with `license-files` to remove
  the deprecated poetry warnings and keep the packaging clean.

## [0.2.0]

- Added a refreshed Market tab with a combined 30y/15y legend-driven chart plus a multi-column table.
- Cached FRED rate fetches (15-minute TTL) with manual refresh and cache status indicator.
- Introduced range selectors (1y default plus 2y, 5y, all) so the graph/table can show longer spans.
- Documented the API key requirement and new time-range controls.
