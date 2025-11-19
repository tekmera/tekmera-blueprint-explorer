"""Component extraction for Make.com blueprints."""

from typing import Any, Dict, List

from ...types import Blueprint


def extract_all_components(
    blueprint: Blueprint, include_orphans: bool = True
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extract all components from Make.com blueprint, categorized by type.

    Note: Make.com structure is simpler than Workfront Fusion.
    Most components are modules in the scenario.modules array.

    Returns:
        Dict with keys: 'modules', 'routers', 'filters', 'error_handlers'
    """
    components = {"modules": [], "routers": [], "filters": [], "error_handlers": []}

    # Make.com structure: scenario.modules contains the flow
    scenario = blueprint.get("scenario", {})
    modules = scenario.get("modules", [])

    for module in modules:
        # Add context
        module_with_context = {**module, "_extraction_context": "scenario.modules"}

        # For now, treat all as modules - Make.com structure needs more investigation
        # TODO: Investigate Make.com routing/filtering patterns when we have more examples
        if "module" in module:
            components["modules"].append(module_with_context)

        # Check for any routing or filtering patterns specific to Make.com
        # (This will need to be filled in based on actual Make.com blueprint analysis)

    return components


def extract_modules_only(
    blueprint: Blueprint, include_orphans: bool = True
) -> List[Dict[str, Any]]:
    """Extract only modules (backward compatibility)."""
    components = extract_all_components(blueprint, include_orphans)
    return components["modules"]


def extract_routers(blueprint: Blueprint, include_orphans: bool = True) -> List[Dict[str, Any]]:
    """Extract only routers from Make.com blueprint."""
    components = extract_all_components(blueprint, include_orphans)
    return components["routers"]


def extract_filters(blueprint: Blueprint, include_orphans: bool = True) -> List[Dict[str, Any]]:
    """Extract only filters from Make.com blueprint."""
    components = extract_all_components(blueprint, include_orphans)
    return components["filters"]


def extract_error_handlers(
    blueprint: Blueprint, include_orphans: bool = True
) -> List[Dict[str, Any]]:
    """Extract only error handlers from Make.com blueprint."""
    components = extract_all_components(blueprint, include_orphans)
    return components["error_handlers"]
