"""Component extraction for Make.com blueprints."""

from typing import Dict, List

from ...types import (
    Blueprint,
    Component,
    ErrorHandlerComponent,
    FilterComponent,
    ModuleComponent,
    Platform,
    RouterComponent,
)


def extract_all_components(
    blueprint: Blueprint, include_orphans: bool = True
) -> Dict[str, List[Component]]:
    """
    Extract all components from Make.com blueprint, categorized by type.

    Make.com uses flow-based structure like Workfront Fusion, with support for
    routers (BasicRouter), filters, error handlers, and regular modules.

    Returns:
        Dict with keys: 'modules', 'routers', 'filters', 'error_handlers'
    """
    components = {"modules": [], "routers": [], "filters": [], "error_handlers": []}

    # Make.com uses flow array (like Fusion) not scenario.modules
    top_level_flow = blueprint.get("flow", [])
    
    def extract_components_recursive(flow_items, parent_context="main"):
        """Recursively extract all component types from flow."""
        for item in flow_items:
            # Add context about where this component was found
            item_with_context = {**item, "_extraction_context": parent_context}

            # 1. Check if it's a module (has 'module' field)
            if "module" in item:
                module_component = ModuleComponent(
                    id=str(item.get("id", "unknown")),
                    platform=Platform.MAKE_COM,
                    extraction_context=parent_context,
                    raw_data=item_with_context,
                    module_type=item.get("module", "unknown"),
                )
                components["modules"].append(module_component)

            # 2. Check if it's a router (builtin:BasicRouter with routes)
            if item.get("module") == "builtin:BasicRouter" and "routes" in item:
                router_component = RouterComponent(
                    id=str(item.get("id", "unknown")),
                    platform=Platform.MAKE_COM,
                    extraction_context=parent_context,
                    raw_data=item_with_context,
                    routes_count=len(item["routes"]),
                    has_filter="filter" in item,
                )
                components["routers"].append(router_component)

                # Recursively process routes
                for route_idx, route in enumerate(item["routes"]):
                    route_flow = route.get("flow", [])
                    if route_flow:
                        extract_components_recursive(
                            route_flow, f"{parent_context}.route[{route_idx}]"
                        )

            # 3. Check if it has a filter (Make.com filters are on individual modules)
            if "filter" in item:
                filter_component = FilterComponent(
                    id=str(item.get("id", "unknown")),
                    platform=Platform.MAKE_COM,
                    extraction_context=parent_context,
                    raw_data=item_with_context,
                    filter_name=item["filter"].get("name", "Unnamed Filter"),
                    conditions_count=len(item["filter"].get("conditions", [])),
                )
                components["filters"].append(filter_component)

            # 4. Check if it has error handlers
            if "onerror" in item:
                handler_types = [
                    h.get("module", "unknown") for h in item["onerror"] if isinstance(h, dict)
                ]
                error_handler_component = ErrorHandlerComponent(
                    id=str(item.get("id", "unknown")),
                    platform=Platform.MAKE_COM,
                    extraction_context=parent_context,
                    raw_data=item_with_context,
                    handlers_count=len(item["onerror"]),
                    handler_types=handler_types,
                )
                components["error_handlers"].append(error_handler_component)

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
) -> List[ModuleComponent]:
    """Extract only modules (backward compatibility)."""
    components = extract_all_components(blueprint, include_orphans)
    return components["modules"]


def extract_routers(blueprint: Blueprint, include_orphans: bool = True) -> List[RouterComponent]:
    """Extract only routers from Make.com blueprint."""
    components = extract_all_components(blueprint, include_orphans)
    return components["routers"]


def extract_filters(blueprint: Blueprint, include_orphans: bool = True) -> List[FilterComponent]:
    """Extract only filters from Make.com blueprint."""
    components = extract_all_components(blueprint, include_orphans)
    return components["filters"]


def extract_error_handlers(
    blueprint: Blueprint, include_orphans: bool = True
) -> List[ErrorHandlerComponent]:
    """Extract only error handlers from Make.com blueprint."""
    components = extract_all_components(blueprint, include_orphans)
    return components["error_handlers"]
