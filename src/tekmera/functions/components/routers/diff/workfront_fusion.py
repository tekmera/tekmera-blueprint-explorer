"""Workfront Fusion router-specific diff analysis."""

from typing import Any, Dict, List

from . import RouterDifference


def analyze_workfront_fusion_router(
    old_router: Dict[str, Any], new_router: Dict[str, Any]
) -> List[RouterDifference]:
    """
    Analyze differences between Workfront Fusion routers.

    Focuses on route paths, filters, and branching logic.
    """
    differences = []

    # Analyze route structure changes
    old_routes = old_router.get("routes", [])
    new_routes = new_router.get("routes", [])

    differences.extend(_analyze_route_structure(old_routes, new_routes))

    # Analyze router metadata
    old_meta = old_router.get("metadata", {})
    new_meta = new_router.get("metadata", {})
    differences.extend(_analyze_router_metadata(old_meta, new_meta))

    return differences


def _analyze_route_structure(old_routes: List, new_routes: List) -> List[RouterDifference]:
    """Analyze changes in router path structure."""
    differences = []

    old_count = len(old_routes) if old_routes else 0
    new_count = len(new_routes) if new_routes else 0

    if old_count != new_count:
        if new_count > old_count:
            routing_impact = "adds_path"
            significance = "important"
            description = f"Router paths increased from {old_count} to {new_count} - new execution branches added"
        else:
            routing_impact = "removes_path"
            significance = "critical"
            description = f"Router paths decreased from {old_count} to {new_count} - execution branches removed"

        differences.append(
            RouterDifference(
                field_path="routes",
                old_value=f"{old_count} routes",
                new_value=f"{new_count} routes",
                change_type="modified",
                significance=significance,
                description=description,
                routing_impact=routing_impact,
            )
        )

    # Analyze individual routes for filter changes
    max_routes = max(old_count, new_count)
    for i in range(min(5, max_routes)):  # Analyze first 5 routes in detail
        old_route = old_routes[i] if i < old_count else None
        new_route = new_routes[i] if i < new_count else None

        if old_route and new_route:
            differences.extend(_analyze_individual_route(old_route, new_route, i))
        elif old_route is None and new_route is not None:
            differences.append(
                RouterDifference(
                    field_path=f"routes.{i}",
                    old_value=None,
                    new_value="new_route",
                    change_type="added",
                    significance="important",
                    description=f"Route {i} added - new execution path",
                    routing_impact="adds_path",
                )
            )
        elif old_route is not None and new_route is None:
            differences.append(
                RouterDifference(
                    field_path=f"routes.{i}",
                    old_value="existing_route",
                    new_value=None,
                    change_type="removed",
                    significance="critical",
                    description=f"Route {i} removed - execution path eliminated",
                    routing_impact="removes_path",
                )
            )

    return differences


def _analyze_individual_route(
    old_route: Dict, new_route: Dict, route_index: int
) -> List[RouterDifference]:
    """Analyze changes within a specific router path."""
    differences = []

    # Analyze route filter changes (affects which data takes this path)
    old_filter = old_route.get("filter", {})
    new_filter = new_route.get("filter", {})

    if old_filter != new_filter:
        # Route filter changes affect branching logic
        differences.append(
            RouterDifference(
                field_path=f"routes.{route_index}.filter",
                old_value=_summarize_filter(old_filter),
                new_value=_summarize_filter(new_filter),
                change_type="modified",
                significance="important",
                description=f"Route {route_index} filter conditions changed - affects data branching",
                routing_impact="changes_logic",
            )
        )

    # Analyze flow structure within the route
    old_flow = old_route.get("flow", [])
    new_flow = new_route.get("flow", [])

    old_flow_count = len(old_flow) if old_flow else 0
    new_flow_count = len(new_flow) if new_flow else 0

    if old_flow_count != new_flow_count:
        differences.append(
            RouterDifference(
                field_path=f"routes.{route_index}.flow",
                old_value=f"{old_flow_count} modules",
                new_value=f"{new_flow_count} modules",
                change_type="modified",
                significance="minor",
                description=f"Route {route_index} flow: {old_flow_count} → {new_flow_count} modules",
                routing_impact="changes_logic",
            )
        )

    return differences


def _analyze_router_metadata(old_meta: Dict, new_meta: Dict) -> List[RouterDifference]:
    """Analyze router metadata changes."""
    differences = []

    # Router name changes
    old_designer = old_meta.get("designer", {})
    new_designer = new_meta.get("designer", {})

    old_name = old_designer.get("name", "")
    new_name = new_designer.get("name", "")

    if old_name != new_name:
        differences.append(
            RouterDifference(
                field_path="metadata.designer.name",
                old_value=old_name,
                new_value=new_name,
                change_type="modified",
                significance="cosmetic",
                description=f"Router name changed from '{old_name}' to '{new_name}'",
                routing_impact="cosmetic",
            )
        )

    return differences


def _summarize_filter(filter_config: Dict) -> str:
    """Create a summary of filter configuration for comparison display."""
    if not filter_config:
        return "no filter"

    name = filter_config.get("name", "")
    conditions = filter_config.get("conditions", [])
    condition_count = len(conditions) if conditions else 0

    if name and condition_count:
        return f"'{name}' ({condition_count} conditions)"
    elif name:
        return f"'{name}'"
    elif condition_count:
        return f"{condition_count} conditions"
    else:
        return "filter present"
