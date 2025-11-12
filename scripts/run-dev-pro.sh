#!/bin/bash
#
# Run Tekmera in PRO license mode for development/testing
#
# This script generates a temporary premium license and runs the app
# to test full Pro functionality without expiration concerns.
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "💎 Running Tekmera in PRO license mode"
echo "======================================"

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

# Clear any existing license and environment variables
echo "🧹 Clearing existing license..."
rm -f ~/.tekmera/license.json 2>/dev/null || true
unset TEKMERA_LOCAL_PRO 2>/dev/null || true
unset TEKMERA_LICENSE_KEY 2>/dev/null || true

# Generate premium license
echo "🎫 Generating permanent Pro license..."
cd "$PROJECT_DIR"

# Generate the license using our script
PRO_LICENSE=$(python "$SCRIPT_DIR/generate-pro-license.py" pro 2>/dev/null)

if [[ -z "$PRO_LICENSE" ]]; then
    echo "❌ Failed to generate premium license"
    exit 1
fi

echo "📋 Generated License: $PRO_LICENSE"

# Activate the license
echo "🔑 Activating premium license..."
python -m tekmera.interfaces.cli.main license activate "$PRO_LICENSE"

if [[ $? -ne 0 ]]; then
    echo "❌ Failed to activate premium license"
    exit 1
fi

echo ""
echo "✅ Premium license activated successfully!"
echo "📋 License Status: PRO (permanent, no expiration)"
echo "🎯 Features Available: ALL Pro features permanently enabled"
echo "💎 Premium Features: AI analysis, advanced governance, live walkthrough"
echo ""

# Run the application
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <blueprint_directory>"
    echo "Example: $0 ./blueprints"
    exit 1
fi

echo "🚀 Starting Tekmera in PRO mode..."
echo "Directory: $1"
echo ""

python -m tekmera.interfaces.cli.main analyze "$1"