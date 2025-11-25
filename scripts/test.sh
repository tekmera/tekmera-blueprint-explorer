#!/bin/bash
# Quick test script for Tekmera Explorer
# Runs tests and quality checks without building binary

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Tekmera Explorer - Quick Test Suite${NC}\n"

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}⚠️  Warning: Not in a virtual environment. Activating venv...${NC}"
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
        echo -e "${GREEN}✅ Virtual environment activated${NC}"
    else
        echo -e "${RED}❌ Virtual environment not found${NC}"
        exit 1
    fi
fi

# Install test dependencies
echo -e "\n${BLUE}📦 Installing test dependencies...${NC}"
pip install -e ".[dev]" > /dev/null 2>&1
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Quick formatting
echo -e "\n${BLUE}🎨 Quick formatting...${NC}"
black src/ tests/ --line-length 100 --quiet
isort src/ tests/ --profile black --line-length 100 --quiet
echo -e "${GREEN}✅ Code formatted${NC}"

# Run tests with coverage
echo -e "\n${BLUE}🧪 Running test suite...${NC}"
pytest tests/ -v \
    --cov=tekmera \
    --cov-report=term-missing \
    --cov-fail-under=70

if [[ $? -eq 0 ]]; then
    echo -e "\n${GREEN}🎉 All tests passed!${NC}"
else
    echo -e "\n${RED}❌ Some tests failed${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ Quick test completed successfully!${NC}"