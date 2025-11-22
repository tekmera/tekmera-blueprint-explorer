"""
Error handler text content extraction function.

## Function-Specific Contract
*Inherits baseline projection function contract*

### Purpose
Extracts all text content from error handler components including retry configurations,
error module parameters, and metadata.

### Input
Error handler component object extracted from blueprint flow.

### Platform-Specific Input Structures

#### Workfront Fusion & Make.com
```json
{
  "type": "error_handler",
  "handlers_count": 1,
  "item": {
    "id": 22,
    "module": "workfront-workfront:watchEvents",
    "onerror": [
      {
        "id": 58,
        "module": "builtin:Break",
        "parameters": {},
        "mapper": {
          "count": "3",
          "retry": true,
          "interval": "10"
        }
      }
    ]
  }
}
```

### Output Data Type
- `ModuleResult[str]` where `data` contains extracted text content

### Text Content Sources
- Error handler module names and types
- Retry configuration (count, interval)
- Error handling parameters
- Custom designer names and metadata
"""

from .....meta.types import ErrorHandlerComponent, ModuleResult, Platform
from . import make_com, workfront_fusion

IMPLEMENTATIONS = {
    Platform.WORKFRONT_FUSION: workfront_fusion.text_content,
    Platform.MAKE_COM: make_com.text_content,
}


def text_content(
    error_handler_component: ErrorHandlerComponent, platform: Platform
) -> ModuleResult[str]:
    """
    Extract text content from error handler component.

    Args:
        error_handler_component: Typed error handler component object
        platform: Platform identifier (required for component functions)

    Returns:
        ModuleResult containing extracted text content
    """
    if platform in IMPLEMENTATIONS:
        return IMPLEMENTATIONS[platform](error_handler_component)

    raise ValueError(
        f"Platform {platform.value} not supported for error handler text content extraction"
    )
