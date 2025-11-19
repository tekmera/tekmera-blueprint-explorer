# Tekmera Projection Functions Architecture

## Overview

This document describes the platform-aware projection function architecture for Tekmera Explorer. This architecture transforms the codebase from a stateful, tightly-coupled design into a composable, functional system where each projection function takes one or more blueprint JSON as input and returns standardized output without side effects.

## Core Principles

### Pure Functional Design
- **Immutable Inputs**: Functions never modify input blueprints
- **Deterministic Output**: Same input always produces identical output  
- **No Side Effects**: No I/O, external dependencies in projection functions
- **Composable**: Functions can (and should) be chained and combined
- **Testable**: Easy unit testing with deterministic behavior

### Platform Awareness
- **Multi-Platform Support**: Functions work across different automation platforms
- **Platform-Specific Logic**: Each platform can have optimized implementations
- **Auto-Detection**: Automatic platform identification with explicit override capability
- **Extensible**: Easy to add new platforms as they emerge

## Architecture Overview

```
src/tekmera/
├── projections/                   # Pure projection functions (business logic)
│   ├── single/                    # Single blueprint projections
│   │   ├── basic/                 # Basic info (name, count, etc.)
│   │   ├── modules/               # Module analysis  
│   │   ├── flow/                  # Flow analysis
│   │   └── connections/           # Connection analysis
│   ├── multiple/                  # Multi-blueprint projections
│   │   ├── corpus/                # Corpus analysis
│   │   ├── comparison/            # Blueprint comparison
│   │   └── patterns/              # Pattern detection
│   └── meta/                      # Metadata and infrastructure
│       ├── types.py               # Type definitions
│       ├── registry.py            # Function discovery
│       ├── platform_detection.py  # Auto-detect platform
│       └── utils.py               # Shared utilities
├── clients/                       # Client implementations (UI/UX)
│   ├── cli/                       # Command-line interface client
│   │   ├── single_use/            # Direct command execution
│   │   ├── formatters/            # Output formatting
│   │   └── main.py                # CLI entry point
│   └── interactive/               # Interactive exploration client
│       ├── menus/                 # Menu system
│       ├── explorers/             # Interactive explorers
│       └── main.py                # Interactive entry point
└── legacy/                        # Existing code (during migration)
    └── ...
```

**Key Principle**: Clients consume projections. Projection functions are pure business logic with no UI dependencies. Clients are separate packages that consume projection functions via the standard API, enabling reusability, testability, scalability, and maintainability.

## Data Types and Schemas

### Platform Enumeration
```typescript
enum Platform {
  WORKFRONT_FUSION = "workfront_fusion",
  MAKE_COM = "make_com", 
  N8N = "n8n",
  ZAPIER = "zapier",
  POWER_AUTOMATE = "power_automate"
}
```

### Standard Output Schema
```typescript
interface ProjectionResult<T> {
  blueprint_id: string;
  blueprint_name: string;
  platform: Platform;
  data: T;
  metadata: {
    function: string;
    version: string;
    computed_at: string;
    input_hash: string;
    supported_platforms: Platform[];
  };
}
```

## Hierarchical Organization

### Primary Classification: Single vs Multiple Blueprints
- **`single/`**: Functions that analyze a single blueprint (intrinsic properties)
- **`multiple/`**: Functions that analyze multiple blueprints (comparative/aggregate analysis)

### Secondary Classification: Functional Domains
- **Single**: `basic/` (name, count), `modules/` (analysis), `flow/` (paths), `connections/` (data flow)
- **Multiple**: `corpus/` (aggregate), `comparison/` (diffs), `patterns/` (similarity)

## Baseline Function Contract

All projection functions MUST inherit and implement this baseline contract:

### Universal Input Requirements
- **blueprint**: `Dict[str, Any]` - Valid JSON object representing automation platform blueprint
- **platform**: `Optional[Platform]` - Platform override (auto-detected if None)

### Universal Output Contract
Returns `ProjectionResult[T]` where T is function-specific data type:
- **data**: Function-specific extracted/computed data
- **platform**: Auto-detected or explicitly specified platform
- **blueprint_id**: Deterministic hash-based blueprint identifier
- **blueprint_name**: Extracted blueprint name (using name projection if needed)
- **metadata**: Standard execution metadata (function, version, timestamp, input_hash, supported_platforms)

### Universal Error Handling
#### Automatic Platform Detection Errors
- **UnsupportedPlatformError**: Blueprint structure doesn't match any supported platform
#### Function-Specific Errors  
- **ValueError**: Specified platform not supported for this specific function
- **KeyError**: Required blueprint field missing (function-specific)

### Universal Behavioral Guarantees
1. **Immutability**: Input blueprint is NEVER modified
2. **Determinism**: Identical input always produces identical output
3. **No Side Effects**: No I/O, logging, external dependencies, or state changes
4. **Platform Independence**: Function behavior is identical across all supported platforms
5. **Graceful Degradation**: Missing optional fields default to sensible values

### Function Documentation Rules
1. **Baseline Inheritance**: All functions inherit the above contract automatically
2. **Function-Specific Documentation**: Only document what differs from baseline
3. **Required Sections**: Purpose, platform-specific input structures, function-specific error handling
4. **Optional Sections**: Complex examples, performance notes, algorithm details

## Function Package Structure

Each function is a subpackage with platform-specific implementations:

```
single/basic/
├── __init__.py                    # Package API and auto-discovery
├── metadata.py                    # Package-level metadata
├── name/                          # Name extraction function
│   ├── __init__.py               # Function API and routing
│   ├── workfront_fusion.py       # Workfront Fusion implementation
│   ├── make_com.py               # Make.com implementation
│   ├── n8n.py                    # n8n implementation
│   └── common.py                 # Cross-platform implementation
├── module_count/                  # Module count function
│   ├── __init__.py
│   ├── workfront_fusion.py
│   ├── make_com.py
│   └── common.py
└── complexity/                    # Complexity analysis function
    ├── __init__.py
    ├── workfront_fusion.py
    ├── algorithms.py             # Shared complexity algorithms
    └── common.py
```

### Function Implementation Pattern

```python
# single/basic/name/__init__.py
from ....meta.types import Platform
from . import workfront_fusion, make_com, n8n, common

IMPLEMENTATIONS = {
    Platform.WORKFRONT_FUSION: workfront_fusion.name,
    Platform.MAKE_COM: make_com.name,
    Platform.N8N: n8n.name,
}

def name(blueprint, platform=None):
    """Extract scenario name - main entry point."""
    if platform in IMPLEMENTATIONS:
        return IMPLEMENTATIONS[platform](blueprint)
    return common.name(blueprint, platform)

# single/basic/name/workfront_fusion.py
def name(blueprint):
    """Extract scenario name from Workfront Fusion blueprint."""
    scenario_name = blueprint.get("name", "Unnamed Scenario")
    return create_result(blueprint, Platform.WORKFRONT_FUSION, "basic.name", scenario_name)
```

## Platform Detection

The `detect_platform()` function enables seamless multi-platform support:

```python
# meta/platform_detection.py
def detect_platform(blueprint: Dict[str, Any]) -> Platform:
    """Auto-detect platform from blueprint JSON structure."""
    # Check metadata.zone first (most reliable)
    metadata = blueprint.get("metadata", {})
    if isinstance(metadata, dict):
        zone = metadata.get("zone", "")
        if "workfrontfusion.com" in zone:
            return Platform.WORKFRONT_FUSION
        elif "make.com" in zone or "make.celonis.com" in zone:
            return Platform.MAKE_COM
    
    # Fallback to structure-based detection
    if "flow" in blueprint:
        return Platform.WORKFRONT_FUSION
    else:
        raise UnsupportedPlatformError("Unable to detect platform")
```

## CLI Interface Design

### Dual Interface Modes

```bash
# Interactive mode (current default)
tekmera analyze ./blueprints/
tekmera interactive ./blueprints/

# Single-use commands (new)
tekmera name ./blueprint.json
tekmera module-count ./blueprint.json
tekmera complexity ./blueprint.json --algorithm cyclomatic
tekmera corpus-summary ./blueprints/*.json
```

### Command Structure

**All commands automatically detect the platform** from blueprint JSON structure, with optional explicit override via `--platform` flag:

```bash
# Basic projections
tekmera name FILE                              # Extract scenario name
tekmera module-count FILE                      # Count total modules  
tekmera complexity FILE [--algorithm ALGO]    # Calculate complexity
tekmera count FILE                             # Alias for module-count

# Advanced analysis
tekmera flow-paths FILE [--max-depth N]       # Execution paths
tekmera modules FILE [--include-orphans]      # Module analysis

# Multi-blueprint analysis  
tekmera corpus-summary FILES...               # Corpus statistics
tekmera compare FILE1 FILE2                   # Compare blueprints
tekmera shared-modules FILES...               # Common modules

# Platform override
tekmera name FILE --platform workfront-fusion
tekmera name FILE --platform make-com
```

### Standard Options

```bash
--platform PLATFORM         # Override auto-detection
--format FORMAT             # Output: json, table, yaml, csv
--output FILE, -o FILE      # Output file
--verbose, -v               # Debug information
--quiet, -q                 # Suppress output
```

### File Input Patterns

```bash
# Single files
tekmera name ./blueprint.json

# Multiple files  
tekmera corpus-summary ./bp1.json ./bp2.json
tekmera corpus-summary ./blueprints/*.json     # Glob patterns
tekmera corpus-summary ./blueprints/           # Directory

# Stdin
cat blueprint.json | tekmera name -
echo '{"name":"test"}' | tekmera name --platform n8n
```

### Output Formats

```bash
# Table (interactive default)
tekmera module-count ./blueprint.json
┌─────────────────┬───────┐
│ Module Type     │ Count │
├─────────────────┼───────┤
│ workfront:search│   3   │
└─────────────────┴───────┘

# JSON (scripting default)
tekmera name ./blueprint.json --format json
{"blueprint_id": "bp-123", "platform": "workfront_fusion", 
 "data": "My Scenario", "metadata": {...}}

# CSV (spreadsheet import)
tekmera corpus-summary ./blueprints/*.json --format csv
name,module_count,complexity,platform
"Scenario 1",15,8,"workfront_fusion"
```

## Programming API Usage

```python
from tekmera.projections import project
from tekmera.projections.meta.platform_detection import detect_platform

# Main API - auto-detects platform
result = project("single", "basic", "name", [blueprint])

# Manual platform detection
platform = detect_platform(blueprint)
result = project("single", "basic", "name", [blueprint], platform=platform)

# Multi-blueprint analysis
summary = project("multiple", "corpus", "summary", blueprints)

# Direct function calls
from tekmera.projections.single.basic import name, module_count
name_result = name(blueprint)           # Auto-detects platform
count_result = module_count(blueprint)
```

### API Integration

```python
# projections/__init__.py - Main API with auto-detection
def project(category: str, subcategory: str, function: str, 
           blueprints: List[Dict], platform: Platform = None, **kwargs):
    if platform is None and blueprints:
        platform = detect_platform(blueprints[0])
    
    registry = ProjectionRegistry()
    func = registry.get_function(category, subcategory, function, platform)
    
    return func(blueprints[0] if len(blueprints) == 1 else blueprints, **kwargs)
```

## Function Registry and Discovery

```python
class ProjectionRegistry:
    """Central registry for function discovery and routing."""
    
    def get_function(self, category: str, subcategory: str, name: str, platform: Platform):
        """Get platform-specific function implementation."""
        # Try platform-specific, fall back to common
        
    def list_functions(self, platform: Platform = None) -> List[FunctionMetadata]:
        """List available functions, optionally filtered by platform."""
        
    def get_supported_platforms(self) -> Set[Platform]:
        """Get all supported platforms."""
```

Auto-discovery through package introspection and metadata registration.

## Migration Strategy

### Implementation Phases
1. **Foundation (Weeks 1-2)**: Create projection infrastructure and basic functions
2. **Core Migration (Weeks 3-4)**: Convert existing analysis logic to projections  
3. **Multi-Platform (Weeks 5-6)**: Add platform support and detection
4. **Advanced Features (Weeks 7-8)**: Multi-blueprint and comparison projections
5. **CLI Migration (Weeks 9-10)**: Refactor CLI to use projection API

## Testing and Performance

### Testing Strategy
- **Unit Testing**: Each projection function tested in isolation with deterministic verification
- **Integration Testing**: End-to-end projection pipelines and cross-platform compatibility
- **Property-Based Testing**: Random blueprint variations to catch edge cases

### Test Package Structure Rules
Test packages MUST mirror production code structure exactly with platform separation enforced:

```
tests/
├── projections/                    # Mirrors src/tekmera/projections/
│   ├── meta/                       # Meta component tests
│   │   ├── test_platform_detection.py
│   │   ├── test_registry.py
│   │   └── test_types.py
│   ├── single/                     # Single blueprint tests
│   │   └── basic/                  # Basic projection tests
│   │       └── name/               # Name function tests
│   │           ├── test_workfront_fusion.py  # Platform-specific tests
│   │           ├── test_make_com.py          # Platform-specific tests
│   │           └── test_name.py              # Integration tests
│   └── multiple/                   # Multi-blueprint tests
│       └── ...
```

**Platform Separation Rules**:
1. **Platform-Specific Test Files**: Each platform implementation gets its own test file (e.g., `test_workfront_fusion.py`, `test_make_com.py`)
2. **Integration Test Files**: Cross-platform integration tests in separate files (e.g., `test_name.py`)
3. **No Shared Test Code**: No shared test utilities or fixtures between platforms
4. **Mirror Production Structure**: Test directory structure must exactly match `src/tekmera/projections/` hierarchy
5. **Platform Test Isolation**: Platform-specific tests must not import or reference other platform implementations

**Required Test Patterns**:
Each platform-specific test file MUST include these three test categories:
1. **Blue Sky Example**: Happy path test with valid, typical input data
2. **Complex Example**: Edge case test with complex/unusual but valid input data  
3. **Error Handling**: Test error scenarios with invalid input and proper exception handling

**Test Method Naming Convention**:
- Blue sky: `test_<function>_blue_sky()`
- Complex: `test_<function>_complex_case()`
- Error handling: `test_<function>_error_<specific_error>()`

### Performance Optimizations
- **Caching**: Input hash-based result caching with platform-specific keys
- **Parallel Execution**: Stateless functions enable concurrent projection execution
- **Memory Optimization**: Immutable data structures and lazy evaluation

## Extension Points

### Adding New Platforms
1. Create platform-specific implementation files in existing function packages
2. Add platform enum value and update detection logic
3. Add platform-specific tests and utilities

### Adding New Functions  
1. Create function subpackage in appropriate domain
2. Implement for supported platforms with shared algorithms as needed
3. Add to registry and include comprehensive tests

### Custom Clients
External packages can extend the registry and create custom interfaces (web dashboards, IDE plugins, etc.) that consume the same projection functions.

## Error Handling and Documentation

### Error Handling
- **Input Validation**: At client boundaries with clear error messages
- **Platform Compatibility**: Explicit unsupported platform errors with helpful guidance
- **Graceful Degradation**: Fallbacks for malformed data

### Self-Describing System
- **Function Metadata**: Rich descriptions, usage examples, platform compatibility
- **Auto-Generated Docs**: Registry powers documentation generation and interactive exploration
- **Platform Discovery Tools**: CLI tools for platform experts (`tekmera dev list-functions --platform make-com`)

## Future Enhancements

- **Cross-Platform Analysis**: Compatibility scoring and migration feasibility analysis
- **Function Composition**: DSL for projection pipelines and visual composition interface  
- **Real-Time Analysis**: Streaming blueprint processing with incremental updates

---

This architecture provides a solid foundation for scalable, maintainable, and extensible blueprint analysis across multiple automation platforms while maintaining pure functional principles essential for reliable and testable code.