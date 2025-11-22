"""
Router text content extraction function.

## Function-Specific Contract
*Inherits baseline projection function contract*

### Purpose
Extracts all text content from router components including route flows,
filter conditions, variable names/values, and metadata.

### Input
Router component object extracted from blueprint flow.

### Platform-Specific Input Structures

#### Workfront Fusion & Make.com
```json
{
  "id": 5,
  "module": "builtin:BasicRouter",
  "routes": [
    {
      "flow": [
        // Array of modules in this route
      ]
    }
  ],
  "filter": {                    // Optional
    "name": "Filter Name",
    "conditions": [...]
  },
  "metadata": {                  // Optional
    "designer": {
      "name": "Custom Router Name"
    }
  }
}
```

### Output Data Type
- `ModuleResult[str]` where `data` contains extracted text content

### Text Content Sources
- Router metadata names and descriptions
- Filter condition names and values
- Variable names and expressions in route flows
- Module names and parameters within routes
- Designer custom names
"""

from .....meta.types import ModuleResult, Platform, RouterComponent
from . import make_com, workfront_fusion

IMPLEMENTATIONS = {
    Platform.WORKFRONT_FUSION: workfront_fusion.text_content,
    Platform.MAKE_COM: make_com.text_content,
}


def text_content(router: RouterComponent, platform: Platform) -> ModuleResult[str]:
    """
    Extract text content from router component.

    Args:
        router: Typed router component object
        platform: Platform identifier (required for component functions)

    Returns:
        ModuleResult containing extracted text content
    """
    if platform in IMPLEMENTATIONS:
        return IMPLEMENTATIONS[platform](router)

    raise ValueError(f"Platform {platform.value} not supported for router text content extraction")
