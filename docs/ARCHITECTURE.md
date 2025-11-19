# Tekmera Projection Functions Architecture

## Overview
Platform-aware, pure functional projection system. Each function takes blueprint JSON and returns standardized output without side effects.

## Core Principles
- **Pure Functions**: Immutable inputs, deterministic output, no side effects
- **Platform Aware**: Auto-detection with explicit override, extensible design
- **Composable**: Functions can be chained and combined

## Architecture
```
src/tekmera/projections/
├── components/              # Individual component analysis  
│   ├── modules/            # Module functions (metadata, content, validation)
│   ├── routers/            # Router component functions
│   ├── filters/            # Filter component functions  
│   └── other/              # Other component types
├── blueprints/             # Blueprint-level analysis (flexible input: single or multiple)
│   ├── basic/              # Fundamental info (name, count, complexity)
│   ├── flow/               # Flow analysis and connections  
│   ├── comparison/         # Blueprint diffs and comparison
│   └── corpus/             # Multi-blueprint analysis
└── meta/                   # Infrastructure
    ├── types.py            # Type definitions and utilities
    ├── platform_detection.py # Auto-detect platform
    └── utils/              # Platform-specific utilities (workfront_fusion/, make_com/)
```

## Function Types

### Components vs Blueprints
- **Components**: Analyze individual automation components (modules, routers, filters)
- **Blueprints**: Analyze blueprint-level data with flexible input (`Union[Dict, List[Dict]]`)

### Input/Output Patterns

#### Component Functions
```python
def module_type(module: Dict, platform: Platform) -> ModuleResult[str]:
    # Requires explicit platform, single component input
```

#### Blueprint Functions  
```python
def name(blueprints: Union[Dict, List[Dict]], platform: Platform = None) -> ProjectionResult[Union[str, List[str]]]:
    # Auto-detects platform, handles single or multiple blueprints
```

## Platform Support
- **Workfront Fusion**: `workfront_fusion` 
- **Make.com**: `make_com`
- **Extensible**: Easy to add new platforms

## Usage Examples

### Direct Function Calls
```python
# Blueprint functions - flexible input
from tekmera.projections.blueprints.basic import name, module_count
name_result = name(blueprint)                    # Single blueprint
name_result = name([blueprint1, blueprint2])    # Multiple blueprints

# Component functions - explicit platform required
from tekmera.projections.components.modules.metadata.module_type import module_type
type_result = module_type(module, Platform.WORKFRONT_FUSION)
```

### Main API
```python
# Auto-detection and flexible input
result = project("blueprints", "basic", "name", blueprint)          # Single
result = project("blueprints", "basic", "name", [bp1, bp2])         # Multiple

# Component analysis with explicit platform
result = project("components", "modules", "module_type", module, platform=Platform.WORKFRONT_FUSION)
```

## Key Benefits
- **Clean Separation**: Components (atomic) vs Blueprints (composite)
- **Flexible Input**: Functions handle single/multiple blueprints uniformly
- **Platform Consistency**: Same patterns across all platforms and component types
- **Pure Functional**: Composable, testable, deterministic
- **Extensible**: Easy to add new platforms and component types

## Migration Complete
✅ **Old Structure**: `single/` and `multiple/` directories removed  
✅ **New Structure**: `components/` and `blueprints/` implemented  
✅ **Flexible Input**: Blueprint functions accept `Union[Dict, List[Dict]]`  
✅ **Platform Separation**: Consistent platform-specific implementations  
✅ **Tested & Working**: All functions validated and tested