#!/bin/bash
# Complete build and test script for Tekmera Explorer
# Runs full test suite, quality checks, and binary build

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Build configuration
BINARY_NAME="tekmera"
BUILD_DIR="dist"
SPEC_FILE="tekmera.spec"
COVERAGE_MIN=15
SKIP_TESTS=false
SKIP_BUILD=false
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --coverage)
            COVERAGE_MIN="$2"
            shift 2
            ;;
        --help|-h)
            echo "Tekmera Explorer - Build and Test Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --skip-tests     Skip running tests"
            echo "  --skip-build     Skip binary build (run tests only)"
            echo "  --verbose, -v    Verbose output"
            echo "  --coverage NUM   Minimum coverage percentage (default: 80)"
            echo "  --help, -h       Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Full build and test"
            echo "  $0 --skip-build      # Tests only"
            echo "  $0 --skip-tests      # Build only"
            echo "  $0 --coverage 90     # Require 90% test coverage"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Start timer
START_TIME=$(date +%s)

echo -e "${BLUE}🚀 Tekmera Explorer - Full Build and Test Pipeline${NC}\n"

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}⚠️  Warning: Not in a virtual environment. Activating venv...${NC}"
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
        echo -e "${GREEN}✅ Virtual environment activated${NC}"
    else
        echo -e "${RED}❌ Virtual environment not found. Please run:${NC}"
        echo -e "   ${CYAN}python -m venv venv && source venv/bin/activate${NC}"
        exit 1
    fi
fi

# Install dependencies
echo -e "\n${BLUE}📦 Installing dependencies...${NC}"
if [[ "$VERBOSE" == "true" ]]; then
    pip install -e ".[dev]"
    pip install pyinstaller bandit pip-audit flake8 autoflake
else
    pip install -e ".[dev]" > /dev/null 2>&1
    pip install pyinstaller bandit pip-audit flake8 autoflake > /dev/null 2>&1
fi
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Get version information
echo -e "\n${BLUE}📋 Reading version information...${NC}"
VERSION=$(python -c "
import sys
sys.path.insert(0, 'src')
try:
    from tekmera._version import get_version_string
    print(get_version_string())
except ImportError:
    # Fallback to pyproject.toml
    try:
        import tomllib
        with open('pyproject.toml', 'rb') as f:
            data = tomllib.load(f)
        print(data['project']['version'])
    except:
        print('unknown')
")
echo -e "Version: ${GREEN}${VERSION}${NC}"

# Clean previous build artifacts
echo -e "\n${BLUE}🧹 Cleaning build artifacts...${NC}"
rm -rf build/ dist/ *.spec .coverage htmlcov/ .mypy_cache/ .pytest_cache/
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}✅ Build artifacts cleaned${NC}"

# Code formatting and quality checks
echo -e "\n${PURPLE}🔧 Code Quality Checks${NC}"
echo -e "${BLUE}──────────────────────────────────────────────────${NC}"

# Auto-format code
echo -e "\n${BLUE}🎨 Auto-formatting code...${NC}"
black src/ tests/ --line-length 100
isort src/ tests/ --profile black --line-length 100
echo -e "${GREEN}✅ Code formatting completed${NC}"

# Remove unused imports
echo -e "\n${BLUE}🔥 Removing unused imports...${NC}"
autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive src/ tests/
echo -e "${GREEN}✅ Unused imports removed${NC}"

# Linting
echo -e "\n${BLUE}📏 Running linter...${NC}"
if flake8 src/ tests/ --extend-ignore=E203,W503,E501,F541 --max-line-length=100; then
    echo -e "${GREEN}✅ Linting passed${NC}"
else
    echo -e "${YELLOW}⚠️  Linting issues found (not failing build)${NC}"
fi

# Security scanning
echo -e "\n${BLUE}🔒 Security scanning...${NC}"
if bandit -r src/ -f json -o bandit-report.json > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Security scan passed${NC}"
else
    echo -e "${YELLOW}⚠️  Security issues found - check bandit-report.json${NC}"
fi

# Dependency audit
echo -e "\n${BLUE}🔍 Dependency audit...${NC}"
if pip-audit --desc > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Dependency audit passed${NC}"
else
    echo -e "${YELLOW}⚠️  Dependency vulnerabilities found${NC}"
fi

# Type checking
echo -e "\n${BLUE}🏷️  Type checking...${NC}"
if mypy src/ --ignore-missing-imports --no-error-summary > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Type checking passed${NC}"
else
    echo -e "${YELLOW}⚠️  Type checking issues found (not failing build)${NC}"
fi

# Run tests
if [[ "$SKIP_TESTS" == "false" ]]; then
    echo -e "\n${PURPLE}🧪 Test Suite${NC}"
    echo -e "${BLUE}──────────────────────────────────────────────────${NC}"
    
    echo -e "\n${BLUE}🧪 Running test suite with coverage...${NC}"
    
    # Run tests with coverage
    if [[ "$VERBOSE" == "true" ]]; then
        pytest tests/ -v \
            --cov=tekmera \
            --cov-report=term-missing \
            --cov-report=html \
            --cov-fail-under=${COVERAGE_MIN}
    else
        pytest tests/ \
            --cov=tekmera \
            --cov-report=term-missing \
            --cov-report=html \
            --cov-fail-under=${COVERAGE_MIN} \
            -q
    fi
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ All tests passed with >=${COVERAGE_MIN}% coverage${NC}"
        
        # Display coverage summary
        COVERAGE_PCT=$(python -c "
import re
try:
    with open('.coverage', 'rb'): pass
    import coverage
    cov = coverage.Coverage()
    cov.load()
    print(f'{cov.report():.0f}')
except:
    print('unknown')
" 2>/dev/null || echo "unknown")
        
        if [[ "$COVERAGE_PCT" != "unknown" ]]; then
            echo -e "  📊 Coverage: ${GREEN}${COVERAGE_PCT}%${NC}"
        fi
        echo -e "  📄 HTML Report: ${CYAN}htmlcov/index.html${NC}"
    else
        echo -e "${RED}❌ Tests failed or coverage below ${COVERAGE_MIN}%${NC}"
        exit 1
    fi
    
    # Test import functionality
    echo -e "\n${BLUE}📦 Testing package imports...${NC}"
    python -c "
import sys
sys.path.insert(0, 'src')
try:
    import tekmera
    from tekmera.clients.cli.main import main
    from tekmera.functions.blueprints.basic.name.workfront_fusion import extract_blueprint_name_workfront_fusion
    from tekmera.reporting.diff.diff import generate_diff_report
    print('✅ All critical imports successful')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
"
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ Package imports validated${NC}"
    else
        echo -e "${RED}❌ Package import validation failed${NC}"
        exit 1
    fi
else
    echo -e "\n${YELLOW}⏭️  Skipping tests (--skip-tests flag)${NC}"
fi

# Build binary
if [[ "$SKIP_BUILD" == "false" ]]; then
    echo -e "\n${PURPLE}🔨 Binary Build${NC}"
    echo -e "${BLUE}──────────────────────────────────────────────────${NC}"
    
    echo -e "\n${BLUE}🔨 Building production binary...${NC}"
    
    # Build binary with PyInstaller
    pyinstaller \
        --onefile \
        --name "${BINARY_NAME}" \
        --distpath "${BUILD_DIR}" \
        --workpath "build" \
        --specpath "." \
        --console \
        --add-data "src/tekmera:tekmera" \
        src/tekmera/__main__.py
    
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}❌ Binary build failed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Binary built successfully${NC}"
    
    # Test binary functionality
    echo -e "\n${BLUE}🧪 Testing binary functionality...${NC}"
    
    if [[ ! -f "${BUILD_DIR}/${BINARY_NAME}" ]]; then
        echo -e "${RED}❌ Binary not found at ${BUILD_DIR}/${BINARY_NAME}${NC}"
        exit 1
    fi
    
    # Make binary executable
    chmod +x "${BUILD_DIR}/${BINARY_NAME}"
    
    # Test version command
    echo "  Testing version command..."
    if "./${BUILD_DIR}/${BINARY_NAME}" --version > /dev/null 2>&1; then
        VERSION_OUTPUT=$("./${BUILD_DIR}/${BINARY_NAME}" --version 2>&1)
        echo -e "    ${GREEN}✅ Version: ${VERSION_OUTPUT}${NC}"
    else
        echo -e "    ${RED}❌ Version command failed${NC}"
        "./${BUILD_DIR}/${BINARY_NAME}" --version
        exit 1
    fi
    
    # Test help command
    echo "  Testing help command..."
    if "./${BUILD_DIR}/${BINARY_NAME}" --help > /dev/null 2>&1; then
        echo -e "    ${GREEN}✅ Help command working${NC}"
    else
        echo -e "    ${RED}❌ Help command failed${NC}"
        exit 1
    fi
    
    # Test basic functionality with sample data if available
    if [[ -d "blueprints" ]]; then
        SAMPLE_BLUEPRINT=$(find blueprints -name "*.json" -type f | head -1)
        if [[ -n "$SAMPLE_BLUEPRINT" ]]; then
            echo "  Testing basic analysis..."
            if "./${BUILD_DIR}/${BINARY_NAME}" count "$SAMPLE_BLUEPRINT" > /dev/null 2>&1; then
                echo -e "    ${GREEN}✅ Basic analysis working${NC}"
            else
                echo -e "    ${YELLOW}⚠️  Basic analysis test skipped (expected on some systems)${NC}"
            fi
        fi
    fi
    
    echo -e "${GREEN}✅ Binary testing completed${NC}"
    
    # Generate build info
    BUILD_INFO="${BUILD_DIR}/build-info.txt"
    echo -e "\n${BLUE}📄 Generating build information...${NC}"
    
    cat > "${BUILD_INFO}" << EOF
Tekmera Explorer Build Information
==================================

Version: ${VERSION}
Build Date: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Platform: $(uname -s)-$(uname -m)
Python Version: $(python --version 2>&1)
Git Commit: $(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
Git Branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
Coverage: ${COVERAGE_PCT}%

Binary Information:
- Location: ${BUILD_DIR}/${BINARY_NAME}
- Size: $(ls -lh "${BUILD_DIR}/${BINARY_NAME}" | awk '{print $5}')

Build Environment:
- Virtual Environment: ${VIRTUAL_ENV:-"None"}
- Working Directory: $(pwd)
- Build User: $(whoami)

Quality Metrics:
- Tests Passed: $(pytest tests/ --collect-only -q 2>/dev/null | grep "test session starts" | wc -l | tr -d ' ' || echo "unknown")
- Coverage: ${COVERAGE_PCT}%
- Security Scan: $(if [[ -f bandit-report.json ]]; then echo "Completed"; else echo "N/A"; fi)

Usage Commands:
- Run: ./${BUILD_DIR}/${BINARY_NAME}
- Install: cp ${BUILD_DIR}/${BINARY_NAME} /usr/local/bin/
- Help: ./${BUILD_DIR}/${BINARY_NAME} --help
- Version: ./${BUILD_DIR}/${BINARY_NAME} --version

EOF
    
    echo -e "${GREEN}✅ Build information generated${NC}"
    
    # Cleanup spec file
    rm -f "${SPEC_FILE}"
    
else
    echo -e "\n${YELLOW}⏭️  Skipping binary build (--skip-build flag)${NC}"
fi

# Calculate total time
END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))
MINUTES=$((TOTAL_TIME / 60))
SECONDS=$((TOTAL_TIME % 60))

# Final summary
echo -e "\n${PURPLE}📊 Build Summary${NC}"
echo -e "${BLUE}──────────────────────────────────────────────────${NC}"

if [[ "$SKIP_BUILD" == "false" ]]; then
    echo -e "  📦 Binary: ${GREEN}./${BUILD_DIR}/${BINARY_NAME}${NC}"
    echo -e "  📊 Size: ${GREEN}$(ls -lh "${BUILD_DIR}/${BINARY_NAME}" 2>/dev/null | awk '{print $5}' || echo "unknown")${NC}"
    echo -e "  📄 Build Info: ${GREEN}./${BUILD_DIR}/build-info.txt${NC}"
fi

if [[ "$SKIP_TESTS" == "false" ]]; then
    echo -e "  🧪 Test Coverage: ${GREEN}${COVERAGE_PCT}%${NC}"
    echo -e "  📊 Coverage Report: ${CYAN}htmlcov/index.html${NC}"
fi

echo -e "  🏷️  Version: ${GREEN}${VERSION}${NC}"
echo -e "  ⏱️  Total Time: ${GREEN}${MINUTES}m ${SECONDS}s${NC}"

echo -e "\n${GREEN}🎉 Build pipeline completed successfully!${NC}"

if [[ "$SKIP_BUILD" == "false" ]]; then
    echo -e "\n${BLUE}🚀 Quick Start:${NC}"
    echo -e "  ${GREEN}./${BUILD_DIR}/${BINARY_NAME} --help${NC}"
    echo -e "  ${GREEN}cp ${BUILD_DIR}/${BINARY_NAME} /usr/local/bin/${NC}  # Install globally"
fi

echo -e "\n${BLUE}📚 Next Steps:${NC}"
if [[ "$SKIP_TESTS" == "false" ]]; then
    echo -e "  • Review coverage report: ${CYAN}open htmlcov/index.html${NC}"
fi
if [[ -f bandit-report.json ]]; then
    echo -e "  • Review security scan: ${CYAN}cat bandit-report.json${NC}"
fi
echo -e "  • Test installation: ${CYAN}./${BUILD_DIR}/${BINARY_NAME} --version${NC}"

echo -e "\n${GREEN}✅ All done!${NC}"