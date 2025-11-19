#!/bin/bash
# Patch release script for Tekmera CLI
# Bumps patch version (1.0.0 → 1.0.1)

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source the shared release functions
source "$SCRIPT_DIR/release.sh"

# Execute patch release
do_release "patch" false