# Tekmera Fusion Explorer

A command-line tool for auditing and analyzing Workfront Fusion scenarios.

Tekmera processes exported Fusion blueprint JSON files to provide governance auditing, cross-scenario analysis, and AI-powered insights for integration teams managing complex automation portfolios.

## Core Capabilities

**Exploration** - Interactive navigation of scenarios with module-level inspection and search  
**Governance** - 11 automated rules covering naming conventions, structural integrity, and complexity analysis  
**AI Insight** - Natural language analysis of business processes, scenario chat, and cross-blueprint impact assessment

Designed for integration developers and Workfront administrators who need systematic approaches to scenario maintenance, change impact analysis, and automation governance at scale.

## Quick Start

```bash
# Setup
./scripts/setup-dev.sh
source venv/bin/activate

# Analyze blueprints
tekmera analyze ./blueprints
```

## Installation

```bash
# Automated setup
./scripts/setup-dev.sh

# Manual installation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Usage

```bash
# Analyze blueprint directory
tekmera analyze /path/to/blueprints/

# License management
tekmera license status
tekmera license activate YOUR-LICENSE-KEY-HERE  # Example placeholder
tekmera license deactivate

# Development mode (enables all features)
export TEKMERA_LOCAL_PRO=true
tekmera analyze ./blueprints
```

## Features

### Exploration
**Scenario Navigation** - Module-by-module inspection with parameter viewing and JSON export  
**Cross-Blueprint Search** - Find patterns, fields, and module types across scenario collections  
**Diff Analysis** - Side-by-side blueprint comparison with change detection

### Governance
**Free Rules (5)** - Naming conventions, structural validation, connection environment checking  
**Premium Rules (6)** - Algorithmic complexity analysis, router density metrics, field mapping complexity  
**Rule Categories** - Naming, Structure, Connection, Size, Complexity, and Field standards

### AI Insight
**Business Process Description** - Natural language explanation of scenario functionality  
**Interactive Scenario Chat** - Persistent conversations with automated search capabilities  
**Cross-Blueprint Analysis** - Impact assessment and dependency mapping across collections

All AI features require OpenAI API key and Pro license. Premium governance rules require Pro license.

## Governance Rules

| Rule ID | Category | Tier | Description |
|---------|----------|------|-------------|
| GOV-NAME-001 | Naming | Free | Scenario naming prefix enforcement |
| GOV-NAME-002 | Naming | Free | Default module label detection |
| GOV-STRUC-001 | Structure | Free | Router default branch validation |
| GOV-STRUC-002 | Structure | Free | Orphan module detection |
| GOV-CONN-001 | Connection | Free | Dev connection in production |
| GOV-COMP-001 | Complexity | Pro | Flow complexity index |
| GOV-SIZE-001 | Size | Pro | Functional density analysis |
| GOV-COMP-002 | Complexity | Pro | Router density metrics |
| GOV-COMP-003 | Complexity | Pro | Route fan-out analysis |
| GOV-COMP-004 | Complexity | Pro | Flow depth estimation |
| GOV-FIELD-003 | Field | Pro | Field mapping complexity |

## Licensing

**Free Tier**  
Exploration, basic governance (5 rules), blueprint comparison

**Pro Tier**  
AI features, advanced governance (6 additional rules), live walkthrough

```bash
# License activation
tekmera license status
tekmera license activate YOUR-LICENSE-KEY-HERE

# Development mode (all features enabled)
export TEKMERA_LOCAL_PRO=true
```

**AI Requirements**  
Set `OPENAI_API_KEY` environment variable for AI features

## Blueprint Structure

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

## Search Capabilities

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

## Getting Started Examples

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
# Set up OpenAI API key for AI features
export OPENAI_API_KEY="your-key-here"
tekmera analyze ./blueprints

# AI-powered business process description
# Select "Explore Scenario" → Choose scenario → "Describe Business Process"

# Interactive AI chat about scenarios  
# Select "Explore Scenario" → Choose scenario → "Ask AI Question"

# Cross-blueprint AI analysis
# Select "Analyze All Blueprints" → "Cross-Blueprint AI Query"
```

### AI Features Overview
```bash
# The AI features provide different levels of analysis:

# 1. Business Process Description (One-time analysis)
#    - Generates comprehensive business process overview
#    - Explains what the scenario does in business terms
#    - Perfect for documentation and stakeholder communication

# 2. AI Scenario Chat (Interactive conversation)
#    - Persistent chat history with conversation management
#    - AI actively searches scenario for specific details
#    - Ask follow-up questions and dive deeper
#    - Perfect for detailed investigation and troubleshooting

# 3. Cross-Blueprint AI Analysis (Collection-wide insights)
#    - Analyzes patterns across all scenarios in the folder
#    - Quantifies business impact and identifies dependencies
#    - AI searches across entire blueprint collection
#    - Perfect for change impact analysis and governance
```

## Documentation

- **Features Overview**: See `docs/FEATURES.md` for detailed feature documentation
- **License Generation**: See `docs/LICENSE_GENERATION.md` for creating and managing license files
- **Governance Rules**: Built-in rule descriptions available in governance audit mode
- **API Reference**: Explore the `src/tekmera/` package structure for API details
- **Licensing Business Plan**: See `docs/LICENSING_STRATEGY.md` for business model details
- **Terms of Service**: See `docs/TERMS_OF_SERVICE.md` for Pro user terms
- **Privacy Policy**: See `docs/PRIVACY_POLICY.md` for data handling information

## Contributing

To extend functionality:

1. **Add governance rules**: Extend `src/tekmera/governance/rules/`
2. **Enhance analysis**: Modify `src/tekmera/analysis/` modules
3. **Improve UI**: Update `src/tekmera/interfaces/cli/` interfaces
4. **Add features**: Integrate with `src/tekmera/config/menu_system.py`

## Dependencies

- **click**: Command-line interface framework
- **InquirerPy**: Interactive terminal prompts and menus
- **rich**: Rich text formatting and syntax highlighting  
- **openai**: AI-powered business process analysis (premium features)

## Requirements

- Python 3.8+
- Virtual environment (recommended)
- Workfront Fusion blueprint JSON exports
- OpenAI API key (optional, for premium AI features)

## Version

Current version: 0.1.0

Install the package and use `tekmera --version` to check your installed version.