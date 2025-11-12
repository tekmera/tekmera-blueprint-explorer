#!/bin/bash
#
# Run Tekmera in EVALUATION license mode for development/testing
#
# This script generates a temporary evaluation license and runs the app
# to test evaluation functionality, expiration warnings, and upgrade flows.
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Default to 30 days, but allow override
EVAL_DAYS=${1:-30}

# Validate days parameter
if ! [[ "$EVAL_DAYS" =~ ^[0-9]+$ ]] || [[ $EVAL_DAYS -lt 1 ]] || [[ $EVAL_DAYS -gt 365 ]]; then
    echo "❌ Invalid evaluation days: $EVAL_DAYS (must be 1-365)"
    echo "Usage: $0 [days] [blueprint_directory]"
    echo "Example: $0 7 ./blueprints    # 7-day evaluation"
    echo "Example: $0 ./blueprints       # 30-day evaluation (default)"
    exit 1
fi

# Shift arguments if first is days
if [[ "$1" =~ ^[0-9]+$ ]]; then
    shift
    BLUEPRINT_DIR="$1"
else
    BLUEPRINT_DIR="$EVAL_DAYS"
    EVAL_DAYS=30
fi

echo "⏰ Running Tekmera in EVALUATION license mode ($EVAL_DAYS days)"
echo "============================================================="

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

# Generate evaluation license
echo "🎫 Generating $EVAL_DAYS-day evaluation license..."
cd "$PROJECT_DIR"

# Generate the license using our script
EVAL_LICENSE=$(python "$SCRIPT_DIR/generate-eval-license.py" "$EVAL_DAYS" 2>/dev/null)

if [[ -z "$EVAL_LICENSE" ]]; then
    echo "❌ Failed to generate evaluation license"
    exit 1
fi

echo "📋 Generated License: $EVAL_LICENSE"

# Activate the license
echo "🔑 Activating evaluation license..."
python -m tekmera.interfaces.cli.main license activate "$EVAL_LICENSE"

if [[ $? -ne 0 ]]; then
    echo "❌ Failed to activate evaluation license"
    exit 1
fi

echo ""
echo "✅ Evaluation license activated successfully!"
echo "📋 License Status: EVALUATION ($EVAL_DAYS days remaining)"
echo "🎯 Features Available: ALL Pro features during evaluation period"
echo "⚠️  Automatic expiration: License will revert to FREE after $EVAL_DAYS days"
echo ""

# Run the application
if [[ -z "$BLUEPRINT_DIR" ]]; then
    echo "Usage: $0 [days] <blueprint_directory>"
    echo "Example: $0 7 ./blueprints      # 7-day evaluation"
    echo "Example: $0 ./blueprints        # 30-day evaluation"
    exit 1
fi

echo "🚀 Starting Tekmera in EVALUATION mode..."
echo "Directory: $BLUEPRINT_DIR"
echo ""

python -m tekmera.interfaces.cli.main analyze "$BLUEPRINT_DIR"