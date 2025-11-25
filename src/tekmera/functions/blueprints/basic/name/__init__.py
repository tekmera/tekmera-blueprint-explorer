"""
Blueprint name extraction function.

## Function-Specific Contract
*Inherits baseline projection function contract*

### Purpose
Extracts the scenario/blueprint name string from automation platform JSON files.
Supports both single blueprint and multiple blueprints as input.

### Input
Accepts Union[Dict, List[Dict]] to handle both single and multiple blueprints.

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
- Single blueprint: `ProjectionResult[str]` where `data` contains the extracted scenario name
- Multiple blueprints: `ProjectionResult[List[str]]` where `data` contains list of scenario names
"""

from typing import List, Union

from ....meta.platform_detection import detect_platform
from ....meta.types import BlueprintInput, Platform, ProjectionResult, normalize_blueprint_input
from . import make_com, workfront_fusion

IMPLEMENTATIONS = {
    Platform.WORKFRONT_FUSION: workfront_fusion.name,
    Platform.MAKE_COM: make_com.name,
}


def name(
    blueprints: BlueprintInput, platform: Platform = None
) -> ProjectionResult[Union[str, List[str]]]:
    """
    Extract scenario name(s) from blueprint(s).

    Args:
        blueprints: Single blueprint or list of blueprints
        platform: Optional platform override

    Returns:
        ProjectionResult containing the scenario name(s)
    """
    normalized_blueprints = normalize_blueprint_input(blueprints)

    if platform is None:
        platform = detect_platform(normalized_blueprints[0])

    if platform in IMPLEMENTATIONS:
        return IMPLEMENTATIONS[platform](normalized_blueprints)

    raise ValueError(f"Platform {platform.value} not supported for name extraction")
