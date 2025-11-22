"""Module extraction for Workfront Fusion blueprints."""

from typing import List

from ...types import Blueprint, Module


def extract_modules(blueprint: Blueprint, include_orphans: bool = True) -> List[Module]:
    """Extract all modules from Workfront Fusion blueprint."""
    all_modules = []
    top_level_flow = blueprint.get("flow", [])

    def extract_modules_recursive(modules_list):
        """Recursively extract modules from nested route structures and error handlers."""
        for module in modules_list:
            all_modules.append(module)

            # Check if this module has routes (nested flows)
            routes = module.get("routes", [])
            for route in routes:
                route_flow = route.get("flow", [])
                if route_flow:
                    extract_modules_recursive(route_flow)

            # Check if this module has error handlers (onerror flows)
            onerror = module.get("onerror", [])
            if onerror:
                extract_modules_recursive(onerror)

    # Extract modules from main execution flow
    extract_modules_recursive(top_level_flow)

    # Optionally extract modules from orphaned flows
    if include_orphans:
        orphans = blueprint.get("metadata", {}).get("designer", {}).get("orphans", [])
        for orphan_group in orphans:
            if isinstance(orphan_group, list):
                extract_modules_recursive(orphan_group)

    return all_modules
