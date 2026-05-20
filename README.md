# Tekmera Explorer

A command-line tool for analyzing exported blueprint JSON files from automation platforms — currently **Workfront Fusion** and **Make.com**. The platform is detected automatically from the blueprint structure.

Tekmera Explorer produces summary reports, diffs, and text searches across one or many blueprints, in table, JSON, or HTML form.

## Install

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

This installs the `tekmera` command on your PATH.

## Commands

```bash
# Summary report for a single blueprint
tekmera report blueprints/blueprint-14926.json

# Search across blueprints (file or directory; recurses up to 3 levels)
tekmera search blueprints/ "PI43"
tekmera search blueprints/ "PI\d+" --regex
tekmera search blueprints/ "term1" "term2"          # OR logic across queries

# Diff two blueprints
tekmera diff blueprints/old.json blueprints/new.json

# Sample report (no input needed — useful for demos/docs)
tekmera demo --platform workfront_fusion
tekmera demo --platform make_com --format html
```

Every command accepts `--format {table|json|html}` (default `table`). HTML reports are written to `reports/`.

Run `tekmera --help` or `tekmera <command> --help` for full option lists.

## Supported platforms

| Platform | Module naming | Auto-detected from |
|----------|--------------|--------------------|
| Workfront Fusion | `workfront-service:action` | Module ID patterns |
| Make.com | `service:action`, `builtin:action` | Module ID patterns |

Blueprints are JSON exports from the respective platforms. See `CLAUDE.md` for the structural differences and sample shapes.

## Development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pip install -r requirements-dev.txt
```

Common tasks:

```bash
pytest tests/ -v                                    # Run tests
black src tests && isort src tests                  # Format
flake8 src/ --extend-ignore=E203,W503,E501,F541     # Lint
mypy src/                                           # Type check
./scripts/build.sh                                  # Build single-file binary
```

## Project structure

```
src/tekmera/
├── functions/   # Pure functional analysis engine (auto-detects platform)
├── reporting/   # Composes function outputs into summary + diff reports
└── clients/cli/ # Click-based CLI and table/JSON/HTML formatters
```

For more detail on package relationships and the projection dispatch model, see `docs/architecture/README.md`.

## License

See `LICENSE`.
