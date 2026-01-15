# User Guide

This guide walks through installing, configuring, and operating Refi Calculator across the GUI,
web placeholder, and supporting tooling. Follow the sections below in order, or jump straight to
the workflow that matches your role (borrower, analyst, or maintainer).

## Project Intent

Refi Calculator is a decision-support suite for borrowers who want to understand how a refinance
offer stacks up against an existing mortgage. The GUI layers clear comparisons, visualizations,
and forecasts on top of a single analytics core, so every view (breakeven, holding period,
amortization, or savings chart) relies on consistent rules, taxation assumptions, and payoff math.

## Installation & Environment Setup

1. **System requirements**
   - Python 3.13 or newer.
   - Poetry for dependency resolution and virtual environment management.
   - A shell capable of activating the generated `.venv/` in the project root (standard on macOS/
     Linux).
2. **Bootstrap the project**

   ```bash
   poetry install
   ```

   This command installs runtime and development dependencies, generates the virtual environment,
   and registers Git hooks declared in `.pre-commit-config.yaml`.
3. **Optional extras**
   - Install GUI-only requirements via `pip install .[gui]` (already included when running `poetry
     install`).
   - Add the web placeholder dependencies with `pip install .[web]` to bring in Streamlit and
     front-end helpers.
4. **Environment variables**
   - Provide `FRED_API_KEY` to enable the Market tab to refresh historical 30-year fixed rates from
     the Federal Reserve Economic Data (FRED) API. The key populates tables and the default
     refinance rate.

## Running the Tkinter GUI

1. **Launch command**

   ```bash
   poetry run refi-calculator
   ```

   The `refi-calculator` console script routes to `refi_calculator.gui.app:main`, which initializes
   the tabs, logging, and data exporters.
2. **GUI layout highlights**
   - **Overview tab**: Compares current and proposed loans using nominal and after-tax payments
     while surfacing an early decision recommendation.
   - **Breakeven tab**: Shows when tax-adjusted savings justify the refinance. Use the table
     filters to focus on different holding periods.
   - **Holding Period tab**: Projects payments over discrete horizons so you can model shorter
     timeframes.
   - **Loan Visualizations tab**: Displays the amortization table (with cumulative interest delta
     column), the refreshed cumulative savings chart, and the new balance comparison chart for
     both loans.
   - **Market tab**: When `FRED_API_KEY` exists, the tab pulls the latest 30-year fixed data,
     toggles between tenors (15Y/30Y), and pre-fills the refinance rate. If the API call fails or
     the key is absent, the UI logs the skip but keeps other tabs operational.
3. **Exporting insights**
   Every tab includes a CSV export button. Use this to feed spreadsheets or downstream analytics
   with the exact rows shown in the table.

## Running the Streamlit Web Placeholder

1. **Install extras**: `pip install .[web]` (if not already part of `poetry install`).
2. **Launch command**

   ```bash
   poetry run refi-calculator-web
   ```

   This command invokes `streamlit run src/refi_calculator/web/app.py`, giving you a browser-based
   preview of the future web experience while retaining centralized configuration logic. The same
   Streamlit workflow also hosts at [https://refi-calculator.streamlit.app/](https://refi-calculator.streamlit.app/)
   for a zero-install, shareable showcase.
3. **Behavior**
   The placeholder mirrors the GUI's core calculations but simplifies interactions for rapid
   prototyping. Expect limited functionality while the Streamlit UI continues to evolve.

## CLI & Automation Considerations

- The CLI entry point `refi_calculator.cli` centralizes logging configuration, verbosity controls,
  and optional JSON config loading. Use `bin/refi-calculator.py` for scriptable hooks or automation
  wrappers.
- PowerShell scripts inside `automation/` follow the structure described in `AGENTS.md`, including
  transcript logging, repository management, Poetry activation, and safe cleanup.

## Data, Logs, and Troubleshooting

- **Market data**: If historical data is unavailable, the Market tab reports the reason via the GUI
  log window and gracefully disables the missing dataset. Always verify `FRED_API_KEY` formatting
  and connectivity when the tab reports stale data.
- **Logging**: Related modules use `logging.getLogger(__name__)`; check the console output when you
  encounter inconsistent calculations or GUI launch failures.
- **Exception handling**: The core follows the `logger.exception(...); raise` pattern whenever an
  unexpected condition occurs, keeping tracebacks accessible for maintainers.

## Testing & Quality Assurance

- Run `poetry run pytest` to execute tests under `tests/` (expand coverage as functionality grows).
- Use `poetry run pre-commit run --all-files` to ensure formatting and linting (Black, Ruff, etc.)
  remain consistent with project policy.
- Add tests whenever you introduce calculations or UI logic; align file names with `test_*.py` and
  place shared fixtures in the appropriate `conftest.py` files.

## Contributions & Release Readiness

1. **Workflow**
   - Branch from `main`, keep changes focused, and describe your work with a conventional commit
     message (`feat`, `fix`, `docs`, etc.).
   - Update `CHANGELOG.md` when you ship features or fixes that users should notice.
2. **Documentation**
   - Refresh `docs/guide.md` or `docs/index.md` whenever behavior changes or new interfaces emerge.
   - Regenerate auto reference pages with `python docs/gen_ref_pages.py` if you add new modules.
3. **Publishing**
   - After review and testing, `poetry publish` targets PyPI releases (the project already publishes
     via GitHub Actions using the CI workflow described in `README.md`).

## Additional Resources

- `README.md` for a quick overview, feature list, and install instructions.
- `AGENTS.md` for code standards, logging practices, docstring expectations, and CLI patterns.
- `docs/reference/` (auto-generated) for developer-facing API details.
- `mkdocs.yml` + `docs/gen_ref_pages.py` for how the static documentation site builds itself.
