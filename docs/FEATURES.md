# Tekmera Fusion Explorer - Feature Inventory

## 1. Main Menu Options

### 1.1 🔍 Explore Scenario
**Interactive exploration, search, and trace execution flow for a single scenario**

#### 1.1.0 Scenario Selection Features:
- Hierarchical folder navigation with breadcrumbs
- Auto-selection for single scenarios
- Module count display per scenario
- Back option

#### Sub-menu Options (after selecting scenario):
**1.1.1** 🔍 Explore modules & search within scenario
   - Interactive module exploration with built-in search capabilities
   
**1.1.2** 🎥 Live Scenario Walkthrough
   - Interactive step-by-step walkthrough of scenario execution
   
**1.1.3** 📝 Describe Business Process
   - AI-powered business process description of the scenario

---

### 1.2 📊 Analyze All Blueprints
**Generate reports and search across all scenarios in the directory**

#### Sub-menu Options:
**1.2.1** 📋 Generate static analysis report
   - Comprehensive summaries, module counts, and field analysis
   
**1.2.2** 🔎 Search across all blueprints
   - Find patterns, fields, and modules across all scenarios

---

### 1.3 ⚖️ Governance Audit
**Audit scenarios for compliance with governance rules**

#### Available Governance Checks:
**1.3.1** Scenario Naming Prefix - Validates naming conventions
**1.3.2** Default Module Label - Checks for generic/default module names  
**1.3.3** Router Without Default Branch - Ensures routers have fallback paths
**1.3.4** Orphan Module - Detects disconnected modules
**1.3.5** Dev Connection in Prod - Identifies development connections in production
**1.3.6** Flow Complexity Index - Measures scenario complexity
**1.3.7** Functional Density Index - Analyzes module-to-function ratio
**1.3.8** Router Density Analysis - Evaluates routing complexity
**1.3.9** Route Fan-Out Profile - Analyzes branching patterns
**1.3.10** Flow Depth Estimate - Measures execution depth
**1.3.11** Field Mapping Complexity - Evaluates mapping sophistication

#### 1.3.0 Governance Menu Flow:
- Select scenario for governance checking
- Choose specific governance check to run
- View results and violations
- Options: Run another check / Select different scenario / Return to main menu

---

### 1.4 🔄 Compare Scenarios
**Compare two blueprint scenarios to identify functional differences**

#### 1.4.0 Diff Features:
- Interactive scenario selection (first and second)
- Side-by-side comparison
- Functional difference identification

---

## 2. Explorer Interface Menu (Feature 1.1.1)

### 2.0 Main Explorer Options:
**2.1** 🔍 Explore modules in '{scenario_name}' - Module navigation and exploration
**2.2** 🔎 Search for Workfront field (DE:) - Find specific Workfront fields
**2.3** 🔧 Search for module type - Locate module types
**2.4** 📄 Search for text/string - Full-text search
**2.5** 📊 Show field usage rankings - Field usage frequency
**2.6** 📈 Show module type usage - Module type statistics
**2.7** ⚠️ Detect inconsistent field naming - Field naming analysis
**2.8** 🔗 Analyze connections - Connection configuration review
**2.9** ❌ Quit - Exit explorer

### 2.1 Module Detail Options (when viewing individual modules):
**2.1.1** 📋 View parameters - Module configuration settings
**2.1.2** 🔗 View mapper/inputs - Input field mappings
**2.1.3** 🏷️ View Workfront fields - DE fields used by module
**2.1.4** 📄 View raw JSON - Complete module data
**2.1.5** ← Back to module list - Return to module navigation

---

## 3. Cross-Blueprint Search Interface Menu (Feature 1.2.2)

### 3.0 Search Functions:
**3.1** 🔎 Search for Workfront field (DE:) - Find specific Workfront fields across all blueprints
**3.2** 🔧 Search for module type - Search for module types across corpus
**3.3** 📄 Search for text/string - Text search across all configurations

### 3.0 Analysis Functions:
**3.4** 📊 Show field usage rankings - Most commonly used fields across all scenarios
**3.5** 📈 Show module type usage - Module type usage statistics across corpus
**3.6** ⚠️ Detect inconsistent field naming - Cross-scenario field naming inconsistencies
**3.7** 🔗 Analyze connections - Connection usage analysis with environment warnings

### 3.0 Utility Functions:
**3.8** 📋 Show corpus statistics - Overall statistics about loaded blueprints
**3.9** ❌ Quit - Exit search interface

---

## Supporting Features

### Navigation & UI:
- Recursive blueprint discovery in subdirectories
- Pagination for large datasets (15 modules per page)
- Rich console interface with colors, panels, tables
- InquirerPy interactive menus
- Hierarchical folder structure support
- Relative path management

### File Handling:
- Multiple blueprint format support (standard and diff structures)
- JSON validation and error handling
- Recursive directory scanning
- Blueprint data normalization

### Core Analysis Engines:
- Blueprint Parser (`parser.py`)
- Blueprint Analyzer (`analyzer.py`) 
- Corpus Analyzer (`corpus_analyzer.py`)
- Flow Walker (`flow_walker.py`)
- Connection Utilities (`connection_utils.py`)

### AI Integration:
- OpenAI GPT-4o-mini integration for business process descriptions
- Requires OPENAI_API_KEY environment variable
- Converts technical blueprints to business narratives

---

## Product Tier Planning

### Free Tier (Core - Acquisition + Baseline Utility)
**Purpose:** Give real value for consultants; show reliability and depth.

| Feature ID | Feature Name | Description |
|------------|--------------|-------------|
| 1.1 | Explore Scenario | Single scenario exploration (without AI or live walkthrough) |
| 1.1.1 | Explore modules & search within scenario | Interactive module exploration with built-in search |
| 2.0-2.1.5 | Explorer Interface | Complete module navigation, search, and detail views |
| 1.2.1 | Generate static analysis report | Comprehensive summaries, module counts, and field analysis |
| 1.3.1-1.3.5 | Basic Governance Checks | Naming, labels, routers, orphans, dev connections |
| 1.4 | Compare Scenarios | Side-by-side blueprint comparison |
| Supporting | Navigation/UI + File Handling | Rich CLI, hierarchical navigation, file validation |

**Value Proposition:** Users can inspect, diff, and run basic audits with no paywall.

---

### Premium Tier (Paygate - Governance Intelligence + AI + Multi-Blueprint Insight)
**Purpose:** Monetize operational insight and LLM cost.

| Feature ID | Feature Name | Description | Cost Driver |
|------------|--------------|-------------|-------------|
| 1.1.3 | Describe Business Process | AI-powered business process description | OpenAI API |
| 1.1.2 | Live Scenario Walkthrough | Interactive step-by-step flow execution | Flow Walker engine |
| 1.2.2 | Cross-blueprint search and analysis | Entire section 3 functionality | Multi-scenario intelligence |
| 1.3.6-1.3.11 | Advanced Governance Checks | Complexity + density metrics | Analytical sophistication |
| 3.7 | Connection analysis with environment warnings | Environment classification and warnings | Operational insight |
| Future | Governance summary report | Export or markdown generation | Reporting capability |

**Package as:** "Tekmera Pro / Governance Pack"

---

### Drop or Delay (Non-essential for launch)

| Feature ID | Feature Name | Reasoning |
|------------|--------------|-----------|
| 1.1.0 | Folder breadcrumbs | May be brittle in CLI environment |
| UI Polish | Pagination beyond 15-item pages | Non-essential for core functionality |
| 3.8-3.9 | Cross-blueprint utility stats | Until multi-client use case proven |

---

### Tier Strategy Reasoning

**Free Tier:** Should feel like a complete diagnostic toolbox but stop short of organization-wide or AI-augmented insight.

**Premium Tier:** Locks the costly (OpenAI) and high-leverage (governance density, cross-scenario) functions—the ones buyers value for oversight and reporting.