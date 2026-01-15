# Refi Calculator

Refi Calculator is a multi-interface toolkit that helps homeowners and finance professionals
evaluate refinancing decisions. The package blends a full-featured Tkinter GUI with a Streamlit
placeholder for future web delivery, a CLI entry point, and a core analytics library so every
interface relies on consistent calculations.

## Key Capabilities

- **Side-by-side loan comparisons** for current vs. proposed mortgages covering nominal
  payments, after-tax analysis, and amortization.
- **Decision support** such as breakeven and holding-period tables, plus accelerated payoff
  scenarios that keep target payments constant.
- **Insightful visualizations** via the Tkinter tabbed UI: refreshed cumulative savings chart,
  loan balance comparison, and the amortization table that highlights cumulative interest deltas.
- **Market intelligence** when the `FRED_API_KEY` is provided: historical 30-year fixed rates,
  live default refinance estimates, and dual-tenor comparison tables.
- **Export-ready data** for every tab so downstream tools or reports can consume precise CSV
  exports.

## Quick Links & Navigation

| Destination | Description |
| --- | --- |
| **User Guide** | Guides for installing, configuring, and using the GUI or web experience. |
| **API Reference** | Auto-generated reference for the core analytics library under `reference/`. |
| **Codebase Overview** | Key modules live under `src/refi_calculator/`, including `core/`, `gui/`, and `web/`. |
| **Automation/Entry Points** | Entry scripts under `bin/` for CLI launches and PowerShell wrappers. |

Use the navigation pane (Home, User Guide, API Reference) to jump into each document or explore
the generated reference pages from `docs/gen_ref_pages.py`.

## Environment & Entry Points

1. **Runtime requirements**: Python 3.13+, Poetry-managed dependencies, and an optional `.venv/`
   for isolation.
2. **GUI launch**: `poetry run refi-calculator` (the console script wires into
   `refi_calculator.gui.app:main`).
3. **Hosted Streamlit experience**: Visit [https://refi-calculator.streamlit.app/](https://refi-calculator.streamlit.app/)
   for the hosted preview powered by the Streamlit placeholder layers.
4. **Web placeholder**: enable `[web]` extras and run `poetry run refi-calculator-web` to start
   `streamlit run src/refi_calculator/web/app.py` and continue iterating toward the future web UI.
5. **CLI scaffolding**: `src/refi_calculator/cli.py` and `bin/refi-calculator.py` share logging and
   configuration plumbing for command-line workflows.

## Development & Quality

- **Testing**: `poetry run pytest` (tests live under `tests/` following `test_*.py`).
- **Pre-commit checks**: `poetry run pre-commit run --all-files` keeps formatting (Black, Ruff,
  isort) and linting in sync.
- **Documentation generation**: `mkdocs` powers static sites with plugins for search, literate
  navigation, and mkdocstrings referencing `src/`.
- **Versioning and releases**: use conventional commits (`feat`, `fix`, `docs`, etc.) and keep
  changelog entries in `CHANGELOG.md` aligned with PyPI releases.

## Contribution Guidance

- Update docs (`docs/guide.md` and `docs/index.md`) whenever behavior changes or new capabilities
  are added.
- Keep feature branches focused; run targeted tests locally and ensure all relevant hooks pass
  before opening a pull request.
- For automation updates (PowerShell scripts, bin scripts), preserve the structure outlined in
  `AGENTS.md` and mirror logging/transcript behavior.
- Refer to `AGENTS.md` for standards on module headers, docstrings, logging, and error handling so
  every Python module stays consistent.

## Next Steps

- Dive into the **User Guide** to see detailed workflows for using the GUI, enabling the market
  tab, and contributing safely.
- Browse **API Reference** for individual plot builders, calculators, and models exposed under
  `src/refi_calculator/core/`.
- Run `docs/gen_ref_pages.py` when you add new modules so the reference site stays current.
