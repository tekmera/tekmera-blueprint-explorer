#!/bin/bash
# Initialization script for Tekmera Explorer development environment
# Sets up virtual environment, installs dependencies, and validates setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Initializing Tekmera Explorer development environment...${NC}\n"

# Check if Python 3 is available
echo -e "${BLUE}🔍 Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed or not in PATH${NC}"
    echo -e "${YELLOW}Please install Python 3.8+ and try again${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo -e "  Found: ${GREEN}${PYTHON_VERSION}${NC}"

# Remove existing virtual environment if corrupted
if [[ -d "venv" ]]; then
    echo -e "\n${YELLOW}⚠️  Existing virtual environment found${NC}"
    echo -e "${BLUE}🧹 Removing old virtual environment...${NC}"
    rm -rf venv
    echo -e "${GREEN}✅ Old virtual environment removed${NC}"
fi

# Create new virtual environment
echo -e "\n${BLUE}🏗️  Creating virtual environment...${NC}"
python3 -m venv venv
echo -e "${GREEN}✅ Virtual environment created${NC}"

# Activate virtual environment
echo -e "\n${BLUE}⚡ Activating virtual environment...${NC}"
source venv/bin/activate

# Verify activation
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    exit 1
fi
echo -e "  Virtual environment: ${GREEN}${VIRTUAL_ENV}${NC}"

# Upgrade pip
echo -e "\n${BLUE}📦 Upgrading pip...${NC}"
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✅ pip upgraded${NC}"

# Install requirements
echo -e "\n${BLUE}📋 Installing project requirements...${NC}"
if [[ -f "requirements.txt" ]]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Requirements installed${NC}"
else
    echo -e "${YELLOW}⚠️  No requirements.txt found${NC}"
fi

# Install project in development mode
echo -e "\n${BLUE}🔧 Installing project in development mode...${NC}"
pip install -e . --force-reinstall > /dev/null 2>&1
echo -e "${GREEN}✅ Project installed${NC}"

# Install development dependencies
echo -e "\n${BLUE}🛠️  Installing development dependencies...${NC}"
pip install black isort flake8 mypy pytest pytest-cov pyinstaller > /dev/null 2>&1
echo -e "${GREEN}✅ Development dependencies installed${NC}"

# Test basic functionality
echo -e "\n${BLUE}🧪 Testing basic functionality...${NC}"

# Test if tekmera command is available
if ! command -v tekmera &> /dev/null; then
    echo -e "${RED}❌ tekmera command not available${NC}"
    echo -e "${YELLOW}Try: source venv/bin/activate${NC}"
    exit 1
fi

# Test version command
if tekmera --version > /dev/null 2>&1; then
    VERSION=$(tekmera --version)
    echo -e "  Version: ${GREEN}${VERSION}${NC}"
else
    echo -e "${RED}❌ tekmera --version failed${NC}"
    exit 1
fi

# Test help command
if tekmera --help > /dev/null 2>&1; then
    echo -e "  Help command: ${GREEN}✅ Working${NC}"
else
    echo -e "${RED}❌ tekmera --help failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Basic functionality tests passed${NC}"

# Generate activation script
echo -e "\n${BLUE}📝 Creating activation helper script...${NC}"
cat > activate-dev.sh << 'EOF'
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
EOF
chmod +x activate-dev.sh
echo -e "${GREEN}✅ Activation script created: ./activate-dev.sh${NC}"

# Display summary
echo -e "\n${GREEN}🎉 Development environment initialized successfully!${NC}"
echo -e "\n${BLUE}📋 Setup Summary:${NC}"
echo -e "  🐍 Python: ${GREEN}${PYTHON_VERSION}${NC}"
echo -e "  📦 Virtual Environment: ${GREEN}${VIRTUAL_ENV}${NC}"
echo -e "  🔧 Project Version: ${GREEN}$(tekmera --version)${NC}"
echo -e "  📁 Working Directory: ${GREEN}$(pwd)${NC}"

echo -e "\n${BLUE}🚀 Quick Start:${NC}"
echo -e "  Activate: ${GREEN}source venv/bin/activate${NC}"
echo -e "  Or use: ${GREEN}./activate-dev.sh${NC}"
echo -e "  Test: ${GREEN}tekmera --help${NC}"
echo -e "  Build: ${GREEN}./scripts/build.sh${NC}"

echo -e "\n${BLUE}📖 Next Steps:${NC}"
echo -e "  1. ${GREEN}source venv/bin/activate${NC} - Activate environment"
echo -e "  2. ${GREEN}tekmera report ./blueprints/blueprint-14926.json${NC} - Test with sample"
echo -e "  3. ${GREEN}./scripts/build.sh${NC} - Build production binary"
echo -e "  4. ${GREEN}pytest tests/ -v${NC} - Run test suite"

echo -e "\n${GREEN}✅ Ready to develop! 🎯${NC}"