"""
Filter text content extraction function.

## Function-Specific Contract
*Inherits baseline projection function contract*

### Purpose
Extracts all text content from filter components including condition names,
comparison values, variables, and metadata.

### Input
Filter component object extracted from blueprint flow.

### Platform-Specific Input Structures

#### Workfront Fusion & Make.com
```json
{
  "type": "filter",
  "filter_name": "Customer Intake Form",
  "conditions_count": 2,
  "item": {
    "id": 103,
    "module": "builtin:BasicRouter",
    "filter": {
      "name": "Customer Intake Form",
      "conditions": [
        [
          {
            "a": "{{16.data.name}}",
            "b": "IKP - Customer Project Intake",
            "o": "text:equal"
          }
        ]
      ]
    }
  }
}
```

### Output Data Type
- `ModuleResult[str]` where `data` contains extracted text content

### Text Content Sources
- Filter names and descriptions
- Condition variable expressions (a, b values)
- Operator descriptions
- Custom metadata names
"""

from .....meta.types import FilterComponent, ModuleResult, Platform
from . import make_com, workfront_fusion

IMPLEMENTATIONS = {
    Platform.WORKFRONT_FUSION: workfront_fusion.text_content,
    Platform.MAKE_COM: make_com.text_content,
}


def text_content(filter_component: FilterComponent, platform: Platform) -> ModuleResult[str]:
    """
    Extract text content from filter component.

    Args:
        filter_component: Typed filter component object
        platform: Platform identifier (required for component functions)

    Returns:
        ModuleResult containing extracted text content
    """
    if platform in IMPLEMENTATIONS:
        return IMPLEMENTATIONS[platform](filter_component)

    raise ValueError(f"Platform {platform.value} not supported for filter text content extraction")
