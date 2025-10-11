#!/bin/bash
# Shared release functions for Tekmera CLI
# This file is sourced by individual release scripts

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
BRANCH="main"

# Main release function
do_release() {
    local BUMP_TYPE="$1"
    local DRY_RUN="${2:-false}"

    echo -e "${BLUE}🚀 Tekmera CLI Release Automation${NC}"
    echo -e "Bump type: ${YELLOW}$BUMP_TYPE${NC}"
    echo -e "Branch: ${YELLOW}$BRANCH${NC}"
    echo -e "Dry run: ${YELLOW}$DRY_RUN${NC}"
    echo ""

    # Check prerequisites
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${RED}❌ Not in a git repository${NC}"
        exit 1
    fi

    # Check if we have the required tools
    for tool in python git; do
        if ! command -v $tool > /dev/null 2>&1; then
            echo -e "${RED}❌ Required tool not found: $tool${NC}"
            exit 1
        fi
    done

    # Check for clean working directory
    if [[ -n $(git status --porcelain) ]]; then
        echo -e "${RED}❌ Working directory is not clean. Please commit or stash changes.${NC}"
        git status --short
        exit 1
    fi

    # Check current branch
    CURRENT_BRANCH=$(git branch --show-current)
    if [[ "$CURRENT_BRANCH" != "$BRANCH" ]]; then
        echo -e "${RED}❌ Not on release branch '$BRANCH' (currently on '$CURRENT_BRANCH')${NC}"
        echo "Switch to $BRANCH first"
        exit 1
    fi

    # Ensure we're up to date with remote
    echo -e "${BLUE}📡 Fetching latest changes...${NC}"
    if ! $DRY_RUN; then
        git fetch origin
        if [[ $(git rev-parse HEAD) != $(git rev-parse origin/$BRANCH) ]]; then
            echo -e "${RED}❌ Local branch is not up to date with origin/$BRANCH${NC}"
            echo "Run: git pull origin $BRANCH"
            exit 1
        fi
    fi

    # Get current version from pyproject.toml
    CURRENT_VERSION=$(python -c "
import re
with open('pyproject.toml', 'r') as f:
    content = f.read()
    match = re.search(r'version = \"([^\"]+)\"', content)
    if match:
        print(match.group(1))
    else:
        print('0.0.0')
")

    echo -e "Current version: ${YELLOW}$CURRENT_VERSION${NC}"

    # Calculate new version
    NEW_VERSION=$(python -c "
import sys
from packaging.version import Version

current = Version('$CURRENT_VERSION')
bump_type = '$BUMP_TYPE'

if bump_type == 'major':
    new = Version(f'{current.major + 1}.0.0')
elif bump_type == 'minor':
    new = Version(f'{current.major}.{current.minor + 1}.0')
elif bump_type == 'patch':
    new = Version(f'{current.major}.{current.minor}.{current.micro + 1}')
else:
    print('Invalid bump type', file=sys.stderr)
    sys.exit(1)

print(str(new))
")

    echo -e "New version: ${GREEN}$NEW_VERSION${NC}"

    # Run checks
    echo -e "\n${BLUE}🧪 Running pre-release checks...${NC}"
    if ! $DRY_RUN; then
        # Run the development checks
        if [[ -f "scripts/check-dev.sh" ]]; then
            echo "Running check-dev.sh..."
            ./scripts/check-dev.sh --skip-tests
        else
            echo "⚠️  check-dev.sh not found, running basic checks..."
            
            # Check if virtual environment exists and activate it
            if [[ -f "venv/bin/activate" ]]; then
                source venv/bin/activate
            fi
            
            # Install packaging for version calculations
            pip install packaging > /dev/null 2>&1
            
            # Run basic tests
            if [[ -f "pyproject.toml" ]] && command -v pytest > /dev/null 2>&1; then
                pytest tests/ --tb=short
            fi
        fi
        echo -e "${GREEN}✅ Pre-release checks passed${NC}"
    fi

    # Update version in pyproject.toml
    echo -e "\n${BLUE}📝 Updating version...${NC}"
    if ! $DRY_RUN; then
        # Update pyproject.toml
        python -c "
import re

with open('pyproject.toml', 'r') as f:
    content = f.read()

new_content = re.sub(
    r'version = \"[^\"]+\"',
    f'version = \"$NEW_VERSION\"',
    content
)

with open('pyproject.toml', 'w') as f:
    f.write(new_content)

print('Updated pyproject.toml')
"
        
        # Update _version.py for development
        cat > src/tekmera/_version.py << EOF
"""
Version information for Tekmera CLI.
This file is automatically updated during the build process.
"""

__version__ = "$NEW_VERSION"
__build_date__ = "dev"
__commit__ = "dev"
__platform__ = "dev"


def get_version_info():
    """Get comprehensive version information."""
    return {
        "version": __version__,
        "build_date": __build_date__,
        "commit": __commit__,
        "platform": __platform__,
    }


def get_version_string():
    """Get a formatted version string for display."""
    if __build_date__ == "dev":
        return f"{__version__} (development)"
    return f"{__version__} (built {__build_date__})"
EOF
        
        echo -e "${GREEN}✅ Version updated to $NEW_VERSION${NC}"
    else
        echo -e "${YELLOW}📝 Would update version to $NEW_VERSION${NC}"
    fi

    # Commit version bump
    echo -e "\n${BLUE}💾 Committing version bump...${NC}"
    if ! $DRY_RUN; then
        git add pyproject.toml src/tekmera/_version.py
        git commit -m "chore: bump version to $NEW_VERSION

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
        echo -e "${GREEN}✅ Version bump committed${NC}"
    else
        echo -e "${YELLOW}💾 Would commit version bump${NC}"
    fi

    # Create and push tag
    TAG_NAME="v$NEW_VERSION"
    echo -e "\n${BLUE}🏷️  Creating tag $TAG_NAME...${NC}"
    if ! $DRY_RUN; then
        git tag -a "$TAG_NAME" -m "Release $NEW_VERSION

Tekmera CLI $NEW_VERSION

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
        
        echo "Pushing tag to origin..."
        git push origin "$TAG_NAME"
        git push origin $BRANCH
        
        echo -e "${GREEN}✅ Tag $TAG_NAME created and pushed${NC}"
    else
        echo -e "${YELLOW}🏷️  Would create and push tag $TAG_NAME${NC}"
    fi

    # Final instructions
    echo -e "\n${GREEN}🎉 Release process completed!${NC}"
    echo ""
    if ! $DRY_RUN; then
        echo "✅ Version bumped to $NEW_VERSION"
        echo "✅ Tag $TAG_NAME created and pushed" 
        echo "✅ GitHub Actions will now build and create the release"
        echo ""
        echo "🔗 Monitor the release build at:"
        REPO_URL=$(git remote get-url origin | sed 's/\.git$//' | sed 's/git@github\.com:/https:\/\/github.com\//') 
        echo "   $REPO_URL/actions"
        echo ""
        echo "📦 The release will be available at:"
        echo "   $REPO_URL/releases/tag/$TAG_NAME"
    else
        echo "🔍 Dry run completed - no changes made"
    fi

    echo ""
    echo "Release timeline:"
    echo "  📝 Version bumped and tagged     ← Done"
    echo "  🔨 CI builds multi-platform bins ← In progress" 
    echo "  🚀 GitHub release created        ← ~5-10 minutes"
    echo "  📦 Binaries attached to release  ← ~5-10 minutes"
}

# If this script is run directly (not sourced), show usage
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "🚀 Tekmera CLI Release Scripts"
    echo ""
    echo "Available release scripts:"
    echo "  ./scripts/release-patch.sh     - Patch release (1.0.0 → 1.0.1)"
    echo "  ./scripts/release-minor.sh     - Minor release (1.0.0 → 1.1.0)"
    echo "  ./scripts/release-major.sh     - Major release (1.0.0 → 2.0.0)"
    echo "  ./scripts/release-dry-run.sh   - Preview any release changes"
    echo ""
    echo "Each script is self-contained and does exactly what the name suggests."
    exit 0
fi