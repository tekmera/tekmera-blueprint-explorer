"""Module types analysis with platform-specific implementations.

This module provides platform-agnostic module type analysis by routing
to platform-specific implementations.
"""

from typing import Any, Dict

from ....meta.platform_detection import detect_platform
from ....meta.types import Platform, ProjectionResult, UnsupportedPlatformError


def analyze_module_types(
    blueprint: Dict[str, Any], platform: Platform = None
) -> ProjectionResult[Dict[str, Any]]:
    """
    Analyze module types used in a blueprint with platform-specific logic.

    Args:
        blueprint: Blueprint JSON data
        platform: Override platform detection (optional)

    Returns:
        ProjectionResult containing module type analysis

    Raises:
        UnsupportedPlatformError: If platform is not supported
    """
    if platform is None:
        platform = detect_platform(blueprint)

    if platform == Platform.WORKFRONT_FUSION:
        from .workfront_fusion import analyze_module_types as analyze_wf_types

        return analyze_wf_types(blueprint)
    elif platform == Platform.MAKE_COM:
        from .make_com import analyze_module_types as analyze_make_types

        return analyze_make_types(blueprint)
    else:
        raise UnsupportedPlatformError(
            f"Module types analysis not implemented for platform: {platform}"
        )
