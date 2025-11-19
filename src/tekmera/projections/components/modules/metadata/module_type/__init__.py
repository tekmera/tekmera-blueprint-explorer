"""
Module type extraction function.

## Function-Specific Contract
*Inherits baseline module projection function contract*

### Purpose
Extracts the module type string from automation platform module JSON objects.

### Platform-Specific Input Structures

#### Workfront Fusion
```json
{
  "id": 1,
  "module": "workfront-workfront:searchv3",  // Required: module type
  "parameters": {...}                        // Optional: module parameters
}
```

#### Make.com
```json
{
  "id": "1",
  "module": "workfront:searchRecords",       // Required: module type
  "parameters": {...}                        // Optional: module parameters
}
```

### Function-Specific Error Handling
**Graceful Degradation**:
- Missing `module` field → Returns "unknown"
- Empty `module` field → Returns "unknown"
- Null `module` field → Returns "unknown"

### Output Data Type
`ModuleResult[str]` where `data` contains the extracted module type string.
"""

from .....meta.types import Module, ModuleResult, Platform
from . import make_com, workfront_fusion

IMPLEMENTATIONS = {
    Platform.WORKFRONT_FUSION: workfront_fusion.module_type,
    Platform.MAKE_COM: make_com.module_type,
}


def module_type(module: Module, platform: Platform) -> ModuleResult[str]:
    """
    Extract module type from module.

    Args:
        module: Module JSON object
        platform: Platform (required - no auto-detection at module level)

    Returns:
        ModuleResult containing the module type
    """
    if platform in IMPLEMENTATIONS:
        return IMPLEMENTATIONS[platform](module)

    raise ValueError(f"Platform {platform.value} not supported for module type extraction")
