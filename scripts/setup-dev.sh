#!/bin/bash
# Development environment setup script
# Run this once to set up your development environment

set -e

echo "🚀 Setting up Tekmera development environment..."

# Check if Python 3.10+ is available
if ! python3 --version | grep -E "3\.(1[0-9]|[2-9][0-9])" > /dev/null 2>&1; then
    echo "❌ Python 3.10 or higher is required"
    echo "Current Python version: $(python3 --version)"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [[ ! -d "venv" ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install development dependencies
echo "📚 Installing development dependencies..."
pip install -e ".[dev]"

# Install CI tools
echo "🔧 Installing CI tools..."
pip install \
    black \
    isort \
    mypy \
    bandit \
    flake8 \
    pip-audit \
    pyinstaller \
    types-requests

# Install pre-commit if available
if command -v pre-commit > /dev/null 2>&1; then
    echo "🪝 Installing pre-commit hooks..."
    pip install pre-commit
    pre-commit install
fi

echo "✅ Development environment setup complete!"
echo ""
echo "Available development scripts:"
echo "  📋 ./scripts/setup-dev.sh      - First-time development environment setup"
echo "  🏃 ./scripts/run-dev.sh        - Run CLI with auto-environment"
echo "  🔧 ./scripts/check-dev.sh      - Auto-fix code + run all checks"
echo ""
echo "Development workflow:"
echo "  1. Make your changes"
echo "  2. Run: ./scripts/check-dev.sh  (auto-fixes + validates)"
echo "  3. Test: ./scripts/run-dev.sh analyze ./blueprints"
echo "  4. Commit when checks pass"