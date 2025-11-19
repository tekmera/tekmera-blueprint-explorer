"""
Blueprint name extraction function.

## Function-Specific Contract
*Inherits baseline projection function contract*

### Purpose
Extracts the scenario/blueprint name string from automation platform JSON files.

### Platform-Specific Input Structures

#### Workfront Fusion
```json
{
  "name": "Scenario Name",          // Optional: scenario name
  "flow": [...],                    // Required for platform detection
  "metadata": {...}                 // Required for platform detection
}
```

#### Make.com
```json
{
  "name": "Scenario Name",          // Optional: scenario name
  "scenario": {                     // Required for platform detection
    "modules": [...]                // Required for platform detection
  }
}
```

### Function-Specific Error Handling
**Graceful Degradation**:
- Missing `name` field → Returns "Unnamed Scenario"
- Empty `name` field → Returns "Unnamed Scenario"
- Null `name` field → Returns "Unnamed Scenario"

### Output Data Type
`ProjectionResult[str]` where `data` contains the extracted scenario name.
"""

from typing import Any, Dict

from ....meta.platform_detection import detect_platform
from ....meta.types import Platform, ProjectionResult
from . import make_com, workfront_fusion

IMPLEMENTATIONS = {
    Platform.WORKFRONT_FUSION: workfront_fusion.name,
    Platform.MAKE_COM: make_com.name,
}


def name(blueprint: Dict[str, Any], platform: Platform = None) -> ProjectionResult[str]:
    """
    Extract scenario name from blueprint.

    Args:
        blueprint: Blueprint JSON object
        platform: Optional platform override

    Returns:
        ProjectionResult containing the scenario name
    """
    if platform is None:
        platform = detect_platform(blueprint)

    if platform in IMPLEMENTATIONS:
        return IMPLEMENTATIONS[platform](blueprint)

    raise ValueError(f"Platform {platform.value} not supported for name extraction")
