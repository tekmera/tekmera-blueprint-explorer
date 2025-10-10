# Tekmera Fusion Explorer

A command-line tool for analyzing exported Workfront Fusion blueprint JSON files. Provides both static reporting and interactive exploration modes to understand scenario structure, modules, and field dependencies.

## Features

### 📊 Static Analysis Mode (Default)
- Scans directory of blueprint JSON files
- Extracts scenario names, module counts, and types
- Identifies Workfront field references (DE: keys)
- Generates structured summary report

### 🔍 Interactive Explorer Mode 
- Navigate scenarios like a structured map
- Drill down into individual modules  
- View parameters, inputs, and Workfront fields
- Inspect raw JSON data with syntax highlighting
- **Built-in search capabilities**: All cross-blueprint search features integrated
- Search for fields, modules, text, and analyze patterns within explorer

### 🔎 Cross-Blueprint Search Mode
- Search for Workfront fields (DE:) across all blueprints
- Find modules by type with partial or exact matching
- Search for arbitrary text within module configurations  
- Analyze field and module usage rankings
- Detect inconsistent field naming patterns
- Review connection usage across scenarios

### 🔄 Execution Flow Trace Mode
- Step-by-step trace through scenario execution paths
- Visual tree or linear flow representation
- Identify DE fields, variables, and external calls per step
- Track router branches and conditional logic
- Compare execution flows between scenarios
- Export traces to JSON for documentation

## Installation

1. **Clone or download the project**
2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Interactive Mode (Default)

Launch the interactive interface with mode selection:

```bash
python cli.py /path/to/blueprints/
```

This will present a menu:
```
What would you like to do?
▸ Run static analysis report
  Explore Scenario
  Trace execution flow
  Search across blueprints
  Exit
```

### Direct Mode Access (Flags)

You can also access specific modes directly using command-line flags:

```bash
# Static analysis report
python cli.py --report /path/to/blueprints/

# Interactive exploration
python cli.py --explore /path/to/blueprints/

# Cross-blueprint search
python cli.py --search /path/to/blueprints/

# Execution flow tracing
python cli.py --trace /path/to/blueprints/
```

**Example output:**
```
============================================================
WORKFRONT FUSION BLUEPRINT ANALYSIS REPORT
============================================================

Scenario: PROD WF Project Listener SA - Optimized
File: blueprint-15793.json
Modules: 5
Module Types:
  - builtin:BasicRouter
  - datastore:SearchRecord
  - workfront-workfront:custom
  - workfront-workfront:watchEvents
Workfront Fields:
  - DE:eyk_ikp_activityID_fus
  - DE:eyk_ikp_engagementID_fus
  ...

SUMMARY
--------------------
Total Scenarios: 2
Total Modules: 9
Unique Module Types: 6
Unique Workfront Fields: 11
```

### Interactive Explorer Mode

Launch the interactive mode to explore scenarios in detail:

```bash
python cli.py --explore /path/to/blueprints/
```

**Interactive features:**
- **Scenario Selection**: Choose from available blueprints
- **Module Index**: View all modules with summaries
- **Module Details**: Deep dive into parameters, inputs, and fields
- **Raw JSON**: Inspect complete module data with syntax highlighting

### Cross-Blueprint Search Mode

Launch search mode to analyze patterns across all blueprints:

```bash
python cli.py --search /path/to/blueprints/
```

**Search capabilities:**
- **Field Search**: Find all uses of specific Workfront fields (DE:)
- **Module Search**: Locate modules by type with flexible matching
- **Text Search**: Find arbitrary strings in any module configuration
- **Usage Rankings**: See most/least used fields and module types
- **Naming Analysis**: Detect inconsistent field naming patterns
- **Connection Analysis**: Review connection usage across scenarios

### Execution Flow Trace Mode

Launch trace mode to follow execution paths step-by-step:

```bash
python cli.py --trace /path/to/blueprints/
```

**Trace features:**
- **Tree View**: Hierarchical display showing router branches and nesting
- **Linear View**: Step-by-step list with indentation for nested flows  
- **JSON Export**: Structured data export for documentation/analysis
- **Flow Comparison**: Side-by-side analysis of different scenarios
- **Smart Detection**: Automatically identifies variables, external calls, DE fields
- **Router Analysis**: Shows conditional branches and filter conditions

## File Structure

```
fusion_parser/
├── cli.py              # Command-line interface and main entry point
├── parser.py           # JSON loading and blueprint parsing (with recursive module extraction)
├── analyzer.py         # Module analysis and field extraction
├── reporter.py         # Static report formatting
├── explorer.py         # Interactive exploration interface
├── corpus_analyzer.py  # Cross-blueprint analysis engine
├── search_interface.py # Interactive search and analysis UI
├── flow_tracer.py      # Execution flow tracing engine
├── trace_interface.py  # Interactive trace and flow analysis UI
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Blueprint Structure

The tool expects Workfront Fusion blueprint JSON files with this structure:
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

## Dependencies

- **click**: Command-line interface framework
- **InquirerPy**: Interactive terminal prompts and menus
- **rich**: Rich text formatting and syntax highlighting

## Examples

### Interactive Usage
```bash
# Launch interactive mode (default)
python cli.py ./blueprints

# The interface will guide you through:
# 1. Mode selection (report/explore/trace/search)
# 2. Scenario selection (when applicable)
# 3. Configuration options for each mode
```

### Direct Mode Usage
```bash
# Generate static report directly
python cli.py --report ./blueprints

# Launch specific modes directly
python cli.py --explore ./blueprints
python cli.py --search ./blueprints  
python cli.py --trace ./blueprints
```

### Interactive Exploration
```bash
# Launch explorer mode
python cli.py --explore ./blueprints

# Navigate through the interface:
# 1. Select a scenario from the list
# 2. View module index with summaries
# 3. Choose a module to examine in detail
# 4. View parameters, inputs, Workfront fields, or raw JSON
# 5. Navigate back or switch scenarios
```

### Cross-Blueprint Search
```bash
# Launch search mode
python cli.py --search ./blueprints

# Search capabilities:
# 1. Search for specific DE fields (e.g., "DE:client_id")
# 2. Find modules by type (e.g., "workfront" or exact match)
# 3. Text search across all configurations
# 4. View field usage rankings (most/least used)
# 5. Analyze module type distribution
# 6. Detect inconsistent field naming patterns
# 7. Review connection usage across scenarios
```

### Execution Flow Tracing
```bash
# Launch trace mode
python cli.py --trace ./blueprints

# Trace capabilities:
# 1. Select scenario and output format (tree/linear/json)
# 2. Follow execution paths from trigger to completion
# 3. See router branches and conditional logic
# 4. Identify variables, DE fields, external calls per step
# 5. Compare flows between different scenarios
# 6. Export traces to JSON for documentation
```

### Typical Workflow
1. **Export blueprints**: Download `.json` files from Workfront Fusion
2. **Launch analyzer**: Run `python cli.py blueprints/` for interactive mode selection
3. **Choose your approach**:
   - **Quick overview**: Select "Run static analysis report"
   - **Deep investigation**: Select "Explore Scenario" (includes built-in search)
   - **Flow understanding**: Select "Trace execution flow"
   - **Pattern analysis**: Select "Search across blueprints" (dedicated search mode)
4. **Direct access**: Use flags (`--report`, `--explore`, `--trace`, `--search`) for direct mode access
5. **Documentation**: Use findings to document integrations and dependencies

## Output Details

### Static Report
- **Scenario Name**: From JSON metadata or filename
- **Module Count**: Total modules in the scenario
- **Module Types**: Unique module types (e.g., `workfront-workfront:searchv3`)
- **Workfront Fields**: All DE: field references found

### Interactive Explorer
- **Module Summaries**: Context-aware descriptions (e.g., "Search PROJ objects")
- **Parameters**: Module configuration settings
- **Mapper/Inputs**: Input field mappings and transformations
- **DE Fields**: Workfront custom fields used by the module
- **Raw JSON**: Complete module data for technical review

## Error Handling

The tool handles common issues gracefully:
- **Malformed JSON**: Skips files with warnings, continues processing
- **Missing fields**: Uses fallbacks and safe defaults
- **Empty directories**: Reports no files found
- **Keyboard interrupts**: Clean exit from interactive mode

## Contributing

To extend functionality:
1. **Add new analysis**: Extend `analyzer.py` methods
2. **Improve summaries**: Update `_generate_module_summary()` for new module types
3. **Enhance UI**: Modify `explorer.py` for better navigation
4. **Add export formats**: Create new output modules

## License

[Add your license information here]