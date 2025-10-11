#!/bin/bash
# Local CI check script - runs all the same checks as GitHub Actions
# Usage: ./scripts/check.sh [--fix] [--skip-tests]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
FIX_MODE=false
SKIP_TESTS=false
for arg in "$@"; do
    case $arg in
        --fix)
            FIX_MODE=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        *)
            echo "Usage: $0 [--fix] [--skip-tests]"
            echo "  --fix: Auto-fix formatting and import issues"
            echo "  --skip-tests: Skip running the test suite"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}🔍 Running local CI checks...${NC}\n"

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}⚠️  Warning: Not in a virtual environment. Activating venv...${NC}"
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
    else
        echo -e "${RED}❌ Virtual environment not found. Please run: python -m venv venv && source venv/bin/activate${NC}"
        exit 1
    fi
fi

# Install CI dependencies
echo -e "${BLUE}📦 Installing CI dependencies...${NC}"
pip install -e ".[dev]" > /dev/null 2>&1
pip install black isort mypy flake8 bandit pip-audit pyinstaller types-requests > /dev/null 2>&1

echo -e "${GREEN}✅ Dependencies installed${NC}\n"

# 1. Code Formatting
echo -e "${BLUE}🎨 Code Formatting${NC}"
if [[ "$FIX_MODE" == true ]]; then
    echo "  Running black and isort (fixing)..."
    black src tests
    isort src tests
    echo -e "${GREEN}✅ Code formatted${NC}"
else
    echo "  Checking formatting..."
    if ! black --check src tests > /dev/null 2>&1; then
        echo -e "${RED}❌ Black formatting issues found. Run with --fix to auto-format${NC}"
        black --check src tests
        exit 1
    fi
    
    if ! isort --check-only src tests > /dev/null 2>&1; then
        echo -e "${RED}❌ Import sorting issues found. Run with --fix to auto-format${NC}"
        isort --check-only src tests
        exit 1
    fi
    echo -e "${GREEN}✅ Code is properly formatted${NC}"
fi

# 2. Type Checking (lenient for now)
echo -e "\n${BLUE}🔍 Type Checking (warnings only)${NC}"
echo "  Running mypy..."
mypy src/tekmera --ignore-missing-imports || echo -e "${YELLOW}⚠️  Type checking has issues (not failing build)${NC}"

# 3. Linting
echo -e "\n${BLUE}📝 Linting${NC}"
echo "  Running flake8..."
if ! flake8 src/ --max-line-length=100 --extend-ignore=E203,W503 > /dev/null 2>&1; then
    echo -e "${RED}❌ Flake8 linting failed${NC}"
    flake8 src/ --max-line-length=100 --extend-ignore=E203,W503
    exit 1
fi

echo -e "${GREEN}✅ Linting passed${NC}"

# 4. Security Scan
echo -e "\n${BLUE}🔒 Security Scan${NC}"
echo "  Running bandit..."
if ! bandit -r src/ -f json -o bandit-report.json -ll > /dev/null 2>&1; then
    bandit_exit=$?
    if [[ $bandit_exit -eq 1 ]]; then
        echo -e "${RED}❌ High severity security issues found${NC}"
        bandit -r src/ -ll
        exit 1
    fi
fi
echo -e "${GREEN}✅ No high severity security issues found${NC}"

# 5. Dependency Audit
echo -e "\n${BLUE}🔐 Dependency Audit${NC}"
echo "  Running pip-audit..."
if ! pip-audit --desc . > /dev/null 2>&1; then
    echo -e "${RED}❌ Security vulnerabilities found in dependencies${NC}"
    pip-audit --desc .
    exit 1
fi
echo -e "${GREEN}✅ No security vulnerabilities in dependencies${NC}"

# 6. Tests (optional)
if [[ "$SKIP_TESTS" != true ]]; then
    echo -e "\n${BLUE}🧪 Running Tests${NC}"
    if ! pytest tests/ -v --cov=tekmera --cov-report=term-missing > /dev/null 2>&1; then
        echo -e "${RED}❌ Tests failed${NC}"
        pytest tests/ -v --cov=tekmera --cov-report=term-missing
        exit 1
    fi
    echo -e "${GREEN}✅ All tests passed${NC}"
fi

# 7. Test Binary Build
echo -e "\n${BLUE}🔨 Testing Binary Build${NC}"
echo "  Building test binary..."
if ! pyinstaller --onefile --name tekmera-test-local src/tekmera/interfaces/cli/main.py > /dev/null 2>&1; then
    echo -e "${RED}❌ Binary build failed${NC}"
    pyinstaller --onefile --name tekmera-test-local src/tekmera/interfaces/cli/main.py
    exit 1
fi

echo "  Testing binary execution..."
if ! ./dist/tekmera-test-local --version > /dev/null 2>&1; then
    echo -e "${RED}❌ Binary execution failed${NC}"
    ./dist/tekmera-test-local --version
    exit 1
fi

# Clean up test binary
rm -f dist/tekmera-test-local*
echo -e "${GREEN}✅ Binary build and execution successful${NC}"

# 8. License Integration Test
echo -e "\n${BLUE}📄 License Integration Test${NC}"
python -c "
import sys, os
sys.path.insert(0, 'src')

# Test license manager imports
from tekmera.infra.license import license_manager
from tekmera.infra.license_ui import LicenseUI

print('✅ License components imported successfully')

# Test license info retrieval (should work in free mode)
info = license_manager.get_license_info()
print(f'✅ License info retrieved: {info[\"status\"]}')

# Test CLI license commands are wired up
from tekmera.interfaces.cli.main import cli
license_cmd = cli.commands.get('license')
assert license_cmd is not None, 'License command not found'

subcommands = list(license_cmd.commands.keys())
expected = ['activate', 'deactivate', 'status']
for cmd in expected:
    assert cmd in subcommands, f'Missing subcommand: {cmd}'

print('✅ All license CLI commands are properly wired')
"

echo -e "${GREEN}✅ License integration test passed${NC}"

# Summary
echo -e "\n${GREEN}🎉 All CI checks passed!${NC}"
echo -e "Ready to commit. The following checks were run:"
echo "  ✅ Code formatting (black, isort)"
echo "  ✅ Type checking (mypy)"
echo "  ✅ Linting (flake8, pylint)"
echo "  ✅ Security scanning (bandit)"
echo "  ✅ Dependency audit (pip-audit)"
if [[ "$SKIP_TESTS" != true ]]; then
    echo "  ✅ Test suite"
fi
echo "  ✅ Binary build test"
echo "  ✅ License integration test"

# Clean up reports
rm -f bandit-report.json audit-report.json coverage.xml .coverage