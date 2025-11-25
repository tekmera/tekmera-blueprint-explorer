"""
Trigger detection function.

Platform-aware detection of scenario triggers from blueprint data.
"""

from typing import Any, Dict

from ....meta.platform_detection import detect_platform
from ....meta.trigger_types import UniversalTrigger
from ....meta.types import Platform, ProjectionResult
from . import make_com, workfront_fusion

IMPLEMENTATIONS = {
    Platform.WORKFRONT_FUSION: workfront_fusion.detect_trigger,
    Platform.MAKE_COM: make_com.detect_trigger,
}


def detect_trigger(
    blueprint: Dict[str, Any], platform: Platform = None
) -> ProjectionResult[UniversalTrigger]:
    """
    Detect the trigger module from a blueprint.

    Analyzes the blueprint to identify the first module (trigger) and returns
    a universal trigger representation with platform-specific details.

    Args:
        blueprint: Single blueprint dictionary
        platform: Optional platform override

    Returns:
        ProjectionResult containing UniversalTrigger data

    Raises:
        ValueError: If no trigger module found or platform not supported
    """
    if platform is None:
        platform = detect_platform(blueprint)

    if platform in IMPLEMENTATIONS:
        return IMPLEMENTATIONS[platform](blueprint)

    raise ValueError(f"Platform {platform.value} not supported for trigger detection")
