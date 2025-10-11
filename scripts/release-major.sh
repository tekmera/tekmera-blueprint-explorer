#!/bin/bash
# Major release script for Tekmera CLI
# Bumps major version (1.0.0 → 2.0.0)

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source the shared release functions
source "$SCRIPT_DIR/release.sh"

# Execute major release
do_release "major" false