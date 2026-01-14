# Refi-Calculator

![CI](https://github.com/jordandpflum/refi-calculator/actions/workflows/ci.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/refi-calculator)
![Python](https://img.shields.io/pypi/pyversions/refi-calculator)
![License](https://img.shields.io/pypi/l/refi-calculator)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)

Refi-Calculator helps borrowers analyze whether refinancing makes sense by comparing current and
proposed loan terms through breakeven, NPV, amortization, and holding-period views inside a Tkinter
GUI.

## Features

- Side-by-side analysis of current vs. proposed mortgage payments (nominal and after-tax)
- Breakeven and holding-period tables with clear recommendations
- Accelerated payoff planning for maintaining current payment levels
- Loan Visualizations tab with the amortization comparison table (including cumulative interest Δ)
  plus the refreshed cumulative savings chart (ticks, zero-line label) and a new balance comparison
  chart for current vs. new loans
- Exportable CSV data for every tab
- Live market tab (when `FRED_API_KEY` is configured) surfaces historical 30-year fixed
  rates and pre-fills the refinance rate so you start with a realistic benchmark.
- Interactive history chart in the Market tab plus the value table below it with 30Y/15Y
  toggles for quick comparisons.

## Getting Started

### Requirements

- Python 3.13+
- Poetry for dependency management (the virtual environment lives in `.venv/`)

### Installation

```bash
poetry install
```

This command creates the virtual environment, installs dependencies, and prepares the hooks defined
in `.pre-commit-config.yaml`.

For a global CLI install, use `pipx` once the package is published, or run a local install with:

```bash
pipx install refi-calculator
# or (for development)
pip install -e .
```

### Running the GUI

```bash
poetry run refi-calculator
```

The `refi-calculator` console script launches the Tkinter application
(`src/refi_calculator/ui/app.py`) without invoking Python manually. When installed globally the
command is available directly from the shell, and when running from the repository the same command
can be executed via `poetry run`.

## Testing & Quality

- `poetry run pre-commit run --all-files` (runs formatting, linting, safety hooks, etc.)
- `poetry run pytest` (not yet populated, but ready for future tests)

### Market Data Tab

- Set the `FRED_API_KEY` environment variable to pull historical 30-year fixed-rate data when
  you launch the app. The Market tab will populate a refreshable table and update the default
  refinance rate using the latest observation. If the key is missing or the FRED request fails,
  the tab keeps working but reports the reason for the skip.
- Use the selectors inside the Market section to start with one year of history or extend the view
  to two years, five years, or all available data. The chart overlays both tenors with a legend,
  and the table below shows one column per tenor for the selected time window.

Add new tests under `tests/` following the `test_*.py` pattern whenever you enhance functionality.

## Code Structure

- `src/refi_calculator/models.py`: Dataclasses for `LoanParams` and `RefinanceAnalysis`.
- `src/refi_calculator/calculations.py`: All refinance math helpers (NPV, amortization,
  sensitivity, etc.).
- `src/refi_calculator/ui/`: Tkinter GUI composed of:
    - `app.py`: The main application wiring.
    - `chart.py`: Custom savings chart canvas.
    - `builders/`: Tab-specific builders and helpers for clean separation of UI concerns.
- `src/refi_calculator/cli.py`: CLI launcher exposed via the `refi-calculator` console script.
- `bin/refi-calculator.py`: Entry point that runs the GUI.

## Contributing

- Keep imports grouped by functionality (allow isort to do the heavy lifting through pre-commit).
- Update or add tests in `tests/` before opening a pull request.
- Run `poetry run pre-commit run --all-files` to catch formatting/lint issues early.

## License

See [LICENSE.txt](LICENSE.txt) for licensing details.
