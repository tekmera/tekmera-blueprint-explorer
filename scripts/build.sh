#!/bin/bash
# Build script for Tekmera Explorer
# Creates production-ready binary using PyInstaller

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Build configuration
BINARY_NAME="tekmera"
BUILD_DIR="dist"
SPEC_FILE="tekmera.spec"

echo -e "${BLUE}🔨 Building Tekmera Explorer...${NC}\n"

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

# Install dependencies
echo -e "${BLUE}📦 Installing build dependencies...${NC}"
pip install -e . > /dev/null 2>&1
pip install pyinstaller > /dev/null 2>&1
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Clean previous builds
echo -e "\n${BLUE}🧹 Cleaning previous builds...${NC}"
rm -rf build/ dist/ *.spec
echo -e "${GREEN}✅ Build directory cleaned${NC}"

# Run quality checks first
echo -e "\n${BLUE}🔍 Running quality checks...${NC}"
if [[ -f "scripts/check-dev.sh" ]]; then
    ./scripts/check-dev.sh --skip-tests
elif [[ -f "scripts/legacy/check-dev.sh" ]]; then
    echo -e "${YELLOW}⚠️  Using legacy quality checks...${NC}"
    # Run basic checks without legacy imports
    echo "  Running basic linting..."
    pip install black isort flake8 > /dev/null 2>&1
    black --check src/ || (echo -e "${YELLOW}⚠️  Code formatting issues found${NC}" && black src/)
    isort --check-only src/ || (echo -e "${YELLOW}⚠️  Import sorting issues found${NC}" && isort src/)
    flake8 src/ --extend-ignore=E203,W503,E501,F541 > /dev/null || echo -e "${YELLOW}⚠️  Linting issues found (not failing build)${NC}"
fi
echo -e "${GREEN}✅ Quality checks completed${NC}"

# Get version from package
echo -e "\n${BLUE}📋 Reading version information...${NC}"
VERSION=$(python -c "
import sys
sys.path.insert(0, 'src')
try:
    from tekmera._version import get_version_string
    print(get_version_string())
except ImportError:
    # Fallback to pyproject.toml
    import tomllib
    with open('pyproject.toml', 'rb') as f:
        data = tomllib.load(f)
    print(data['project']['version'])
")
echo -e "Building version: ${GREEN}${VERSION}${NC}"

# Build binary
echo -e "\n${BLUE}🔨 Creating binary with PyInstaller...${NC}"
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

# Test binary
echo -e "\n${BLUE}🧪 Testing binary...${NC}"
if [[ ! -f "${BUILD_DIR}/${BINARY_NAME}" ]]; then
    echo -e "${RED}❌ Binary not found at ${BUILD_DIR}/${BINARY_NAME}${NC}"
    exit 1
fi

# Make binary executable
chmod +x "${BUILD_DIR}/${BINARY_NAME}"

# Test basic functionality
echo "  Testing version command..."
if ! "./${BUILD_DIR}/${BINARY_NAME}" --version > /dev/null 2>&1; then
    echo -e "${RED}❌ Binary version test failed${NC}"
    "./${BUILD_DIR}/${BINARY_NAME}" --version
    exit 1
fi

echo "  Testing help command..."
if ! "./${BUILD_DIR}/${BINARY_NAME}" --help > /dev/null 2>&1; then
    echo -e "${RED}❌ Binary help test failed${NC}"
    "./${BUILD_DIR}/${BINARY_NAME}" --help
    exit 1
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

Binary Location: ${BUILD_DIR}/${BINARY_NAME}
Binary Size: $(ls -lh "${BUILD_DIR}/${BINARY_NAME}" | awk '{print $5}')

Build Environment:
- Virtual Environment: ${VIRTUAL_ENV:-"None"}
- Working Directory: $(pwd)
- Build User: $(whoami)

Build Commands:
- Run: ./${BUILD_DIR}/${BINARY_NAME}
- Install: cp ${BUILD_DIR}/${BINARY_NAME} /usr/local/bin/
- Help: ./${BUILD_DIR}/${BINARY_NAME} --help

EOF

# Display summary
echo -e "\n${GREEN}🎉 Build completed successfully!${NC}"
echo -e "\n${BLUE}📋 Build Summary:${NC}"
echo -e "  📦 Binary: ${GREEN}./${BUILD_DIR}/${BINARY_NAME}${NC}"
echo -e "  📊 Size: ${GREEN}$(ls -lh "${BUILD_DIR}/${BINARY_NAME}" | awk '{print $5}')${NC}"
echo -e "  🏷️  Version: ${GREEN}${VERSION}${NC}"
echo -e "  📄 Build Info: ${GREEN}./${BUILD_INFO}${NC}"

echo -e "\n${BLUE}🚀 Usage:${NC}"
echo -e "  Test: ${GREEN}./${BUILD_DIR}/${BINARY_NAME} --help${NC}"
echo -e "  Install: ${GREEN}cp ${BUILD_DIR}/${BINARY_NAME} /usr/local/bin/${NC}"

# Cleanup spec file
rm -f "${SPEC_FILE}"

echo -e "\n${GREEN}✅ Build script completed successfully!${NC}"