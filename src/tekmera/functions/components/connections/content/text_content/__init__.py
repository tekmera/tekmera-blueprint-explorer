"""
Connection text content extraction function.

### Purpose
Extracts all textual content from a connection configuration for search and analysis purposes.

### Output Data Type
`ModuleResult[str]` where `data` contains searchable text about the connection including:
- Connection ID and labels
- Service names and types
- User context (emails, usernames)
- Authentication method information
"""

from .....meta.types import ModuleComponent, ModuleResult, Platform
from . import make_com, workfront_fusion

IMPLEMENTATIONS = {
    Platform.WORKFRONT_FUSION: workfront_fusion.text_content,
    Platform.MAKE_COM: make_com.text_content,
}


def text_content(module_component: ModuleComponent, platform: Platform) -> ModuleResult[str]:
    """
    Extract text content from connection component.

    Args:
        module_component: Typed ModuleComponent object containing connection data
        platform: Platform (required - no auto-detection at module level)

    Returns:
        ModuleResult containing the connection's text content for search
    """
    if platform in IMPLEMENTATIONS:
        return IMPLEMENTATIONS[platform](module_component, platform)

    raise ValueError(f"Platform {platform.value} not supported for connection text content extraction")