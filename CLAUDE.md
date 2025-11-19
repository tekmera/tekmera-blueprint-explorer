# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Tekmera Explorer is a professional command-line tool for analyzing exported blueprint JSON files from multiple automation platforms. It provides comprehensive diagnostic capabilities including interactive exploration, AI-powered insights, and cross-blueprint analysis with a freemium licensing model.

## Development Commands

### Environment Setup
```bash
# First-time setup
./scripts/setup-dev.sh

# Daily development workflow 
source venv/bin/activate
tekmera init  # Setup credentials if not done
./scripts/run-dev.sh analyze ./blueprints
```

### Code Quality and CI
```bash
# Auto-fix code issues and run all checks
./scripts/check-dev.sh

# Skip tests during development
./scripts/check-dev.sh --skip-tests
```

### Testing
```bash
# Run tests with coverage
pytest tests/ -v --cov=tekmera --cov-report=term-missing

# Run specific test module
pytest tests/test_core/ -v
```

### Linting and Formatting
```bash
# Auto-format code (done by check-dev.sh)
black src tests
isort src tests
autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive src/

# Manual linting check
flake8 src/ --extend-ignore=E203,W503,E501,F541
```

### Binary Build
```bash
# Test binary build
pyinstaller --onefile --name tekmera-test-local src/tekmera/__main__.py
```

## Architecture

### Core Components

- **`src/tekmera/core/`**: Blueprint parsing and module analysis
  - `parser.py`: JSON parsing, module extraction from nested flows/routes/error handlers  
  - `analyzer.py`: Field extraction and module analysis

- **`src/tekmera/interfaces/cli/`**: Command-line interfaces
  - `main.py`: Main CLI entry point with click commands
  - `interactive.py`: Interactive menu system with feature gating
  - `explorer.py`: Module-by-module scenario exploration
  - `search.py`: Cross-blueprint search capabilities
  - `trace.py`: Live scenario walkthrough (premium)

- **`src/tekmera/analysis/`**: Analysis engines  
  - `corpus_analyzer.py`: Cross-blueprint analysis and reporting
  - `connections.py`: Connection environment analysis
  - `flow_tracer.py`: Execution flow tracing
  - `flow_walker.py`: Live scenario walkthrough engine


- **`src/tekmera/comparison/`**: Blueprint comparison tools
  - `diff_engine.py`: Main diff interface
  - `detailed_diff.py`: Module-level change detection  
  - `simple_diff.py`: Basic diff utilities

- **`src/tekmera/config/`**: Configuration and feature management
  - `menu_system.py`: Centralized menu configuration with feature gating

- **`src/tekmera/infra/`**: Infrastructure and licensing
  - `license.py`: Core license management and validation
  - `license_ui.py`: License user interface components
  - `lemon_squeezy.py`: Lemon Squeezy API integration

### Key Architectural Patterns

1. **Modular CLI**: Click-based command structure with subcommands for different features
2. **Interactive Menus**: InquirerPy-based menu system with rich formatting
3. **Feature Gating**: Premium features automatically enabled based on license status
4. **Recursive Parsing**: Blueprint parser handles nested flows, routes, and error handlers

### Blueprint Data Structure

Automation platform blueprints are JSON files. Workfront Fusion blueprints use this structure:
```json
{
  "name": "Scenario Name",
  "flow": [
    {
      "id": 1,
      "module": "workfront-workfront:searchv3", 
      "routes": [{"flow": [...]}],  // Nested flows
      "onerror": [...]  // Error handler flows
    }
  ],
  "metadata": {
    "designer": {
      "orphans": [[...]]  // Disconnected modules
    }
  }
}
```

### License Integration

- Simple local licensing system without external dependencies  
- Premium features are gated but gracefully degrade to free functionality
- CLI commands: `tekmera license status|activate|deactivate|local`
- License data stored in `~/.tekmera/license.json` with machine fingerprinting
- Local pro mode: Set `TEKMERA_LOCAL_PRO=true` for development/testing
- License key format: `TEKMERA-PRO-{edition}-{hash}`

### Configuration Management

- **New `init` command**: Interactive setup wizard for credentials
- **Secure storage**: Credentials stored in `~/.tekmera/config.json` (mode 600)
- **Automatic detection**: License and OpenAI keys read from config or environment
- **Fallback support**: Environment variables still work if config not available
- **Config manager**: `src/tekmera/config/config_manager.py` handles all credential management

### Development Workflow

1. Make changes to source code
2. Run `./scripts/check-dev.sh` to auto-fix and validate
3. Test with `./scripts/run-dev.sh analyze ./blueprints`
4. Run specific tests if needed
5. Commit when all checks pass

### Code Style

- Black formatting with 100 character line length
- isort for import sorting with black profile
- Flake8 linting (ignores E203, W503, E501, F541)
- Type hints enforced with mypy (warnings only during development)
- Auto-removal of unused imports/variables with autoflake

### Testing Strategy

- pytest with coverage reporting
- Tests organized by module: `test_core/`, `test_analysis/`, etc.
- Binary build testing in CI
- License integration testing
- Security scanning with bandit
- Dependency auditing with pip-audit

## Entry Points

- CLI entry: `src/tekmera/interfaces/cli/main.py:main()`
- PyInstaller entry: `src/tekmera/__main__.py`
- Package script: `tekmera` command defined in pyproject.toml