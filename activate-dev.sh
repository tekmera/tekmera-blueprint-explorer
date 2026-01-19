#!/bin/bash
# Quick activation script for Tekmera development environment
source venv/bin/activate
echo "🚀 Tekmera development environment activated"
echo "💡 Available commands:"
echo "   tekmera --help                    # Show help"
echo "   tekmera report <blueprint.json>   # Generate report"
echo "   tekmera search <query> <dir>      # Search blueprints"
echo "   ./scripts/build.sh               # Build binary"
echo "   pytest tests/ -v                 # Run tests"
