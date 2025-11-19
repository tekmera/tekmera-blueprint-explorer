"""Component extraction for Workfront Fusion blueprints."""

from typing import Any, Dict, List

from ...types import Blueprint


def extract_all_components(
    blueprint: Blueprint, include_orphans: bool = True
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extract all components from Workfront Fusion blueprint, categorized by type.

    Returns:
        Dict with keys: 'modules', 'routers', 'filters', 'error_handlers'
    """
    components = {"modules": [], "routers": [], "filters": [], "error_handlers": []}

    top_level_flow = blueprint.get("flow", [])

    def extract_components_recursive(flow_items, parent_context="main"):
        """Recursively extract all component types from flow."""
        for item in flow_items:
            # Add context about where this component was found
            item_with_context = {**item, "_extraction_context": parent_context}

            # 1. Check if it's a module (has 'module' field)
            if "module" in item:
                components["modules"].append(item_with_context)

            # 2. Check if it's a router (has 'routes' field)
            if "routes" in item:
                router_info = {
                    "type": "router",
                    "routes_count": len(item["routes"]),
                    "item": item_with_context,
                    "_extraction_context": parent_context,
                }
                components["routers"].append(router_info)

                # Recursively process routes
                for route_idx, route in enumerate(item["routes"]):
                    route_flow = route.get("flow", [])
                    if route_flow:
                        extract_components_recursive(
                            route_flow, f"{parent_context}.route[{route_idx}]"
                        )

            # 3. Check if it has a filter
            if "filter" in item:
                filter_info = {
                    "type": "filter",
                    "filter_name": item["filter"].get("name", "Unnamed Filter"),
                    "conditions_count": len(item["filter"].get("conditions", [])),
                    "item": item_with_context,
                    "_extraction_context": parent_context,
                }
                components["filters"].append(filter_info)

            # 4. Check if it has error handlers
            if "onerror" in item:
                error_handler_info = {
                    "type": "error_handler",
                    "handlers_count": len(item["onerror"]),
                    "item": item_with_context,
                    "_extraction_context": parent_context,
                }
                components["error_handlers"].append(error_handler_info)

                # Recursively process error handlers
                extract_components_recursive(item["onerror"], f"{parent_context}.onerror")

    # Extract components from main execution flow
    extract_components_recursive(top_level_flow)

    # Optionally extract components from orphaned flows
    if include_orphans:
        orphans = blueprint.get("metadata", {}).get("designer", {}).get("orphans", [])
        for orphan_idx, orphan_group in enumerate(orphans):
            if isinstance(orphan_group, list):
                extract_components_recursive(orphan_group, f"orphan[{orphan_idx}]")

    return components


def extract_modules_only(
    blueprint: Blueprint, include_orphans: bool = True
) -> List[Dict[str, Any]]:
    """Extract only modules (backward compatibility with current extract_modules)."""
    components = extract_all_components(blueprint, include_orphans)
    return components["modules"]


def extract_routers(blueprint: Blueprint, include_orphans: bool = True) -> List[Dict[str, Any]]:
    """Extract only routers from blueprint."""
    components = extract_all_components(blueprint, include_orphans)
    return components["routers"]


def extract_filters(blueprint: Blueprint, include_orphans: bool = True) -> List[Dict[str, Any]]:
    """Extract only filters from blueprint."""
    components = extract_all_components(blueprint, include_orphans)
    return components["filters"]


def extract_error_handlers(
    blueprint: Blueprint, include_orphans: bool = True
) -> List[Dict[str, Any]]:
    """Extract only error handlers from blueprint."""
    components = extract_all_components(blueprint, include_orphans)
    return components["error_handlers"]
