# Tekmera Fusion Explorer

**Tekmera Fusion Explorer** is a command-line intelligence tool for **Workfront Fusion** blueprints.  
It gives integration teams deep visibility into complex automation portfolios — enabling rapid exploration, search, and analysis without opening Fusion.

Built for architects, developers, and administrators managing dozens or hundreds of scenarios, Tekmera turns exported blueprints into a **structured, queryable knowledge base** that reveals how your automation system actually behaves.

## Core Focus

**Exploration** — Step through scenarios module-by-module, trace execution paths, and inspect parameters in context.

**Search and Analytics** — Search fields, modules, or text across all blueprints, identify usage patterns, and surface architectural statistics.

**AI Insight** — Ask natural-language questions about scenarios, generate process summaries, and run cross-blueprint reasoning for impact or dependency analysis.

Tekmera replaces manual inspection with structured, high-speed insight into how your automation landscape behaves.

## Quick Start

```bash
# 1. Setup (one-time)
./scripts/setup-dev.sh
source venv/bin/activate

# 2. Analyze your blueprints
tekmera analyze ./blueprints

# 3. Start exploring!
# → Select "Explore Scenario" for detailed analysis
# → Select "Analyze All Blueprints" for cross-scenario insights
```

## Installation

### Automated Setup (Recommended)
```bash
./scripts/setup-dev.sh  # Handles everything automatically
```

### Manual Installation
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Usage Patterns

```bash
# Interactive analysis of blueprint directory
tekmera analyze /path/to/blueprints/

# Check license status and activate Pro features
tekmera license status
tekmera license activate YOUR-LICENSE-KEY
```

## Core Features

### 🔍 Interactive Exploration
- **Module Inspector** - Navigate scenarios module-by-module with rich parameter viewing
- **Smart Search** - Find fields, module types, and text patterns across all blueprints
- **Blueprint Comparison** - Side-by-side diff analysis with change detection

### 🤖 AI-Powered Analysis *(Pro)*
- **Business Process Descriptions** - Transform technical flows into readable business narratives
- **Interactive Scenario Chat** - Ask questions about specific scenarios with persistent conversation history
- **Cross-Blueprint Intelligence** - Analyze patterns and dependencies across entire blueprint collections

### 📊 Portfolio Insights *(Pro)*
- **Impact Assessment** - Understand downstream effects of proposed changes
- **Field Usage Analytics** - Track custom field adoption and identify optimization opportunities
- **Connection Analysis** - Map integration touchpoints and environment configurations

## Licensing & Pro Features

### Free Edition
✅ Interactive scenario exploration and module inspection  
✅ Blueprint comparison and diff analysis  
✅ Basic search across all blueprints

### Pro Edition
🚀 **AI-Powered Business Process Analysis** - Natural language explanations of technical workflows  
🚀 **Interactive Scenario Chat** - Ask detailed questions with persistent conversation history  
🚀 **Cross-Blueprint AI Intelligence** - Strategic insights across entire blueprint collections  
🚀 **Live Scenario Walkthrough** - Step-by-step execution flow visualization

**Requirements for AI Features**: OpenAI API key + Pro license

### License Management

```bash
# Check current status
tekmera license status

# Activate 30-day trial
tekmera license activate YOUR-TRIAL-KEY

# Activate permanent Pro license
tekmera license activate YOUR-PRO-LICENSE-KEY

# Deactivate (revert to Free)
tekmera license deactivate
```

### AI Setup (Pro License Required)
```bash
# Set OpenAI API key for AI features
export OPENAI_API_KEY="your-openai-api-key"

# For persistent setup, add to your shell profile:
echo 'export OPENAI_API_KEY="your-key"' >> ~/.bashrc
```

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
- Connection environment analysis

## Common Use Cases

### 📋 Documentation & Audit
```bash
tekmera analyze ./blueprints
# → "Analyze All Blueprints" → "Generate static analysis report"
# Creates comprehensive module counts, field usage, and connection summaries
```

### 🔍 Troubleshooting & Investigation  
```bash
tekmera analyze ./blueprints
# → "Explore Scenario" → Choose problematic scenario → "Explore modules"
# Navigate module-by-module to inspect parameters and mappings
```

### 🤖 Business Process Documentation *(Pro)*
```bash
export OPENAI_API_KEY="your-key"
tekmera analyze ./blueprints
# → "Explore Scenario" → Choose scenario → "Describe Business Process"
# AI generates business-friendly explanations of technical workflows
```

### 💬 Deep Scenario Analysis *(Pro)*
```bash
tekmera analyze ./blueprints
# → "Explore Scenario" → Choose scenario → "Ask AI Question"
# Interactive chat with persistent history: "How does this handle approvals?"
```

### 🌐 Cross-Blueprint Intelligence *(Pro)*
```bash
tekmera analyze ./blueprints
# → "Analyze All Blueprints" → "Cross-Blueprint AI Query"  
# Ask: "Which scenarios would break if I change the 'status' field?"
```

## System Requirements

- **Python**: 3.8+ with virtual environment support
- **Platform**: macOS, Linux, Windows (WSL recommended)  
- **Blueprints**: Workfront Fusion JSON exports from any environment
- **AI Features**: OpenAI API key (GPT-4 recommended for best results)

## Technical Details

**Built With**: Python, Click, Rich, InquirerPy  
**Architecture**: Modular CLI with plugin-based analysis engines  
**Performance**: Handles 100+ scenarios efficiently with smart caching  
**Security**: Cryptographically signed licenses with machine binding

## Documentation & Support

📚 **Comprehensive Docs**: `docs/FEATURES.md` • `docs/LICENSING.md`  
🛡️ **Legal**: `docs/TERMS_OF_SERVICE.md` • `docs/PRIVACY_POLICY.md`  
🔧 **Development**: See `src/tekmera/` for API reference

---

**Version 0.1.0** • [Get Pro License](https://tekmera.com) • [Report Issues](https://github.com/tekmera/issues)