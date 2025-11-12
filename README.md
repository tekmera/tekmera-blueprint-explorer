# Tekmera Fusion Explorer

A command-line tool for analyzing Workfront Fusion scenarios.

Tekmera processes exported Fusion blueprint JSON files to provide cross-scenario analysis and AI-powered insights for integration teams managing complex automation portfolios.

## Core Capabilities

**Exploration** - Interactive navigation of scenarios with module-level inspection and search  
**AI Insight** - Natural language analysis of business processes, scenario chat, and cross-blueprint impact assessment

Designed for integration developers and Workfront administrators who need systematic approaches to scenario maintenance and change impact analysis at scale.

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
```

## License Installation

Tekmera uses simple license key activation for premium features:

### Check Current License
```bash
tekmera license status
```

### Install Evaluation License (30-day trial)
```bash
tekmera license activate TEKMERA-eyJwYXlsb2FkIjp7ImxpY2Vuc2VfdHlwZSI6ImV2YWx1YXRpb24iLCJlZGl0aW9uIjoicHJvIiwiZXhwaXJ5IjoiMjAyNC0wMi0xNVQxMDozMDowMC4wMDAwMDAiLCJldmFsdWF0aW9uX2RheXMiOjMwLCJpc19ldmFsdWF0aW9uIjp0cnVlLCJpc3N1ZWRfYXQiOiIyMDI0LTAxLTE2VDEwOjMwOjAwLjAwMDAwMCIsIm1hY2hpbmVfZmluZ2VycHJpbnQiOiJhMWIyYzNkNGU1ZjZnN2g4IiwibGljZW5zZV9pZCI6ImFiY2RlZjEyLTM0NTYtNzg5MC1hYmNkLWVmMTIzNDU2Nzg5MCIsInZlcnNpb24iOiIyLjAifSwic2lnbmF0dXJlIjoiYWJjZGVmMTIzNDU2Nzg5MGFiY2RlZjEyMzQ1Njc4OTBhYmNkZWYxMjM0NTY3ODkwYWJjZGVmMTIzNDU2Nzg5MCJ9
```

### Install Premium License (permanent)
```bash
tekmera license activate TEKMERA-eyJwYXlsb2FkIjp7ImxpY2Vuc2VfdHlwZSI6InByZW1pdW0iLCJlZGl0aW9uIjoicHJvIiwiZXhwaXJ5IjpudWxsLCJpc19ldmFsdWF0aW9uIjpmYWxzZSwiaXNzdWVkX2F0IjoiMjAyNC0wMS0xNlQxMDozMDowMC4wMDAwMDAiLCJtYWNoaW5lX2ZpbmdlcnByaW50IjoiYTFiMmMzZDRlNWY2ZzdoOCIsImxpY2Vuc2VfaWQiOiJhYmNkZWYxMi0zNDU2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJ2ZXJzaW9uIjoiMi4wIn0sInNpZ25hdHVyZSI6IjEyMzQ1Njc4OTBhYmNkZWYxMjM0NTY3ODkwYWJjZGVmMTIzNDU2Nzg5MGFiY2RlZjEyMzQ1Njc4OTAifQ==
```

### Remove License
```bash
tekmera license deactivate
```

### Development Mode (all features enabled)
```bash
export TEKMERA_LOCAL_PRO=true
tekmera analyze ./blueprints
```

## Features

### Exploration
**Scenario Navigation** - Module-by-module inspection with parameter viewing and JSON export  
**Cross-Blueprint Search** - Find patterns, fields, and module types across scenario collections  
**Diff Analysis** - Side-by-side blueprint comparison with change detection


### AI Insight
**Business Process Description** - Natural language explanation of scenario functionality  
**Interactive Scenario Chat** - Persistent conversations with automated search capabilities  
**Cross-Blueprint Analysis** - Impact assessment and dependency mapping across collections

All AI features require OpenAI API key and Pro license.


## Licensing

**Free**  
Exploration, blueprint comparison

**Paid** (Evaluation or Permanent)  
AI features, live walkthrough

```bash
# License activation (evaluation or permanent)
tekmera license status
tekmera license activate TEKMERA-eyJwYXlsb2FkIjp7ImxpY2Vuc2VfdHlwZSI6ImV2YWx1YXRpb24iLCJlZGl0aW9uIjoicHJvIiwiZXhwaXJ5IjoiMjAyNC0wMi0xNVQxMDozMDowMC4wMDAwMDAiLCJldmFsdWF0aW9uX2RheXMiOjMwfQ  # 30-day trial
tekmera license activate TEKMERA-eyJwYXlsb2FkIjp7ImxpY2Vuc2VfdHlwZSI6InByZW1pdW0iLCJlZGl0aW9uIjoicHJvIiwiZXhwaXJ5IjpudWxsfQ  # Permanent paid license

# Development mode (all features enabled)
export TEKMERA_LOCAL_PRO=true
```

**AI Requirements**  
Set `OPENAI_API_KEY` environment variable for AI features (paid license required)

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


### License Activation
```bash
# Activate evaluation license (30-day trial) 
tekmera license activate TEKMERA-eyJwYXlsb2FkIjp7ImxpY2Vuc2VfdHlwZSI6ImV2YWx1YXRpb24iLCJlZGl0aW9uIjoicHJvIiwiZXhwaXJ5IjoiMjAyNC0wMi0xNVQxMDozMDowMC4wMDAwMDAiLCJldmFsdWF0aW9uX2RheXMiOjMwfQ

# Activate permanent paid license
tekmera license activate TEKMERA-eyJwYXlsb2FkIjp7ImxpY2Vuc2VfdHlwZSI6InByZW1pdW0iLCJlZGl0aW9uIjoicHJvIiwiZXhwaXJ5IjpudWxsfQ

# Check activation status
tekmera license status

# Paid features now work automatically
tekmera analyze ./blueprints
```

### Paid AI Analysis
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
- **Licensing Guide**: See `docs/LICENSING.md` for comprehensive licensing documentation
- **API Reference**: Explore the `src/tekmera/` package structure for API details
- **Terms of Service**: See `docs/TERMS_OF_SERVICE.md` for user terms
- **Privacy Policy**: See `docs/PRIVACY_POLICY.md` for data handling information

## Contributing

To extend functionality:

1. **Enhance analysis**: Modify `src/tekmera/analysis/` modules
2. **Improve UI**: Update `src/tekmera/interfaces/cli/` interfaces
3. **Add features**: Integrate with `src/tekmera/config/menu_system.py`

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