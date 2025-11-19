#!/bin/bash
#
# Run Tekmera in LOCAL PRO mode for development/testing
#
# This script uses the TEKMERA_LOCAL_PRO environment variable to enable
# all Pro features without generating or activating a license. This is
# the fastest way to test Pro features during development.
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🛠️  Running Tekmera in LOCAL PRO mode (development)"
echo "=================================================="

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

# Clear any existing license but keep environment mode
echo "🧹 Clearing existing license..."
rm -f ~/.tekmera/license.json 2>/dev/null || true
unset TEKMERA_LICENSE_KEY 2>/dev/null || true

# Set local pro mode
export TEKMERA_LOCAL_PRO=true

echo ""
echo "✅ Local Pro mode enabled!"
echo "📋 License Status: LOCAL PRO (development mode)"
echo "🎯 Features Available: ALL Pro features (no license required)"
echo "🛠️  Development Mode: TEKMERA_LOCAL_PRO=true"
echo "ℹ️  Note: This mode is for development only and bypasses license validation"
echo ""

# Run the application
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <blueprint_directory>"
    echo "Example: $0 ./blueprints"
    exit 1
fi

echo "🚀 Starting Tekmera in LOCAL PRO mode..."
echo "Directory: $1"
echo ""

cd "$PROJECT_DIR"
python -m tekmera.interfaces.cli.main analyze "$1"