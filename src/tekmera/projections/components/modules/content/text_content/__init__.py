"""
Module text content extraction function.

### Purpose
Extracts all textual content from a module for search and analysis purposes.

### Output Data Type
`ModuleResult[str]` where `data` contains the module JSON serialized as a string.
This allows for text searching across all module parameters and configuration.
"""

from .....meta.types import ModuleComponent, ModuleResult, Platform
from . import make_com, workfront_fusion

IMPLEMENTATIONS = {
    Platform.WORKFRONT_FUSION: workfront_fusion.text_content,
    Platform.MAKE_COM: make_com.text_content,
}


def text_content(module_component: ModuleComponent, platform: Platform) -> ModuleResult[str]:
    """
    Extract text content from module component.

    Args:
        module_component: Typed ModuleComponent object
        platform: Platform (required - no auto-detection at module level)

    Returns:
        ModuleResult containing the module's text content
    """
    if platform in IMPLEMENTATIONS:
        return IMPLEMENTATIONS[platform](module_component, platform)

    raise ValueError(f"Platform {platform.value} not supported for text content extraction")
