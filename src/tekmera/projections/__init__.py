"""
Tekmera Projection Functions

Pure functional blueprint analysis system with platform awareness.
Main entry point for projection function access.
"""

from typing import Any, Dict, List, Optional, Union

from .meta.platform_detection import detect_platform
from .meta.registry import ProjectionRegistry
from .meta.types import BlueprintInput, ModuleResult, Platform, ProjectionResult


def project(
    category: str,
    subcategory: str,
    function: str,
    input_data: Union[Dict[str, Any], List[Dict[str, Any]]],
    platform: Optional[Platform] = None,
    **kwargs,
) -> Union[ProjectionResult, ModuleResult]:
    """
    Main projection API with flexible input handling.

    Args:
        category: 'components' or 'blueprints'
        subcategory: Domain like 'modules', 'basic', 'corpus', etc.
        function: Specific function name
        input_data: Component object (for components) or blueprint(s) (for blueprints)
        platform: Optional platform override (required for components)
        **kwargs: Additional function parameters

    Returns:
        ProjectionResult or ModuleResult with standardized output
    """
    registry = ProjectionRegistry()

    if category == "components":
        # Component functions require explicit platform and single component input
        if platform is None:
            raise ValueError("Platform required for component functions")
        if isinstance(input_data, list):
            raise ValueError("Component functions accept single component only")

        func = registry.get_function(category, subcategory, function, platform)
        return func(input_data, platform, **kwargs)

    elif category == "blueprints":
        # Blueprint functions auto-detect platform and handle flexible input
        # Import the main function directly (not platform-specific implementation)
        import importlib
        module_path = f"tekmera.projections.{category}.{subcategory}.{function}"
        module = importlib.import_module(module_path)
        func = getattr(module, function)
        return func(input_data, **kwargs)

    else:
        raise ValueError(f"Unknown category: {category}. Use 'components' or 'blueprints'")


# Backward compatibility functions for legacy API
def project_single(
    subcategory: str,
    function: str,
    blueprint: Dict[str, Any],
    platform: Optional[Platform] = None,
    **kwargs,
) -> ProjectionResult:
    """Legacy API for single blueprint projections."""
    return project("blueprints", subcategory, function, blueprint, platform, **kwargs)


def project_multiple(
    subcategory: str,
    function: str,
    blueprints: List[Dict[str, Any]],
    platform: Optional[Platform] = None,
    **kwargs,
) -> ProjectionResult:
    """Legacy API for multiple blueprint projections."""
    return project("blueprints", subcategory, function, blueprints, platform, **kwargs)
