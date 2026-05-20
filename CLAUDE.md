# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Tekmera Explorer is a command-line tool for analyzing exported blueprint JSON files from automation platforms (Workfront Fusion and Make.com). It reads blueprint JSON, projects it through a pure-functional analysis engine, and emits summary reports, diff reports, and cross-blueprint search results in table, JSON, or HTML form.

## Architecture

Three top-level packages under `src/tekmera/`:

- **`functions/`** — Pure functional analysis engine. Platform-aware (auto-detected). No side effects, no dependencies on other tekmera packages. Entry point: `tekmera.functions.project(category, subcategory, function, input, **kwargs)`.
- **`reporting/`** — Composes `functions/` outputs into structured `summary` and `diff` reports.
- **`clients/cli/`** — Click-based CLI and output formatters (table/JSON/HTML).

See `docs/architecture/README.md` for the longer description of package relationships and the dispatch model.

## Current CLI Commands

```bash
tekmera report blueprint.json                              # Summary report for a single blueprint
tekmera search ./blueprints/ "query"                       # Search text content across blueprints
tekmera diff blueprint1.json blueprint2.json               # Compare two blueprints
tekmera demo --platform workfront_fusion                   # Sample report (for demos/docs)
tekmera demo --platform make_com --format html             # Sample Make.com HTML report
```

All commands accept `--format {table|json|html}`. HTML output is written into `reports/`.

## Development Commands

### Environment Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pip install -r requirements-dev.txt
```

### Code Quality

```bash
black src tests
isort src tests
flake8 src/ --extend-ignore=E203,W503,E501,F541
mypy src/
```

### Testing

```bash
pytest tests/ -v --cov=tekmera --cov-report=term-missing
```

### Binary Build

```bash
./scripts/build.sh
# Or directly:
pyinstaller --onefile --name tekmera-test-local src/tekmera/__main__.py
```

## Blueprint Data Structure and Examples

Blueprint JSON files live under `blueprints/`:

- **`blueprints/*.json`** — Workfront Fusion examples
- **`blueprints/make/*.blueprint.json`** — Make.com examples
- **`blueprints/CLIENTS/`** — Real client exports (not for redistribution)

### Workfront Fusion Structure

```json
{
  "name": "Scenario Name",
  "flow": [
    {
      "id": 1,
      "module": "workfront-workfront:searchv3",
      "routes": [{"flow": [...]}],
      "onerror": [...]
    }
  ],
  "metadata": {
    "designer": {
      "orphans": [[...]]
    }
  }
}
```

### Make.com Structure

```json
{
  "name": "Scenario Name",
  "flow": [
    {
      "id": 1,
      "module": "builtin:BasicRouter",
      "routes": [{"flow": [...]}],
      "filter": {
        "name": "Filter Name",
        "conditions": [[...]]
      }
    }
  ]
}
```

### Key Differences

- **Workfront Fusion**: `workfront-service:action` module naming
- **Make.com**: `service:action` or `builtin:action` module naming
- **Make.com Routers**: specifically `builtin:BasicRouter`
- **Make.com Filters**: attached to individual modules, not separate components

## Code Style

- Black, 100-character line length
- isort with black profile
- Flake8 (ignores E203, W503, E501, F541)
- Type hints with mypy

## Testing Strategy

- pytest with coverage
- Tests under `tests/functions/` mirror the `src/tekmera/functions/` tree
- Security scanning with bandit
- Dependency auditing with pip-audit

## Entry Points

- CLI entry: `src/tekmera/clients/cli/main.py:main()`
- PyInstaller entry: `src/tekmera/__main__.py`
- Package script: `tekmera` (defined in `pyproject.toml`)
