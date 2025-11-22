"""Blueprint topology extraction.

This module provides pure topology graph extraction from blueprint JSON.
This is analysis functionality that stays in projections.
"""

from typing import Any, Dict
from ...meta.platform_detection import detect_platform
from ...meta.types import Platform, ProjectionResult, UnsupportedPlatformError


def extract_topology(blueprint: Dict[str, Any]) -> ProjectionResult:
    """
    Extract topology graph from a blueprint.
    
    This function performs pure analysis without presentation concerns.
    """
    platform = detect_platform(blueprint)
    
    if platform == Platform.WORKFRONT_FUSION:
        from .workfront_fusion import extract_workfront_topology
        return extract_workfront_topology(blueprint)
    elif platform == Platform.MAKE_COM:
        from .make_com import extract_make_topology
        return extract_make_topology(blueprint)
    else:
        raise UnsupportedPlatformError(f"Topology extraction not implemented for platform: {platform}")


__all__ = ["extract_topology"]