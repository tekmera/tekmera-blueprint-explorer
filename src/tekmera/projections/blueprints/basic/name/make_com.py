"""
Make.com name extraction.
"""

from typing import Any, Dict, List, Union

from ....meta.types import Platform, ProjectionResult, create_result


def name(blueprints: List[Dict[str, Any]]) -> ProjectionResult[Union[str, List[str]]]:
    """
    Extract scenario name(s) from Make.com blueprint(s).
    Implements graceful degradation for missing/empty/null names.
    """
    names = []

    for blueprint in blueprints:
        scenario_name = blueprint.get("name")

        # Graceful degradation: handle missing, empty, or null names
        if not scenario_name:
            scenario_name = "Unnamed Scenario"

        names.append(scenario_name)

    # Return single name if only one blueprint, otherwise return list
    data = names[0] if len(blueprints) == 1 else names

    return create_result(
        blueprint=blueprints[0],
        platform=Platform.MAKE_COM,
        function_name="blueprints.basic.name",
        data=data,
        blueprint_name=names[0],
    )
