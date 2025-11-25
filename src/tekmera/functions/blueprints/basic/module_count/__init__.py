"""
Blueprint module count projection function.

## Function-Specific Contract
*Inherits baseline projection function contract*

### Purpose
Counts the total number of modules in automation platform JSON files, including nested flows.
Supports both single blueprint and multiple blueprints as input.

### Input
Accepts Union[Dict, List[Dict]] to handle both single and multiple blueprints.

### Platform-Specific Input Structures

#### Workfront Fusion
```json
{
  "flow": [                            // Required: main flow array
    {
      "id": 1,
      "module": "workfront:search",
      "routes": [                      // Optional: nested flows
        {"flow": [...]}
      ],
      "onerror": [...]                 // Optional: error handler flows
    }
  ],
  "metadata": {                        // Optional: may contain orphaned modules
    "designer": {
      "orphans": [[...]]
    }
  }
}
```

#### Make.com
```json
{
  "scenario": {                        // Required for platform detection
    "modules": [                       // Required: modules array
      {
        "id": 18,
        "module": "util:SetVariable2"
      }
    ]
  }
}
```

### Function-Specific Error Handling
**Graceful Degradation**:
- Missing `flow` field → Returns 0
- Empty `flow` array → Returns 0
- Malformed modules → Skips invalid entries, counts valid ones

### Output Data Type
- Single blueprint: `ProjectionResult[int]` where `data` contains the total module count
- Multiple blueprints: `ProjectionResult[List[int]]` where `data` contains list of module counts
"""

from typing import List, Union

from ....meta.platform_detection import detect_platform
from ....meta.types import BlueprintInput, Platform, ProjectionResult, normalize_blueprint_input
from . import make_com, workfront_fusion

IMPLEMENTATIONS = {
    Platform.WORKFRONT_FUSION: workfront_fusion.module_count,
    Platform.MAKE_COM: make_com.module_count,
}


def module_count(
    blueprints: BlueprintInput, platform: Platform = None
) -> ProjectionResult[Union[int, List[int]]]:
    """
    Count total modules in blueprint(s) including nested flows.

    Args:
        blueprints: Single blueprint or list of blueprints
        platform: Optional platform override

    Returns:
        ProjectionResult containing the module count(s)
    """
    normalized_blueprints = normalize_blueprint_input(blueprints)

    if platform is None:
        platform = detect_platform(normalized_blueprints[0])

    if platform in IMPLEMENTATIONS:
        return IMPLEMENTATIONS[platform](normalized_blueprints)

    raise ValueError(f"Platform {platform.value} not supported for module counting")
