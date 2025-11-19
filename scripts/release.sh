#!/bin/bash
# Tag-driven release for Tekmera CLI
# Tags are the single source of truth - CI handles version injection

set -euo pipefail
trap 'echo "Error at line $LINENO"' ERR

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BRANCH="main"

is_dry() { [[ "${1:-false}" == "true" ]]; }

do_release() {
    local BUMP_TYPE="$1"
    local DRY_RUN="${2:-false}"

    echo -e "${BLUE}🚀 Tekmera CLI Release (Tag-Driven)${NC}"
    echo -e "Bump type: ${YELLOW}$BUMP_TYPE${NC}"
    echo -e "Dry run: ${YELLOW}$DRY_RUN${NC}"
    echo ""

    # Prerequisites
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${RED}❌ Not in a git repository${NC}"
        exit 1
    fi

    for tool in python3 git; do
        if ! command -v "$tool" > /dev/null 2>&1; then
            echo -e "${RED}❌ Required tool not found: $tool${NC}"
            exit 1
        fi
    done

    # Verify git identity
    if ! git config user.name > /dev/null || ! git config user.email > /dev/null; then
        echo -e "${RED}❌ Git identity not configured${NC}"
        echo "Run: git config --global user.name 'Your Name'"
        echo "Run: git config --global user.email 'your@email.com'"
        exit 1
    fi

    # Clean working directory
    if [[ -n $(git status --porcelain) ]]; then
        echo -e "${RED}❌ Working directory not clean${NC}"
        git status --short
        exit 1
    fi

    # Correct branch
    CURRENT_BRANCH=$(git branch --show-current)
    if [[ "$CURRENT_BRANCH" != "$BRANCH" ]]; then
        echo -e "${RED}❌ Not on $BRANCH (currently on $CURRENT_BRANCH)${NC}"
        exit 1
    fi

    # Fresh tags and up to date
    if ! is_dry "$DRY_RUN"; then
        git fetch --tags origin
        if [[ $(git rev-parse HEAD) != $(git rev-parse "origin/$BRANCH") ]]; then
            echo -e "${RED}❌ Local branch not up to date with origin/$BRANCH${NC}"
            exit 1
        fi
    fi

    # Get latest tag or start at 0.0.0
    LATEST_TAG=$(git tag -l 'v*' | sort -V | tail -n1 || echo "")
    if [[ -z "$LATEST_TAG" ]]; then
        CURRENT_VERSION="0.0.0"
    else
        CURRENT_VERSION="${LATEST_TAG#v}"
    fi

    echo -e "Current version: ${YELLOW}$CURRENT_VERSION${NC}"

    # Calculate new version
    NEW_VERSION=$(python3 -c "
from packaging.version import Version
import sys

try:
    current = Version('$CURRENT_VERSION')
except:
    current = Version('0.0.0')

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

    TAG_NAME="v$NEW_VERSION"
    echo -e "New version: ${GREEN}$NEW_VERSION${NC}"

    # Check if tag already exists
    if git rev-parse "$TAG_NAME" > /dev/null 2>&1; then
        echo -e "${RED}❌ Tag $TAG_NAME already exists${NC}"
        exit 1
    fi

    # Update pyproject.toml with new version
    echo -e "\n${BLUE}📝 Updating pyproject.toml version to $NEW_VERSION...${NC}"
    if ! is_dry "$DRY_RUN"; then
        if command -v sed > /dev/null 2>&1; then
            # Use sed to update version in pyproject.toml
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS sed requires backup extension
                sed -i '' "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
            else
                # Linux sed
                sed -i "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
            fi
            echo -e "${GREEN}✅ Updated pyproject.toml version${NC}"
            
            # Commit the version bump
            git add pyproject.toml
            git commit -m "chore: bump version to $NEW_VERSION"
            echo -e "${GREEN}✅ Committed version bump${NC}"
        else
            echo -e "${RED}❌ sed command not found${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}📝 Would update pyproject.toml version to $NEW_VERSION${NC}"
        echo -e "${YELLOW}📝 Would commit version bump${NC}"
    fi

    # Create and push tag
    echo -e "\n${BLUE}🏷️  Creating tag $TAG_NAME...${NC}"
    if ! is_dry "$DRY_RUN"; then
        git tag -a "$TAG_NAME" -m "Release $NEW_VERSION"
        git push origin "$BRANCH"
        git push origin "$TAG_NAME"
        echo -e "${GREEN}✅ Tag $TAG_NAME created and pushed${NC}"
    else
        echo -e "${YELLOW}🏷️  Would create and push tag $TAG_NAME${NC}"
    fi

    # URLs
    REPO_URL=$(git remote get-url origin | sed 's/\.git$//' | sed 's/git@github\.com:/https:\/\/github.com\//')
    
    echo -e "\n${GREEN}🎉 Release initiated!${NC}"
    if ! is_dry "$DRY_RUN"; then
        echo ""
        echo "🔗 Monitor build: $REPO_URL/actions?query=workflow%3A%22Build+and+Release%22+tag%3A$TAG_NAME"
        echo "📦 Release page: $REPO_URL/releases/tag/$TAG_NAME"
        echo ""
        echo "CI will:"
        echo "  🔨 Build multi-platform binaries (~5-10 min)"
        echo "  🚀 Create GitHub release with assets"
        echo "  📋 Generate checksums and release notes"
    else
        echo "🔍 Dry run complete - no changes made"
    fi
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "🚀 Tekmera CLI Release Scripts"
    echo ""
    echo "Tag-driven releases (no file edits):"
    echo "  ./scripts/release-patch.sh     - Patch release"
    echo "  ./scripts/release-minor.sh     - Minor release" 
    echo "  ./scripts/release-major.sh     - Major release"
    echo "  ./scripts/release-dry-run.sh   - Preview release"
    exit 0
fi