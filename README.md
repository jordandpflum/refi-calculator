# Refi-Calculator

Refi-Calculator helps borrowers analyze whether refinancing makes sense by comparing current and
proposed loan terms through breakeven, NPV, amortization, and holding-period views inside a Tkinter
GUI.

## Features

- Side-by-side analysis of current vs. proposed mortgage payments (nominal and after-tax)
- Breakeven and holding-period tables with clear recommendations
- Accelerated payoff planning for maintaining current payment levels
- Visual amortization comparisons plus cumulative savings (nominal/NPV) chart
- Exportable CSV data for every tab

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

### Running the GUI

```bash
poetry run python bin/refi-calculator.py
```

The script boots the Tkinter application (`src/refi_calculator/ui/app.py`) that ties together all the
analysis helpers.

## Testing & Quality

- `poetry run pre-commit run --all-files` (runs formatting, linting, safety hooks, etc.)
- `poetry run pytest` (not yet populated, but ready for future tests)

Add new tests under `tests/` following the `test_*.py` pattern whenever you enhance functionality.

## Code Structure

- `src/refi_calculator/models.py`: Dataclasses for `LoanParams` and `RefinanceAnalysis`.
- `src/refi_calculator/calculations.py`: All refinance math helpers (NPV, amortization,
  sensitivity, etc.).
- `src/refi_calculator/ui/`: Tkinter GUI composed of:
    - `app.py`: The main application wiring.
    - `chart.py`: Custom savings chart canvas.
    - `builders/`: Tab-specific builders and helpers for clean separation of UI concerns.
- `bin/refi-calculator.py`: Entry point that runs the GUI.

## Contributing

- Keep imports grouped by functionality (allow isort to do the heavy lifting through pre-commit).
- Update or add tests in `tests/` before opening a pull request.
- Run `poetry run pre-commit run --all-files` to catch formatting/lint issues early.

## License

See [LICENSE.txt](LICENSE.txt) for licensing details.
