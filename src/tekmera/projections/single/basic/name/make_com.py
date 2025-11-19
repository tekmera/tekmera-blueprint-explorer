"""
Make.com name extraction.
"""

from typing import Any, Dict

from ....meta.types import Platform, ProjectionResult, create_result


def name(blueprint: Dict[str, Any]) -> ProjectionResult[str]:
    """
    Extract scenario name from Make.com blueprint.
    Implements graceful degradation for missing/empty/null names.
    """
    scenario_name = blueprint.get("name")

    # Graceful degradation: handle missing, empty, or null names
    if not scenario_name:
        scenario_name = "Unnamed Scenario"

    return create_result(
        blueprint=blueprint,
        platform=Platform.MAKE_COM,
        function_name="single.basic.name",
        data=scenario_name,
        blueprint_name=scenario_name,
    )
