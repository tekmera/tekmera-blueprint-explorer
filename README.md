# Tekmera Fusion Explorer

A professional command-line tool for analyzing exported Workfront Fusion blueprint JSON files. Provides comprehensive diagnostic capabilities including interactive exploration, governance auditing, AI-powered insights, and cross-blueprint analysis.

## 🚀 Quick Start

```bash
# Setup (run once)
chmod +x init.sh
./init.sh

# Daily usage
source venv/bin/activate
tekmera ./blueprints
```

## 📦 Installation

### Option 1: Quick Setup Script
```bash
./init.sh
```

### Option 2: Manual Installation
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies and package
pip install -r requirements.txt
pip install -e .
```

## 🎯 Usage

The `tekmera` command provides a centralized menu system with feature gating:

```bash
# Basic usage 
tekmera analyze /path/to/blueprints/
tekmera /path/to/blueprints/              # Backward compatibility

# Premium features automatically enabled with active license

# License management
tekmera license status                    # Check current license
tekmera license activate --file license.json
tekmera license deactivate

# General commands
tekmera --version                         # Show version info
tekmera --help                           # Show usage help
```

## ✨ Features

### 🔍 **Explore Scenario** (Free)
Interactive module-by-module exploration:
- Navigate scenarios like a structured map
- Drill down into individual modules
- View parameters, inputs, and Workfront fields
- Inspect raw JSON data with syntax highlighting
- Built-in search capabilities within scenarios

### 📊 **Analyze All Blueprints** (Free)
Cross-blueprint analysis and reporting:
- **Static Reports**: Comprehensive summaries and module counts
- **Cross-Blueprint Search**: Find patterns, fields, and modules across all scenarios
- **Field Rankings**: Most/least used Workfront fields
- **Module Usage**: Module type distribution analysis
- **Naming Analysis**: Detect inconsistent field naming patterns
- **Connection Analysis**: Review connection usage across scenarios

### ⚖️ **Governance Audit** (Mixed: 5 Free + 6 Pro)
Built-in governance checking with 11 comprehensive rules:
- **Basic Rules (Free)**: Naming conventions, structure validation, connection checking
- **Advanced Rules (Pro)**: Flow complexity analysis, functional density metrics, cognitive load assessment
- **Categories**: Naming, Structure, Field, Size, Connection, and Complexity rules
- **Pro Features**: Algorithmic complexity analysis, router density metrics, field mapping complexity

### 🔄 **Compare Scenarios** (Free)
Advanced scenario comparison:
- Side-by-side blueprint diff analysis
- Module-level change detection
- Parameter and mapping comparisons
- Export differences for documentation

### 🎯 **Premium Features** (Pro License Required)
- **🎥 Live Scenario Walkthrough**: Interactive step-by-step execution flow
- **📝 AI Business Process Description**: OpenAI-powered business process analysis (requires API key)
- **🔎 Advanced Cross-Blueprint Search**: Enhanced search capabilities across all scenarios
- **⚖️ Advanced Governance Rules**: 6 algorithmic complexity and density analysis rules

## 🏗️ Package Structure

```
src/tekmera/
├── core/                    # Core functionality
│   ├── parser.py           # Blueprint parsing and loading
│   └── analyzer.py         # Module analysis and field extraction
├── interfaces/cli/          # Command-line interfaces
│   ├── main.py            # Main CLI entry point
│   ├── interactive.py     # Interactive menu system
│   ├── explorer.py        # Scenario exploration interface
│   ├── search.py          # Cross-blueprint search interface
│   └── trace.py           # Live walkthrough interface
├── analysis/               # Analysis engines
│   ├── corpus_analyzer.py # Cross-blueprint analysis
│   ├── connections.py     # Connection analysis
│   ├── flow_tracer.py     # Execution flow tracing
│   └── flow_walker.py     # Live scenario walkthrough
├── governance/             # Governance rules and checking
│   ├── checker.py         # Governance rule engine
│   ├── models.py          # Governance data models
│   └── rules/             # Individual governance rules
├── comparison/             # Blueprint comparison tools
│   ├── diff_engine.py     # Main diff interface
│   ├── detailed_diff.py   # Detailed difference analysis
│   └── simple_diff.py     # Simple diff utilities
├── reporting/              # Report generation
│   └── reporter.py        # Static analysis reporting
├── config/                 # Configuration
│   ├── menu_system.py     # Centralized menu configuration
│   └── premium_features.py # Premium feature definitions
├── infra/                  # Infrastructure
│   ├── license.py         # Core license management
│   ├── license_ui.py      # License user interface
│   └── licensing_utils.py # License enforcement utilities
└── utils/                  # Shared utilities
```

## 📋 Menu System

The tool uses a hierarchical menu system with feature gating:

```
🔍 Tekmera Fusion Explorer
├── 📊 Explore Scenario
│   ├── 🔍 Explore modules & search within scenario
│   ├── 🎥 Live Scenario Walkthrough [Pro]
│   └── 📝 Describe Business Process [Pro]
├── 📊 Analyze All Blueprints  
│   ├── 📋 Generate static analysis report
│   └── 🔎 Search across all blueprints [Pro]
├── ⚖️ Governance Audit
│   ├── GOV-NAME-001: Scenario Naming Prefix
│   ├── GOV-NAME-002: Default Module Labels
│   ├── GOV-STRUC-001: Router Without Default Branch
│   ├── GOV-STRUC-002: Orphan Module
│   ├── GOV-CONN-001: Dev Connection in Prod
│   ├── GOV-COMP-001: Flow Complexity Index [Pro]
│   ├── GOV-SIZE-001: Functional Density Index [Pro]
│   ├── GOV-COMP-002: Router Density Analysis [Pro]
│   ├── GOV-COMP-003: Route Fan-Out Profile [Pro]
│   ├── GOV-COMP-004: Flow Depth Estimate [Pro]
│   └── GOV-FIELD-003: Field Mapping Complexity [Pro]
└── 🔄 Compare Scenarios
```

## 🛡️ Governance Rules

Built-in governance checking with **5 Free** and **6 Premium** rules:

### Free Governance Rules
- **GOV-NAME-001**: Scenario Naming Prefix - Enforces standardized naming conventions
- **GOV-NAME-002**: Default Module Labels - Identifies generic default labels
- **GOV-STRUC-001**: Router Without Default Branch - Ensures fallback branches exist
- **GOV-STRUC-002**: Orphan Module - Identifies disconnected modules
- **GOV-CONN-001**: Dev Connection in Prod - Prevents dev connections in production

### Premium Governance Rules (Pro License Required)
- **GOV-COMP-001**: Flow Complexity Index - Algorithmic complexity analysis
- **GOV-SIZE-001**: Functional Density Index - Module clustering analysis
- **GOV-COMP-002**: Router Density Analysis - Branching logic patterns
- **GOV-COMP-003**: Route Fan-Out Profile - Complex router detection
- **GOV-COMP-004**: Flow Depth Estimate - Execution path depth analysis
- **GOV-FIELD-003**: Field Mapping Complexity - Deep field reference analysis

## 🔧 Advanced Usage

### Environment Variables
```bash
export OPENAI_API_KEY="your-key-here"  # For AI business process descriptions
```

### Premium Features
```bash
# Premium features are automatically enabled with an active license
tekmera analyze ./blueprints

# Use AI business process description (requires OpenAI API key)
export OPENAI_API_KEY="your-key-here"
tekmera analyze ./blueprints
```

### License Management
```bash
# Check current license status
tekmera license status

# Activate a Pro license (after purchase)
tekmera license activate --file /path/to/license.json

# Deactivate current license (revert to free)
tekmera license deactivate

# With active Pro license, premium features are automatically enabled
tekmera analyze ./blueprints  # Automatically uses Pro features if licensed
```

### License Generation (Development/Testing)
```bash
# Generate a test license (30 days)
python3 scripts/generate_license.py generate --issued-to "Test User" --days 30

# Generate a trial license for customers
python3 scripts/generate_license.py trial --name "Customer" --email "user@company.com" --trial-days 30

# Generate permanent license
python3 scripts/generate_license.py generate --issued-to "Permanent User" --days 0
```

### Governance Auditing
```bash
# Interactive governance checking
tekmera analyze ./blueprints
# Select "Governance Audit" → Choose scenario → Select rule

# Premium governance rules require Pro license (automatically detected)
```

## 📁 Blueprint Structure

The tool supports standard Workfront Fusion blueprint exports:

```json
{
  "name": "Scenario Name",
  "flow": [
    {
      "id": 1,
      "module": "workfront-workfront:searchv3",
      "parameters": {...},
      "mapper": {...},
      "metadata": {...}
    }
  ]
}
```

Also supports diff blueprint format:
```json
{
  "blueprint": {
    "name": "Scenario Name", 
    "flow": [...]
  }
}
```

## 🔍 Search Capabilities

### Field Search
- Find all uses of Workfront fields (DE:)
- Exact or partial matching
- Cross-scenario usage analysis

### Module Search  
- Locate modules by type
- Flexible pattern matching
- Instance counting across blueprints

### Text Search
- Find arbitrary strings in configurations
- Case-sensitive/insensitive options
- Context preview and pagination

### Analytics
- Field usage rankings
- Module type distribution
- Inconsistent naming detection
- Connection environment analysis

## 🚀 Getting Started Examples

### Quick Analysis
```bash
# Generate a static report for all blueprints
tekmera analyze ./blueprints
# Select "Analyze All Blueprints" → "Generate static analysis report"
```

### Interactive Exploration
```bash
# Explore a specific scenario in detail
tekmera analyze ./blueprints
# Select "Explore Scenario" → Choose scenario → "Explore modules"
```

### Governance Auditing  
```bash
# Run governance checks
tekmera analyze ./blueprints
# Select "Governance Audit" → Choose scenario → Select rule
```

### License Activation
```bash
# Purchase license from https://tekmera.com/pricing
# Activate the license
tekmera license activate --file ~/Downloads/license.json

# Check activation status
tekmera license status

# Pro features now work automatically
tekmera analyze ./blueprints
```

### Premium AI Analysis
```bash
# Get AI-powered business process description (requires Pro license)
export OPENAI_API_KEY="your-key-here"
tekmera analyze ./blueprints
# Select "Explore Scenario" → Choose scenario → "Describe Business Process"
```

## 📚 Documentation

- **Features Overview**: See `docs/FEATURES.md` for detailed feature documentation
- **License Generation**: See `docs/LICENSE_GENERATION.md` for creating and managing license files
- **Governance Rules**: Built-in rule descriptions available in governance audit mode
- **API Reference**: Explore the `src/tekmera/` package structure for API details
- **Licensing Business Plan**: See `docs/LICENSING_STRATEGY.md` for business model details
- **Terms of Service**: See `docs/TERMS_OF_SERVICE.md` for Pro user terms
- **Privacy Policy**: See `docs/PRIVACY_POLICY.md` for data handling information

## 🤝 Contributing

To extend functionality:

1. **Add governance rules**: Extend `src/tekmera/governance/rules/`
2. **Enhance analysis**: Modify `src/tekmera/analysis/` modules
3. **Improve UI**: Update `src/tekmera/interfaces/cli/` interfaces
4. **Add features**: Integrate with `src/tekmera/config/menu_system.py`

## 📄 Dependencies

- **click**: Command-line interface framework
- **InquirerPy**: Interactive terminal prompts and menus
- **rich**: Rich text formatting and syntax highlighting  
- **openai**: AI-powered business process analysis (premium features)

## 📋 Requirements

- Python 3.8+
- Virtual environment (recommended)
- Workfront Fusion blueprint JSON exports
- OpenAI API key (optional, for premium AI features)

## 🏷️ Version

Current version: 0.1.0

Install the package and use `tekmera --version` to check your installed version.