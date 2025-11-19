# Tekmera Projection Functions Architecture

## Overview

This document describes the platform-aware projection function architecture for Tekmera Fusion Explorer. This architecture transforms the codebase from a stateful, tightly-coupled design into a composable, functional system where each projection function takes blueprint JSON as input and returns standardized output without side effects.

## Core Principles

### Pure Functional Design
- **Immutable Inputs**: Functions never modify input blueprints
- **Deterministic Output**: Same input always produces identical output  
- **No Side Effects**: No I/O, logging, or external dependencies in projection functions
- **Composable**: Functions can be chained and combined
- **Testable**: Easy unit testing with deterministic behavior

### Platform Awareness
- **Multi-Platform Support**: Functions work across different automation platforms
- **Platform-Specific Logic**: Each platform can have optimized implementations
- **Auto-Detection**: Automatic platform identification with explicit override capability
- **Extensible**: Easy to add new platforms as they emerge

## Architecture Overview

```
src/tekmera/projections/
├── single/                    # Single blueprint projections
│   ├── basic/                 # Basic info (name, count, etc.)
│   ├── modules/               # Module analysis  
│   ├── flow/                  # Flow analysis
│   └── connections/           # Connection analysis
├── multiple/                  # Multi-blueprint projections
│   ├── corpus/                # Corpus analysis
│   ├── comparison/            # Blueprint comparison
│   └── patterns/              # Pattern detection
└── meta/                      # Metadata and infrastructure
    ├── types.py               # Type definitions
    ├── registry.py            # Function discovery
    ├── platform_detection.py  # Auto-detect platform
    └── utils.py               # Shared utilities
```

## Data Types and Schemas

### Platform Enumeration
```typescript
enum Platform {
  WORKFRONT_FUSION = "workfront_fusion",
  MAKE_COM = "make_com", 
  N8N = "n8n",
  ZAPIER = "zapier",
  POWER_AUTOMATE = "power_automate",
  INTEGROMAT = "integromat"  // Legacy Make.com
}
```

### Standard Output Schema
All projection functions return results with this standardized schema:

```typescript
interface ProjectionResult<T> {
  blueprint_id: string;         // Unique identifier for the blueprint
  blueprint_name: string;       // Human-readable name
  platform: Platform;          // Platform identifier
  data: T;                      // Function-specific data
  metadata: {
    function: string;           // Name of projection function
    version: string;            // Schema version
    computed_at: string;        // ISO timestamp
    input_hash: string;         // SHA256 of input for caching
    supported_platforms: Platform[];  // Platforms this function supports
  };
}
```

### Function Metadata
```typescript
interface FunctionMetadata {
  name: string;
  description: string;
  supported_platforms: Set<Platform>;
  category: string;             // "single" or "multiple" 
  subcategory: string;          // "basic", "modules", "flow", etc.
  return_type: string;
  examples: List<string>;
}
```

## Hierarchical Organization

### Primary Classification: Single vs Multiple Blueprints

The architecture uses a binary classification based on the number of input blueprints:

- **`single/`**: Functions that analyze a single blueprint
- **`multiple/`**: Functions that analyze multiple blueprints together

This separation is fundamental because:
- Single blueprint functions focus on intrinsic properties
- Multiple blueprint functions enable comparative and aggregate analysis
- Different algorithms and optimizations apply to each category

### Secondary Classification: Functional Domains

Within each primary category, functions are organized by analytical domain:

#### Single Blueprint Domains
- **`basic/`**: Fundamental properties (name, module count, complexity)
- **`modules/`**: Module-specific analysis (types, connections, parameters)
- **`flow/`**: Execution flow analysis (paths, branching, error handling)
- **`connections/`**: Connection and data flow analysis

#### Multiple Blueprint Domains  
- **`corpus/`**: Aggregate analysis across blueprints
- **`comparison/`**: Blueprint comparison and diff analysis
- **`patterns/`**: Pattern detection and similarity analysis

## Function Package Structure

Each functional domain is implemented as a package with platform-specific implementations:

```
single/basic/
├── __init__.py              # Package API and routing
├── metadata.py              # Function metadata definitions
├── workfront_fusion.py      # Workfront Fusion implementations
├── make_com.py              # Make.com implementations  
├── n8n.py                   # n8n implementations
└── common.py                # Platform-agnostic implementations
```

### Function Implementation Example

```python
# single/basic/metadata.py
FUNCTIONS = {
    "name": FunctionMetadata(
        name="name",
        description="Extract scenario/workflow name from blueprint",
        supported_platforms={Platform.WORKFRONT_FUSION, Platform.MAKE_COM, Platform.N8N},
        category="single",
        subcategory="basic",
        return_type="str",
        examples=["My Workfront Scenario", "User Onboarding Flow"]
    )
}

# single/basic/workfront_fusion.py
def name(blueprint: Dict[str, Any]) -> ProjectionResult[str]:
    """Extract scenario name from Workfront Fusion blueprint."""
    scenario_name = blueprint.get("name", "Unnamed Scenario")
    return ProjectionResult(
        blueprint_id=_get_blueprint_id(blueprint),
        blueprint_name=scenario_name,
        platform=Platform.WORKFRONT_FUSION,
        data=scenario_name,
        metadata={
            "function": "basic.name",
            "version": "1.0.0",
            "computed_at": _now_iso(),
            "input_hash": _hash_input(blueprint),
            "supported_platforms": [Platform.WORKFRONT_FUSION]
        }
    )
```

## Platform-Specific vs Common Implementations

### Platform-Specific Implementation
Use when platforms have significantly different JSON schemas or require platform-specific logic:

```python
# workfront_fusion.py
def module_count(blueprint: Dict[str, Any]) -> ProjectionResult[int]:
    """Count modules including nested routes and error handlers (Fusion-specific)."""
    modules = _get_modules_recursive_fusion(blueprint)  # Fusion-specific traversal
    return create_result(blueprint, Platform.WORKFRONT_FUSION, "module_count", len(modules))

# make_com.py  
def module_count(blueprint: Dict[str, Any]) -> ProjectionResult[int]:
    """Count modules in Make.com scenario."""
    modules = _get_modules_make(blueprint)  # Make.com-specific structure
    return create_result(blueprint, Platform.MAKE_COM, "module_count", len(modules))
```

### Common Implementation
Use when platforms have compatible schemas and unified logic is possible:

```python
# common.py
def name(blueprint: Dict[str, Any], platform: Platform) -> ProjectionResult[str]:
    """Extract name with platform-aware logic."""
    platform_extractors = {
        Platform.WORKFRONT_FUSION: lambda bp: bp.get("name", "Unnamed Scenario"),
        Platform.MAKE_COM: lambda bp: bp.get("scenario", {}).get("name", "Unnamed Scenario"),
        Platform.N8N: lambda bp: bp.get("name", "Unnamed Workflow"),
    }
    
    extractor = platform_extractors.get(platform)
    if not extractor:
        raise UnsupportedPlatformError(f"Platform {platform} not supported")
        
    scenario_name = extractor(blueprint)
    return create_result(blueprint, platform, "name", scenario_name)
```

## Function Registry and Discovery

### Registry System
The `ProjectionRegistry` provides centralized function discovery and routing:

```python
class ProjectionRegistry:
    """Central registry for all projection functions."""
    
    def get_function(self, category: str, subcategory: str, name: str, platform: Platform):
        """Get platform-specific function implementation."""
        # Try platform-specific implementation first
        # Fall back to common implementation with platform parameter
        
    def list_functions(self, platform: Platform = None) -> List[FunctionMetadata]:
        """List available functions, optionally filtered by platform."""
        
    def get_supported_platforms(self) -> Set[Platform]:
        """Get all supported platforms across all functions."""
```

### Auto-Discovery
Functions are automatically discovered through:
- Package introspection
- Metadata registration
- Platform capability detection

## Usage Patterns

### Main Projection API
```python
from tekmera.projections import project

# Single blueprint analysis
result = project("single", "basic", "name", [blueprint])

# Multiple blueprint analysis  
result = project("multiple", "corpus", "summary", blueprints)

# Explicit platform specification
result = project("single", "modules", "types", [blueprint], platform=Platform.N8N)
```

### Convenience Functions
```python
# High-level analysis functions
basic_info = get_basic_info(blueprint)
module_analysis = analyze_modules(blueprint) 
corpus_summary = analyze_corpus(blueprints)
```

### Function Composition
```python
# Chaining projections for complex analysis
pipeline = (
    project("single", "basic", "name") | 
    project("single", "modules", "extract") |
    project("single", "flow", "trace")
)
result = pipeline(blueprint)
```

## Platform Detection Strategy

### Automatic Detection
The system automatically detects platform from blueprint structure:

```python
def detect_platform(blueprint: Dict[str, Any]) -> Platform:
    """Auto-detect platform from blueprint JSON structure."""
    # Check for platform-specific markers
    if "flow" in blueprint and "metadata" in blueprint:
        return Platform.WORKFRONT_FUSION
    elif "scenario" in blueprint:
        return Platform.MAKE_COM
    elif "nodes" in blueprint and "connections" in blueprint:
        return Platform.N8N
    # ... additional detection logic
```

### Explicit Override
Users can explicitly specify platform when auto-detection is insufficient:

```python
# Auto-detect (recommended)
result = project("single", "basic", "name", [blueprint])

# Explicit override (when needed)
result = project("single", "basic", "name", [blueprint], platform=Platform.N8N)
```

## Migration Strategy

### Phase 1: Foundation (Weeks 1-2)
1. Create projection infrastructure (`meta/` package)
2. Implement basic projections for Workfront Fusion
3. Build registry and discovery system
4. Add comprehensive tests

### Phase 2: Core Projections (Weeks 3-4)
1. Migrate existing analysis logic to projection functions
2. Add platform detection and routing
3. Implement module and flow analysis projections

### Phase 3: Multi-Platform Support (Weeks 5-6)
1. Add Make.com platform support
2. Implement platform-specific optimizations
3. Add cross-platform compatibility analysis

### Phase 4: Advanced Features (Weeks 7-8)
1. Multi-blueprint projections (corpus analysis)
2. Comparison and diff projections
3. Pattern detection and similarity analysis

### Phase 5: CLI Migration (Weeks 9-10)
1. Refactor CLI to use projection API
2. Maintain backward compatibility
3. Add new projection-based commands

## Testing Strategy

### Unit Testing
- Each projection function tested in isolation
- Platform-specific test fixtures
- Determinism verification (same input → same output)

### Integration Testing  
- End-to-end projection pipeline testing
- Cross-platform compatibility testing
- Performance benchmarking

### Property-Based Testing
- Generate random blueprint variations
- Verify invariant properties across platforms
- Catch edge cases in platform detection

## Performance Considerations

### Caching Strategy
- Input hash-based result caching
- Platform-specific cache keys
- Cache invalidation on schema changes

### Parallel Execution
- Stateless functions enable parallelization
- Batch processing of multiple blueprints
- Concurrent projection execution

### Memory Optimization
- Immutable data structures
- Lazy evaluation where possible
- Streaming for large blueprint collections

## Extension Points

### Adding New Platforms
1. Create platform-specific implementation files
2. Add platform enum value
3. Update detection logic
4. Add platform-specific tests

### Adding New Functions
1. Create function in appropriate domain package
2. Add metadata description
3. Implement for supported platforms
4. Add to registry

### Custom Function Packages
- External packages can extend the registry
- Plugin architecture for third-party functions
- Standard interfaces for function discovery

## Error Handling

### Function-Level Errors
- Input validation at package boundaries
- Graceful degradation for malformed data
- Clear error messages with context

### Platform Compatibility
- Explicit unsupported platform errors
- Feature availability checking
- Compatibility scoring between platforms

## Documentation and Discoverability

### Self-Describing Functions
- Rich metadata for each function
- Usage examples in metadata
- Platform compatibility matrix

### Auto-Generated Documentation
- Function registry powers documentation generation
- Interactive function explorer
- Platform-specific usage guides

## Future Enhancements

### Cross-Platform Analysis
- Blueprint compatibility scoring across platforms
- Migration feasibility analysis
- Feature gap identification

### Function Composition Language
- Domain-specific language for projection pipelines
- Visual function composition interface
- Saved analysis templates

### Real-Time Analysis
- Streaming blueprint analysis
- Incremental updates
- Live dashboard integration

---

This architecture provides a solid foundation for scalable, maintainable, and extensible blueprint analysis across multiple automation platforms while maintaining the pure functional principles essential for reliable and testable code.