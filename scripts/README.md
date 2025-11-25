# Development Scripts

This directory contains development, testing, and build scripts for Tekmera Explorer.

## Available Scripts

### `./scripts/build-and-test.sh`
**Complete build and test pipeline** - Runs full test suite, quality checks, and binary build.

```bash
# Full pipeline (tests + build)
./scripts/build-and-test.sh

# Tests only (skip binary build)
./scripts/build-and-test.sh --skip-build

# Build only (skip tests)
./scripts/build-and-test.sh --skip-tests

# Verbose output
./scripts/build-and-test.sh --verbose

# Custom coverage requirement
./scripts/build-and-test.sh --coverage 90

# Show help
./scripts/build-and-test.sh --help
```

**Features:**
- ✅ Auto-formatting (black, isort, autoflake)
- ✅ Linting (flake8)
- ✅ Security scanning (bandit)
- ✅ Dependency audit (pip-audit) 
- ✅ Type checking (mypy)
- ✅ Test suite with coverage reporting
- ✅ Package import validation
- ✅ Binary build and testing
- ✅ Comprehensive build reports

### `./scripts/test.sh`
**Quick test runner** - Fast test execution for development cycles.

```bash
# Run quick tests
./scripts/test.sh
```

**Features:**
- ✅ Quick code formatting
- ✅ Test suite with coverage
- ✅ Fast feedback for development

### `./scripts/build.sh`
**Binary-only build** - Creates production binary without running tests.

```bash
# Build binary only
./scripts/build.sh
```

**Features:**
- ✅ Quality checks
- ✅ Binary creation with PyInstaller
- ✅ Binary functionality testing

## Development Workflow

### Quick Development Cycle
```bash
# Make code changes
vim src/tekmera/...

# Quick test
./scripts/test.sh

# Continue development...
```

### Complete Validation
```bash
# Before committing/releasing
./scripts/build-and-test.sh

# Check coverage report
open htmlcov/index.html

# Review security scan
cat bandit-report.json
```

### CI/CD Pipeline
```bash
# Full pipeline with high coverage requirement
./scripts/build-and-test.sh --coverage 85 --verbose
```

## Manual Development Setup

If you prefer manual setup:

```bash
# Setup development environment
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Install additional tools
pip install pyinstaller bandit pip-audit flake8 autoflake

# Run individual tools
pytest tests/ -v --cov=tekmera
black src/ tests/ --line-length 100
isort src/ tests/ --profile black
flake8 src/ tests/ --extend-ignore=E203,W503,E501,F541
mypy src/ --ignore-missing-imports
bandit -r src/
pip-audit
```

## Build Outputs

### Test Results
- **Coverage Report**: `htmlcov/index.html` - Interactive HTML coverage report
- **Coverage Data**: `.coverage` - Raw coverage data
- **Test Cache**: `.pytest_cache/` - Pytest cache files

### Build Artifacts  
- **Binary**: `dist/tekmera` - Production executable
- **Build Info**: `dist/build-info.txt` - Detailed build information
- **Temp Files**: `build/` - PyInstaller temporary files

### Quality Reports
- **Security Scan**: `bandit-report.json` - Security vulnerability report
- **Type Check**: Console output from mypy

## Environment Requirements

- **Python**: 3.10+ (defined in pyproject.toml)
- **Virtual Environment**: Strongly recommended
- **Git**: For commit information in build reports
- **Platform**: Cross-platform (Linux, macOS, Windows)

## Troubleshooting

### Virtual Environment Issues
```bash
# Create new venv if needed
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Permission Issues
```bash
# Make scripts executable
chmod +x scripts/*.sh
```

### Import Issues
```bash
# Verify package structure
pip install -e .
python -c "import tekmera; print('✅ Package imports working')"
```

### Coverage Issues
```bash
# Run with lower coverage requirement
./scripts/build-and-test.sh --coverage 60
```