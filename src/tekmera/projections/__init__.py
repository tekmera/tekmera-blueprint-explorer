"""
Tekmera Projection Functions

Pure functional blueprint analysis system with platform awareness.
Main entry point for projection function access.
"""

from typing import Any, Dict, List, Optional

from .meta.platform_detection import detect_platform
from .meta.registry import ProjectionRegistry
from .meta.types import Platform, ProjectionResult


def project(
    category: str,
    subcategory: str,
    function: str,
    blueprints: List[Dict[str, Any]],
    platform: Optional[Platform] = None,
    **kwargs,
) -> ProjectionResult:
    """
    Main projection API with automatic platform detection.

    Args:
        category: 'single' or 'multiple'
        subcategory: Domain like 'basic', 'modules', 'corpus', etc.
        function: Specific function name
        blueprints: List of blueprint JSON objects
        platform: Optional platform override
        **kwargs: Additional function parameters

    Returns:
        ProjectionResult with standardized output
    """
    if platform is None and blueprints:
        platform = detect_platform(blueprints[0])

    registry = ProjectionRegistry()
    func = registry.get_function(category, subcategory, function, platform)

    if category == "single":
        return func(blueprints[0], **kwargs)
    else:
        return func(blueprints, **kwargs)
