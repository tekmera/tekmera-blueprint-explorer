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

### Phase 1: CLI Foundation (CURRENT)
- [x] CLI command structure (`tekmera diff blueprint1.json blueprint2.json`)
- [x] Argument validation and file loading
- [x] Platform detection for both blueprints
- [x] Stub report generation with placeholder data
- [x] Multi-format output (table, JSON, PDF)

### Phase 2: Topology Projection
- [ ] DAG extraction from blueprint JSON
- [ ] Flow following algorithms (handle nested structures)
- [ ] Platform-specific topology builders
- [ ] Graph validation and consistency checks

### Phase 3: Graph Diff Engine
- [ ] Graph comparison algorithms
- [ ] Node matching across versions
- [ ] Movement detection (same module, different position)
- [ ] Structural change scoring
- [ ] Edge change analysis

### Phase 4: Configuration Analysis
- [ ] Configuration normalization
- [ ] Field-level comparison
- [ ] Change severity classification
- [ ] Impact assessment

### Phase 5: Visualization & Reporting
- [ ] Topology graph rendering (text → visual)
- [ ] Module change cards
- [ ] Summary statistics
- [ ] Risk assessment algorithms

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

---

**Last Updated**: 2025-11-19  
**Current Phase**: Phase 1 - CLI Foundation  
**Next Milestone**: Complete topology projection implementation