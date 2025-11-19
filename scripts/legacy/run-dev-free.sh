#!/bin/bash
#
# Run Tekmera in FREE license mode for development/testing
#
# This script clears any existing license and runs the app in free mode
# to test free-tier functionality and upgrade prompts.
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🆓 Running Tekmera in FREE license mode"
echo "================================================="

# Ensure we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Virtual environment not active. Activating..."
    if [[ -f "$PROJECT_DIR/venv/bin/activate" ]]; then
        source "$PROJECT_DIR/venv/bin/activate"
        echo "✅ Virtual environment activated"
    else
        echo "❌ Virtual environment not found. Run setup-dev.sh first."
        exit 1
    fi
fi

# Clear any existing license
echo "🧹 Clearing existing license..."
rm -f ~/.tekmera/license.json 2>/dev/null || true

# Clear any pro environment variables
unset TEKMERA_LOCAL_PRO 2>/dev/null || true
unset TEKMERA_LICENSE_KEY 2>/dev/null || true

echo "📋 License Status: FREE (no license active)"
echo "🎯 Features Available: Basic exploration, 5 governance rules, blueprint comparison"
echo "🚫 Features Disabled: AI features, advanced governance, live walkthrough"
echo ""

# Run the application
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <blueprint_directory>"
    echo "Example: $0 ./blueprints"
    exit 1
fi

echo "🚀 Starting Tekmera in FREE mode..."
echo "Directory: $1"
echo ""

# Change to project directory and run
cd "$PROJECT_DIR"
python -m tekmera.interfaces.cli.main analyze "$1"