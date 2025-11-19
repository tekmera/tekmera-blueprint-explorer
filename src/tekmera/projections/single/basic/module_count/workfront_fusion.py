"""
Workfront Fusion module count extraction.
"""

from typing import Any, Dict, List

from ....meta.types import Platform, ProjectionResult, create_result


def _extract_modules_from_flow(flow: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Recursively extract all modules from a flow, including nested routes and error handlers.
    """
    modules = []

    for item in flow:
        if not isinstance(item, dict):
            continue

        # Add the current module
        modules.append(item)

        # Handle nested routes
        if "routes" in item and item["routes"]:
            for route in item["routes"]:
                if isinstance(route, dict) and "flow" in route and route["flow"]:
                    modules.extend(_extract_modules_from_flow(route["flow"]))

        # Handle error handlers
        if "onerror" in item and item["onerror"]:
            modules.extend(_extract_modules_from_flow(item["onerror"]))

    return modules


def module_count(blueprint: Dict[str, Any]) -> ProjectionResult[int]:
    """
    Count modules in Workfront Fusion blueprint including nested flows.
    Implements graceful degradation for missing/invalid flow data.
    """
    flow = blueprint.get("flow", [])

    # Graceful degradation: handle missing or invalid flow
    if not isinstance(flow, list):
        flow = []

    # Extract all modules recursively
    all_modules = _extract_modules_from_flow(flow)

    # Also check for orphaned modules
    orphans = []
    metadata = blueprint.get("metadata", {})
    if isinstance(metadata, dict):
        designer = metadata.get("designer", {})
        if isinstance(designer, dict):
            orphan_arrays = designer.get("orphans", [])
            if isinstance(orphan_arrays, list):
                for orphan_array in orphan_arrays:
                    if isinstance(orphan_array, list):
                        orphans.extend(orphan_array)

    total_count = len(all_modules) + len(orphans)

    return create_result(
        blueprint=blueprint,
        platform=Platform.WORKFRONT_FUSION,
        function_name="single.basic.module_count",
        data=total_count,
    )
