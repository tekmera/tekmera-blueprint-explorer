"""
Blueprint module count projection function.

## Function-Specific Contract
*Inherits baseline projection function contract*

### Purpose
Counts the total number of modules in automation platform JSON files, including nested flows.

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
`ProjectionResult[int]` where `data` contains the total module count.
"""

from typing import Any, Dict

from ....meta.platform_detection import detect_platform
from ....meta.types import Platform, ProjectionResult
from . import make_com, workfront_fusion

IMPLEMENTATIONS = {
    Platform.WORKFRONT_FUSION: workfront_fusion.module_count,
    Platform.MAKE_COM: make_com.module_count,
}


def module_count(blueprint: Dict[str, Any], platform: Platform = None) -> ProjectionResult[int]:
    """
    Count total modules in blueprint including nested flows.

    Args:
        blueprint: Blueprint JSON object
        platform: Optional platform override

    Returns:
        ProjectionResult containing the module count
    """
    if platform is None:
        platform = detect_platform(blueprint)

    if platform in IMPLEMENTATIONS:
        return IMPLEMENTATIONS[platform](blueprint)

    raise ValueError(f"Platform {platform.value} not supported for module counting")
