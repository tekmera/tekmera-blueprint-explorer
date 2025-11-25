"""Make.com router-specific diff analysis."""

from typing import Any, Dict, List

from . import RouterDifference


def analyze_make_com_router(
    old_router: Dict[str, Any], new_router: Dict[str, Any]
) -> List[RouterDifference]:
    """
    Analyze differences between Make.com routers.
    """
    differences = []

    # Basic implementation for Make.com routers
    if old_router != new_router:
        differences.append(
            RouterDifference(
                field_path="router",
                old_value="router_config",
                new_value="router_config_modified",
                change_type="modified",
                significance="important",
                description="Router configuration changed",
                routing_impact="changes_logic",
            )
        )

    return differences
