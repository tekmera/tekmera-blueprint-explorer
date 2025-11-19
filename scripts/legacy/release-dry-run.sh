#!/bin/bash
# Dry run release script for Tekmera CLI
# Preview release changes without making any commits or tags

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source the shared release functions
source "$SCRIPT_DIR/release.sh"

# Default to patch for dry run preview
BUMP_TYPE="${1:-patch}"

echo "🔍 Dry run mode - previewing $BUMP_TYPE release"
echo ""

# Execute dry run release
do_release "$BUMP_TYPE" true