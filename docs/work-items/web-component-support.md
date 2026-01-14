# Work Item: Prepare Repository for Web Component Support

## Summary

Refactor the refi-calculator repository structure to support multiple interfaces
(GUI and web) while maintaining a shared core calculation library. This establishes
the foundation for a Streamlit-based web application without disrupting the existing
Tkinter GUI.

## Motivation

- Enable web-based access to the refinance calculator
- Keep calculation logic DRY across interfaces
- Maintain clean separation of concerns for easier maintenance
- Prepare for potential future monetization and deployment to Streamlit Community Cloud

## Current Structure Analysis

The repository already has reasonable separation:

- `src/refi_calculator/gui/` — Tkinter GUI code with tab builders
- `src/refi_calculator/market/` — FRED API integration
- `src/refi_calculator/calculations.py` — Core calculation logic
- `src/refi_calculator/models.py` — Data models
- `src/refi_calculator/chart.py`, `market_chart.py` — Visualization

**Key refactoring need:** Calculation logic and models are at the package root alongside UI code.
These should be isolated into a `core` module so the web interface can import them without
pulling in Tkinter dependencies.

## Requirements

### 1. Create Core Module

**1.1** Create `src/refi_calculator/core/` directory and migrate:

- `calculations.py` → `core/calculations.py`
- `models.py` → `core/models.py`
- `chart.py` → `core/charts.py` (shared chart data/logic) **and** retain any Tkinter-specific rendering helpers under `gui/` as needed so both modules can coexist without duplication

**1.2** Move `market/` under `core/` since FRED data fetching is shared:

- `market/fred.py` → `core/market/fred.py`

**1.3** Create `core/__init__.py` with clean public exports:

```python
from .calculations import (
    calculate_amortization,
    calculate_npv,
    # ... other public functions
)
from .models import LoanParameters, RefinanceResult  # etc.
```

### 2. Rename UI to GUI

**2.1** Rename `ui/` to `gui/` for consistency with dependency groups and terminology.

**2.2** Update all imports throughout the project:

```python
# Before
from refi_calculator.gui.app import main
from refi_calculator.calculations import ...

# After
from refi_calculator.gui.app import main
from refi_calculator.core import ...
```

**2.3** Keep GUI-specific code in `gui/`:

- `app.py`
- `builders/` (all tab builders)
- `helpers.py`
- `market_constants.py` (if GUI-specific)
- Tkinter-specific chart rendering

### 3. Create Web Module Placeholder

**3.1** Create `src/refi_calculator/web/` directory:

```txt
web/
├── __init__.py
└── app.py  # Placeholder with TODO comment
```

**3.2** Placeholder `app.py`:

```python
"""Streamlit web interface for refi-calculator."""
import streamlit as st

def main():
    st.title("Refinance Calculator")
    st.info("Web interface coming soon.")

if __name__ == "__main__":
    main()
```

### 4. Dependency Management

> **NOTE TO AGENT:** Do not modify `pyproject.toml`, `.env`, or `requirements.txt`.
> These have been manually configured by the maintainer.

The following dependencies have already been added:

**Optional dependency groups in `pyproject.toml`:**

- `[gui]` — GUI-specific dependencies
- `[web]` — `streamlit>=1.28.0`, `plotly>=5.18.0`
- `[dev]` — Development and testing dependencies

**`requirements.txt`** at repo root is configured for Streamlit Cloud deployment.

### 5. Update Entry Points

**5.1** Update `pyproject.toml` scripts:

```toml
[project.scripts]
refi-calculator = "refi_calculator.gui.app:main"
refi-calculator-web = "refi_calculator.web.app:main"
```

**5.2** Verify `bin/refi-calculator.py` still works or update it to call the new location.

### 6. Configuration and Secrets

> **NOTE TO AGENT:** Do not modify `.env`, `.gitignore`, or environment configuration files.
> These have been manually configured.

**6.1** `environment.py` already supports:

- Environment variables (for both local and Streamlit Cloud)
- `.env` file loading

**6.2** `.gitignore` already includes `.streamlit/secrets.toml`.

**6.3** FRED API key can be set via:

- `FRED_API_KEY` environment variable
- `.env` file
- Streamlit secrets (for web deployment)

### 7. Update Tests

**7.1** Add tests for core module imports:

```python
def test_core_imports_without_gui_deps():
    """Ensure core can be imported independently."""
    from refi_calculator.core import calculations
    from refi_calculator.core import models
```

**7.2** Reorganize test structure if needed:

```txt
tests/
├── core/
│   ├── test_calculations.py
│   └── test_models.py
├── gui/
│   └── test_builders.py  # If any
└── test_environment.py   # Existing
```

### 8. Documentation Updates

**8.1** Update README.md with:

- New project structure explanation
- Installation variants: `pip install .[gui]` vs `pip install .[web]`
- Instructions for running each interface

**8.2** Update AGENT.md with new module conventions.

## Target Structure

```txt
src/refi_calculator/
├── __init__.py
├── cli.py
├── environment.py
├── core/
│   ├── __init__.py
│   ├── calculations.py
│   ├── models.py
│   ├── charts.py          # Shared chart data generation
│   └── market/
│       ├── __init__.py
│       └── fred.py
├── gui/
│   ├── __init__.py
│   ├── app.py
│   ├── helpers.py
│   ├── chart.py           # Tkinter-specific rendering
│   ├── market_chart.py
│   ├── market_constants.py
│   └── builders/
│       └── ... (existing tabs)
└── web/
    ├── __init__.py
    └── app.py
```

## Acceptance Criteria

- [ ] Existing GUI launches and functions identically (`refi-calculator` command)
- [ ] `from refi_calculator.core import calculations, models` works
- [ ] Core module importable without matplotlib/Tkinter in environment
- [ ] `pip install .[web]` installs Streamlit dependencies
- [ ] `pip install .[gui]` installs GUI dependencies
- [ ] All existing tests pass
- [ ] No circular imports between core, gui, and web
- [ ] `python -m refi_calculator.web.app` runs placeholder Streamlit app
- [ ] FRED API key works via environment variable

## Out of Scope

- Implementing the full Streamlit web interface (separate work item)
- Deployment to Streamlit Community Cloud (separate work item)
- Authentication or payment integration

## Estimated Effort

Medium (3-5 hours) — primarily moving files and updating imports

## Dependencies

None — this is foundational work that unblocks web interface development
