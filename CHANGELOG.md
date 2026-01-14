# Changelog

## [0.6.0]

- Split shared calculations, models, and chart helpers into the new `refi_calculator.core`
  package so non-GUI clients can import the refinance logic without dragging in optional UI
  dependencies, plus added a lightweight import test to guard that split.
- Added `gui` and `web` extras, point the `refi-calculator` console script at the Tkinter GUI, and
  introduced a `refi-calculator-web` script that launches the Streamlit placeholder via the
  official CLI so the upcoming web interface can be exercised with the proper extras.
- Installed `--all-extras` in every workflow/install step and documented the Streamlit placeholder
  requirements to keep CI builds and future web packaging aligned.

## [0.5.8]

- Added `permissions.contents: write` to the executables workflow upload job so the built
  binaries can be published back to the GitHub release from CI.

## [0.5.7]

- Updated the release workflow to use a PAT for artifact uploads and switched the Windows
  build step to `poetry install --no-plugins` so installs finish faster without optional
  plugin hooks.

## [0.5.6]

- Removed the unnecessary `poetry config virtualenvs.prefer-active-python` setting so the
  executables workflow can rely on Poetry’s defaults for virtual environments.

## [0.5.5]

- Configured Poetry cache and virtualenv paths on Windows and allowed the upload job to
  run via `workflow_dispatch`, while dropping the redundant cache configuration step.

## [0.5.4]

- Let the build workflow respond to every release event (no manual type filter) and pointed
  Poetry’s cache directory to the workspace to improve install performance.

## [0.5.3]

- Removed the `cache: "poetry"` flags from the setup-python steps and made the executable
  builder trigger on both `created` and `published` release events to cover all releases.

## [0.5.2]

- Added a Windows executable build workflow that packages `refi-calculator` with PyInstaller
  and uploads it as an artifact, and allowed the CLI to report a version from `REFI_VERSION`.

## [0.5.1]

- Gave the release workflow explicit `contents: write` permissions so CI can tag and publish
  releases without permission failures.

## [0.5.0]

- Bumped the release pipeline to Python 3.13, install Poetry before `poetry install`, and
  documented the Apache Software License classifier for the project metadata.

## [0.4.0]

- Expanded the Loan Visualizations section by renaming the tab, adding a cumulative interest
  delta column, and including both the enhanced cumulative savings chart (with axis ticks and
  zero-line label) and a new amortization balance comparison chart so users can see how both loans
  evolve over time.
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
