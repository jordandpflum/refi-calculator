# Changelog

## [0.9.2](https://github.com/jordandpflum/refi-calculator/compare/v0.9.1...v0.9.2) (2026-01-16)


### Bug Fixes

* **ci:** Adjust package name ([#42](https://github.com/jordandpflum/refi-calculator/issues/42)) ([9e02d60](https://github.com/jordandpflum/refi-calculator/commit/9e02d60c7b2e09993a950777a3dc211bc6a2f7c7))
* **ci:** Fix Release Pipeline ([#39](https://github.com/jordandpflum/refi-calculator/issues/39)) ([1214974](https://github.com/jordandpflum/refi-calculator/commit/12149745cf502f3908750b7abd8deb390e670ecd))
* **ci:** fix toml affecting release pipeline ([#41](https://github.com/jordandpflum/refi-calculator/issues/41)) ([b6e80f4](https://github.com/jordandpflum/refi-calculator/commit/b6e80f4803dab3526ea69757c0436a17fee74e6d))

## [0.9.1](https://github.com/jordandpflum/refi-calculator/compare/v0.9.0...v0.9.1) (2026-01-16)


### Bug Fixes

* **ci:** fix automated release process ([#37](https://github.com/jordandpflum/refi-calculator/issues/37)) ([f971e34](https://github.com/jordandpflum/refi-calculator/commit/f971e343f61acb27664dea1da1f4facb9f57f7f3))

## [0.9.0](https://github.com/jordandpflum/refi-calculator/compare/v0.8.0...v0.9.0) (2026-01-16)


### Features

* **ci:** add automated release workflow ([#29](https://github.com/jordandpflum/refi-calculator/issues/29)) ([c503d7b](https://github.com/jordandpflum/refi-calculator/commit/c503d7b034e65dcc06eea8c99400cb518656e6fe))


### Bug Fixes

* **ci:** Fix release pipeline V3 ([#33](https://github.com/jordandpflum/refi-calculator/issues/33)) ([11d21a4](https://github.com/jordandpflum/refi-calculator/commit/11d21a485942666c93e9f112b63f36a7c7cfa909))
* **ci:** remove deprecated input ([#35](https://github.com/jordandpflum/refi-calculator/issues/35)) ([cbf9b47](https://github.com/jordandpflum/refi-calculator/commit/cbf9b47ec016424ae55e35b9a79fc0bb621ee9f2))
* **ci:** Remove release summary ([#34](https://github.com/jordandpflum/refi-calculator/issues/34)) ([b3e8bfc](https://github.com/jordandpflum/refi-calculator/commit/b3e8bfc5c2d735f27df356460e2a93254260d160))
* Fix failing release pipeline ([#31](https://github.com/jordandpflum/refi-calculator/issues/31)) ([2a32681](https://github.com/jordandpflum/refi-calculator/commit/2a326814c970782f2fd15f76edae29731ff29aa0))
* fix release pipeline summary step V2 ([#32](https://github.com/jordandpflum/refi-calculator/issues/32)) ([6aa6ca6](https://github.com/jordandpflum/refi-calculator/commit/6aa6ca60552a4ce40bfbc0d4744cc0e487f112a0))


### Documentation

* **readme:** remove duplicate test badge from README ([#36](https://github.com/jordandpflum/refi-calculator/issues/36)) ([cc5a976](https://github.com/jordandpflum/refi-calculator/commit/cc5a976d402a8a1bbfa7e053311c7bb0ad93af18))

## [0.8.0]

- Added a MkDocs-powered documentation site. Generated API reference, guide,
  and index pages keep the online docs and README badge accurate.
- Added a `docs` workflow that installs dependencies via Poetry and publishes the MkDocs site.
  The workflow aligns with the hosted docs link used in the README.
  It also matches the Streamlit preview instructions.
- Centralized GUI tab builders behind a `builders` package export.
  Updated the chart classes to accept `tk.Misc` parents so typing is clearer and reuse is easier.
- Expanded docs tooling by adding `mkdocs`, `mkdocstrings`, and literate navigation dependencies.
  Introduced helper scripts that auto-generate reference pages from `src/`.

## [0.7.1]

- Refactored market constants into `refi_calculator.core.market.constants`.
  Both the GUI and Streamlit web placeholder now consume a single source of truth.
  This covers tenor options and the default period.

## [0.7.0]

- Tuned the executables builder so it runs only on `release` events marked `published`.
  The CI workflow now runs on every pull request regardless of branch to broaden validation.

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

- Added a refreshed Market tab with a combined 30y/15y legend-driven chart.
- Also added a multi-column table to show the expanded data.
- Cached FRED rate fetches (15-minute TTL) with manual refresh and cache status indicator.
- Introduced range selectors (1y default plus 2y, 5y, all) so the graph/table can show longer spans.
- Documented the API key requirement and new time-range controls.
