# Tekmera Diff System - Architecture Documentation

## Overview

The Tekmera Diff System provides comprehensive comparison analysis between two blueprint versions, identifying structural, configuration, and functional changes in automation workflows.

## Core Concepts

### 1. Two-Layer Analysis
The diff system operates on two fundamental projections:
- **Topology Projection**: Directed Acyclic Graph (DAG) representing execution flow
- **Configuration Projection**: Module-level settings and parameters

### 2. Change Classification
Every module is classified into exactly one state:
- **Unchanged**: Module exists in both versions with identical config and position
- **Configuration Changed**: Module position unchanged, but configuration modified
- **Structurally Moved**: Module exists in both but in different flow position
- **Added**: Module exists only in new version
- **Removed**: Module exists only in old version

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Blueprint 1   │    │   Blueprint 2   │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          ▼                      ▼
┌─────────────────────────────────────────┐
│        Topology Projector              │
│  ┌─────────────┐  ┌─────────────────┐  │
│  │ DAG Builder │  │ Flow Extractor  │  │
│  └─────────────┘  └─────────────────┘  │
└─────────┬───────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────┐
│           Diff Engine                   │
│  ┌─────────────┐  ┌─────────────────┐  │
│  │Structural   │  │ Configuration   │  │
│  │Diff         │  │ Diff            │  │
│  └─────────────┘  └─────────────────┘  │
└─────────┬───────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────┐
│        Report Generator                 │
│  ┌─────────────┐  ┌─────────────────┐  │
│  │Visualization│  │ Change Cards    │  │
│  │Engine       │  │ Generator       │  │
│  └─────────────┘  └─────────────────┘  │
└─────────┬───────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────┐
│      Multi-Format Output               │
│   ┌─────┐  ┌─────┐  ┌─────┐ ┌─────┐   │
│   │Text │  │JSON │  │ PDF │ │HTML │   │
│   └─────┘  └─────┘  └─────┘ └─────┘   │
└─────────────────────────────────────────┘
```

## Data Structures

### Topology Graph
```python
@dataclass
class TopologyNode:
    id: str
    module_type: str
    name: str
    platform: Platform
    raw_data: Dict[str, Any]
    position: GraphPosition

@dataclass
class TopologyEdge:
    source: str
    target: str
    edge_type: EdgeType  # normal, router_branch, error_handler
    metadata: Dict[str, Any]

@dataclass
class TopologyGraph:
    nodes: List[TopologyNode]
    edges: List[TopologyEdge]
    entry_points: List[str]
    platform: Platform
```

### Configuration Diff
```python
@dataclass
class ConfigurationDiff:
    module_id: str
    changed_fields: List[FieldChange]
    severity: ChangeSeverity
    impact_assessment: str

@dataclass
class FieldChange:
    field_path: str
    old_value: Any
    new_value: Any
    change_type: ChangeType
```

### Diff Report
```python
@dataclass
class BlueprintDiffReport:
    # Metadata
    blueprint1_name: str
    blueprint2_name: str
    platform: Platform
    generated_at: datetime
    
    # Summary
    structural_change_score: float
    total_changes: int
    change_counts: Dict[str, int]  # {added: 2, removed: 1, moved: 3, changed: 5}
    
    # Topology Analysis
    topology1: TopologyGraph
    topology2: TopologyGraph
    structural_changes: List[StructuralChange]
    
    # Module Analysis
    module_changes: List[ModuleChange]
    configuration_changes: List[ConfigurationDiff]
    
    # Risk Assessment
    risk_level: RiskLevel
    breaking_changes: List[str]
    
    def to_text() -> str: ...
    def to_dict() -> Dict[str, Any]: ...
```

## Implementation Phases

### Phase 1: CLI Foundation ✅ COMPLETED
- [x] CLI command structure (`tekmera diff blueprint1.json blueprint2.json`)
- [x] Argument validation and file loading
- [x] Platform detection for both blueprints
- [x] Stub report generation with placeholder data
- [x] Multi-format output (table, JSON, PDF)
- [x] Complete module structure and data types
- [x] Integrated topology analysis in diff reports

### Phase 2: Topology Projection ✅ COMPLETED
- [x] **Task 1 COMPLETED**: Topology extraction module structure
  - Complete `topology/` module with types, interfaces, platform routing
  - Rich data structures: `TopologyGraph`, `TopologyNode`, `TopologyEdge`
  - Integrated with diff reports showing before/after graph statistics
  - Validation and serialization working perfectly

- [x] **Task 2 COMPLETED**: Workfront Fusion topology extractor 
  - Real blueprint parsing from `blueprint.flow` arrays
  - Recursive handling of nested flows in `routes` and `onerror` 
  - Accurate node classification (triggers, routers, filters, error handlers)
  - Complex edge detection (normal, router_branch, error_handler)
  - Tested with production blueprints (219-561 nodes successfully extracted)
  - Entry point detection and validation working

- [x] **Task 3 COMPLETED**: Make.com topology extractor
  - Real blueprint parsing from `blueprint.flow` arrays (similar to Workfront Fusion structure)
  - Uses existing component extraction system with `extract_all_components()`
  - Accurate module classification using `_get_make_module_category()` function
  - Complex edge detection for normal flow, router branches, and error handlers
  - Tested with Make.com blueprints (7-12 nodes successfully extracted)
  - Integrated with full diff pipeline showing real before/after topology statistics

- [ ] **Task 4**: Enhanced graph validation and optimization
  - Cycle detection algorithms
  - Performance optimization for large graphs
  - Graph validation edge cases

### Phase 3: Graph Diff Engine
- [ ] Graph comparison algorithms
- [ ] Node matching across versions (handle ID changes, moved modules)
- [ ] Movement detection (same module, different position)
- [ ] Structural change scoring
- [ ] Edge change analysis

### Phase 4: Configuration Analysis
- [ ] Configuration normalization
- [ ] Field-level comparison
- [ ] Change severity classification
- [ ] Impact assessment

### Phase 5: Visualization & Reporting
- [ ] Enhanced diff report formatting with topology insights
- [ ] Topology graph text rendering 
- [ ] Module change cards with before/after topology context
- [ ] Advanced summary statistics

### Phase 6: Advanced Features
- [ ] Interactive HTML reports
- [ ] Change impact prediction
- [ ] Integration with CI/CD pipelines
- [ ] Batch diff processing

## File Structure

```
src/tekmera/projections/blueprints/diff/
├── __init__.py                     # Platform routing and main interface
├── types.py                        # Data structure definitions
├── workfront_fusion.py             # Fusion-specific diff logic
├── make_com.py                     # Make.com-specific diff logic
├── topology/
│   ├── __init__.py
│   ├── extraction.py               # DAG extraction from blueprints
│   ├── workfront_fusion.py         # Fusion topology extraction
│   └── make_com.py                 # Make.com topology extraction
├── analysis/
│   ├── __init__.py
│   ├── structural.py               # Graph comparison algorithms
│   ├── configuration.py            # Configuration diff logic
│   └── scoring.py                  # Change impact scoring
└── visualization/
    ├── __init__.py
    ├── graph.py                    # Topology visualization
    ├── cards.py                    # Module change cards
    └── summary.py                  # Report summaries
```

## Design Principles

### 1. Platform Independence
- Separate implementation files for each platform
- Common interfaces and data structures
- Platform-specific flow semantics

### 2. Incremental Development
- Each phase builds on previous foundation
- Stub implementations enable end-to-end testing
- Real implementations replace stubs progressively

### 3. Graph-First Approach
- Topology changes are primary concern
- Configuration changes are secondary
- Movement detection is key insight

### 4. Visual Communication
- Graph visualization for stakeholder review
- Change cards for technical detail
- Summary statistics for executive overview

## Testing Strategy

### Unit Tests
- Topology extraction accuracy
- Graph comparison algorithms
- Configuration normalization
- Change classification logic

### Integration Tests
- End-to-end diff pipeline
- Multi-platform compatibility
- Complex blueprint scenarios
- Performance with large workflows

### Validation Tests
- Real blueprint pairs from production
- Known change scenarios
- Edge cases (empty blueprints, single modules)
- Regression testing

## Success Metrics

### Functional Requirements
- [ ] Accurately detects all module additions/removals
- [ ] Correctly identifies moved modules
- [ ] Finds configuration changes at field level
- [ ] Calculates meaningful structural change scores
- [ ] Generates readable reports for stakeholders

### Non-Functional Requirements
- [ ] Processes complex blueprints (50+ modules) in <5 seconds
- [ ] Supports all current Tekmera platforms
- [ ] Integrates cleanly with existing CLI
- [ ] Maintains backwards compatibility
- [ ] Extensible for future platforms

## Future Enhancements

### Advanced Analysis
- Semantic equivalence detection (different implementation, same outcome)
- Performance impact prediction
- Dependency chain analysis
- Rollback difficulty assessment

### Integration Features
- Git integration for version tracking
- Slack/Teams notifications for changes
- Approval workflows for high-risk changes
- Automated testing recommendations

### Visualization Improvements
- Interactive web interface
- Animation of changes over time
- Collaborative review features
- Export to various formats (Visio, Lucidchart)

## Current Implementation Status (as of 2025-11-20)

### ✅ What's Working Now:

1. **Complete CLI Pipeline**: `tekmera diff blueprint1.json blueprint2.json --format table|json|pdf`
2. **Real Workfront Fusion Topology Extraction**: 
   - Tested on production blueprints with 219-561 nodes
   - Recursive parsing of nested flows, routes, and error handlers
   - Accurate module classification and edge detection
3. **Integrated Diff Reports**: Topology analysis shows real before/after graph statistics
4. **Multi-Format Output**: Table, JSON, PDF all working with real topology data
5. **Platform Detection**: Automatic routing to correct topology extractors

### 🔧 Current Implementation Details:

**Key Files:**
- `src/tekmera/projections/blueprints/diff/topology/workfront_fusion.py` - Real topology extraction
- `src/tekmera/projections/blueprints/diff/topology/types.py` - Graph data structures
- `src/tekmera/projections/blueprints/diff/types.py` - Diff report types with topology integration

**Algorithm Insights:**
- Workfront Fusion uses deeply nested `flow` arrays with `routes` and `onerror` 
- Module classification patterns in `_is_trigger_module()`, `_is_router_module()`, `_is_filter_module()`
- Entry point detection: nodes with no incoming edges
- Path naming: `main`, `main_route_1`, `main_error`, `orphaned`

**Test Results:**
- Complex blueprint: 561 nodes, 560 edges, max depth 13, 193 branches
- Medium blueprint: 219 nodes, 217 edges, max depth 6, 82 branches  
- Simple blueprint: 7 nodes, 5 edges, max depth 1, 3 branches

### 🎯 Immediate Next Task: 

**Phase 3 - Graph Diff Engine**
- Location: `src/tekmera/projections/blueprints/diff/analysis/`
- Implement graph comparison algorithms for detecting structural differences
- Handle node matching across blueprint versions (account for ID changes)
- Detect moved modules (same module, different position in flow)
- Calculate structural change scoring based on topology changes

### 🚀 Development Priorities:

1. **Phase 3 Start**: Basic graph comparison (node additions/removals detection)
2. **Phase 3 Advanced**: Movement detection and structural scoring algorithms
3. **Phase 4**: Configuration field-level comparison and change analysis
4. **Phase 5**: Enhanced visualization and reporting with topology insights
5. **Phase 6**: Advanced features (interactive reports, CI/CD integration)

### 🧪 Testing Strategy:

- Use `./blueprints/make/` directory for Make.com testing
- Use `./blueprints/blueprint-*.json` for Workfront Fusion testing  
- Validate with `topology.validate()` method
- Test diff reports with: `python -m tekmera diff blueprint1.json blueprint2.json`

---

**Last Updated**: 2025-11-20  
**Current Phase**: Phase 2 - Topology Projection ✅ COMPLETED  
**Next Milestone**: Begin Phase 3 - Graph comparison algorithms for detecting structural differences