# Tekmera Fusion Explorer - Feature Inventory

## Application Overview
Interactive CLI tool for analyzing, exploring, and comparing Workfront Fusion blueprint JSON files. Supports hierarchical directory navigation and single/multi-scenario analysis.

---

## 🔍 **Explore a Scenario** 
*Interactive exploration, search, and trace execution flow for a single scenario*

### Core Exploration Features
- **Module Explorer** (`explorer.py`): Interactive module navigation with pagination
  - Browse modules page by page (15 per page)
  - View detailed module information and configurations
  - Built-in search capabilities within scenario

### Search & Analysis Within Scenario
- **Field Search**: Find Workfront fields (DE: patterns) within the scenario
- **Module Type Search**: Locate specific module types 
- **Text Search**: Full-text search across module configurations
- **Field Rankings**: Usage frequency analysis of Workfront fields
- **Module Rankings**: Module type usage statistics
- **Inconsistent Field Detection**: Identify field naming inconsistencies
- **Connection Analysis**: Review connection configurations and warnings

### Live Scenario Walkthrough
- **Interactive Flow Tracer** (`trace_interface.py`): Step-by-step execution simulation
  - Follow module execution paths
  - Navigate through conditional logic and routers
  - Visualize data flow between modules

### AI-Powered Business Process Description
- **OpenAI Integration**: Generates human-readable business process descriptions
  - Converts technical blueprint into business workflow narrative
  - Uses GPT-4o-mini for cost-effective analysis
  - Requires OPENAI_API_KEY environment variable

---

## 📊 **Analyze All Blueprints**
*Generate reports and search across all scenarios in the directory*

### Static Analysis & Reporting
- **Comprehensive Report Generation** (`reporter.py`):
  - Module count summaries per scenario
  - Complete module type inventory
  - Workfront field usage analysis
  - Cross-scenario statistics

### Cross-Blueprint Search Interface
- **Multi-Scenario Search** (`search_interface.py`):
  - Field pattern matching across all blueprints
  - Module type discovery and usage analysis
  - Text search across entire corpus
  - Statistical analysis of field and module usage
  - Connection analysis across scenarios
  - Corpus statistics and overview

### Advanced Analytics
- **Corpus Analyzer** (`corpus_analyzer.py`): 
  - Aggregate statistics across all scenarios
  - Pattern recognition and trend analysis
  - Cross-scenario comparison capabilities

---

## ⚖️ **Run a Governance Check**
*Audit scenarios for compliance with governance rules*

### Basic Governance Rules
1. **Scenario Naming Prefix**: Validates naming conventions
2. **Default Module Labels**: Checks for generic/default module names
3. **Router Without Default Branch**: Ensures routers have fallback paths
4. **Orphan Modules**: Detects disconnected modules
5. **Dev Connection in Prod**: Identifies development connections in production

### Advanced Structural Analysis
6. **Flow Complexity Index**: Measures scenario complexity
7. **Functional Density Index**: Analyzes module-to-function ratio
8. **Router Density Analysis**: Evaluates routing complexity
9. **Route Fan-Out Profile**: Analyzes branching patterns
10. **Flow Depth Estimate**: Measures execution depth
11. **Field Mapping Complexity**: Evaluates mapping sophistication

### Governance Framework
- **Rule Engine** (`governance/checker.py`): Modular rule system
- **Violation Reporting**: Detailed violation descriptions with suggested fixes
- **Rule Categories**: Organized by naming, structure, connections, complexity, size, and field rules

---

## 🔄 **Compare Scenarios (Diff)**
*Compare two blueprint scenarios to identify functional differences*

### Comparison Features
- **Interactive Scenario Selection**: Choose any two blueprints for comparison
- **Diff Analysis** (`diff_cli.py`): Side-by-side comparison tool
- **Change Detection**: Identifies additions, deletions, and modifications
- **Structural Comparison**: Compares module relationships and flow paths

---

## 🗂️ **Supporting Infrastructure**

### Core Parsing & Analysis
- **Blueprint Parser** (`parser.py`): JSON blueprint file processing
- **Blueprint Analyzer** (`analyzer.py`): Module and structure analysis
- **Flow Walker** (`flow_walker.py`): Navigation through scenario execution paths

### Connection Management
- **Connection Utilities** (`connection_utils.py`):
  - Connection environment classification (dev/prod/test)
  - Connection validation and warnings
  - Connection summary reporting
  - Connection analysis across scenarios

### Navigation & UI
- **Hierarchical Directory Navigation**: Supports nested folder structures
- **Rich Console Interface**: Colorized output with panels, tables, and syntax highlighting
- **Interactive Menus**: InquirerPy-based selection interfaces
- **Pagination Support**: Handle large datasets efficiently

### File Structure Support
- **Recursive Blueprint Discovery**: Automatically finds JSON files in subdirectories
- **Multiple Blueprint Formats**: Handles both standard and diff blueprint structures
- **Relative Path Management**: Maintains folder hierarchy context

---

## 💡 **Feature Categorization for Product Planning**

### **Core/Essential Features** (MVP Candidates)
- Basic blueprint parsing and loading
- Module exploration with pagination
- Simple field and module search
- Basic governance checks (1-5)
- Static report generation
- Scenario comparison (diff)

### **Advanced Features** (Premium/Pro Tier)
- AI-powered business process description (requires API costs)
- Advanced governance rules (6-11)
- Live scenario walkthrough/tracing
- Cross-blueprint corpus analysis
- Connection analysis and warnings
- Advanced search with ranking algorithms

### **Infrastructure Features** (Foundation)
- Rich CLI interface
- Hierarchical navigation
- File structure management
- Error handling and validation

### **Potential Extensions** (Future Roadmap)
- Export capabilities (PDF reports, CSV data)
- Integration with Workfront/Fusion APIs
- Custom governance rule creation
- Scenario optimization suggestions
- Performance impact analysis
- Automated testing scenario generation