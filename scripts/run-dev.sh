#!/bin/bash
# Development runner script - automatically sets up environment and runs the CLI
# Usage: ./scripts/run-dev.sh [CLI_ARGS...]

set -e

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Tekmera development environment...${NC}"

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    if [[ -f "venv/bin/activate" ]]; then
        echo -e "${BLUE}📦 Activating virtual environment...${NC}"
        source venv/bin/activate
    else
        echo "❌ Virtual environment not found. Please run: ./scripts/setup-dev.sh"
        exit 1
    fi
fi

# Install in development mode if needed
if ! pip show tekmera-fusion-explorer > /dev/null 2>&1; then
    echo -e "${BLUE}🔧 Installing in development mode...${NC}"
    pip install -e . > /dev/null 2>&1
fi

echo -e "${GREEN}✅ Environment ready!${NC}"

# Check if arguments were provided
if [[ $# -eq 0 ]]; then
    echo -e "${BLUE}📋 No arguments provided. Available commands:${NC}"
    echo ""
    python -m tekmera.interfaces.cli.main --help
    echo ""
    echo "Examples:"
    echo "  ./scripts/run-dev.sh analyze ./blueprints"
    echo "  ./scripts/run-dev.sh license status"
    echo "  ./scripts/run-dev.sh --help"
else
    # Run the CLI with provided arguments
    echo -e "${BLUE}🏃 Running: tekmera $*${NC}"
    python -m tekmera.interfaces.cli.main "$@"
fi