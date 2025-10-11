#!/bin/bash
# Minor release script for Tekmera CLI
# Bumps minor version (1.0.0 → 1.1.0)

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source the shared release functions
source "$SCRIPT_DIR/release.sh"

# Execute minor release
do_release "minor" false