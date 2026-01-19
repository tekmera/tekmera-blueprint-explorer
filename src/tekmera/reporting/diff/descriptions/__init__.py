"""
Component addition description generators.

Provides detailed descriptions for newly added components in diff reports,
following the established Functions System pattern for platform abstraction.
"""

from typing import Any

from tekmera.functions.meta.types import Platform
from tekmera.functions.components.topology.types import TopologyNode

from .filters import generate_filter_addition_description
from .modules import generate_module_addition_description


def generate_component_addition_description(node: TopologyNode) -> str:
    """
    Generate detailed description for newly added component.

    Args:
        node: The topology node representing the added component

    Returns:
        Human-readable description of the component and its configuration
    """
    if node.is_filter:
        return generate_filter_addition_description(node)
    elif node.is_router:
        return _generate_router_description(node)
    elif node.is_error_handler:
        return _generate_error_handler_description(node)
    else:
        return _generate_module_description(node)


def _detect_platform(node: TopologyNode) -> Platform:
    """
    Detect platform from node characteristics.

    Uses same detection logic as the Functions System.
    """
    raw_data = getattr(node, "raw_data", {})

    if isinstance(raw_data, dict):
        module_type = raw_data.get("module", "")
        if isinstance(module_type, str):
            if "workfront" in module_type.lower():
                return Platform.WORKFRONT_FUSION
            elif any(
                prefix in module_type for prefix in ["builtin:", "google:", "slack:", "microsoft:"]
            ):
                return Platform.MAKE_COM

    # Default to Workfront Fusion if detection fails
    return Platform.WORKFRONT_FUSION


def _generate_router_description(node: TopologyNode) -> str:
    """Generate description for newly added router components."""
    # TODO: Implement router-specific description logic following registry pattern
    return "New router added to workflow"


def _generate_error_handler_description(node: TopologyNode) -> str:
    """Generate description for newly added error handler components."""
    # TODO: Implement error handler-specific description logic following registry pattern
    return "New error handler added to workflow"


def _generate_module_description(node: TopologyNode) -> str:
    """Generate description for newly added module components."""
    return generate_module_addition_description(node)
