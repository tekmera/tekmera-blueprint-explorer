"""
Make.com module counting.
"""

from typing import Any, Dict, List, Union

from ....meta.types import Platform, ProjectionResult, create_result
from ....meta.utils import extract_modules


def module_count(blueprints: List[Dict[str, Any]]) -> ProjectionResult[Union[int, List[int]]]:
    """
    Count total modules in Make.com blueprint(s).
    Uses centralized module extraction utility.
    """
    counts = []

    for blueprint in blueprints:
        modules = extract_modules(blueprint, Platform.MAKE_COM, include_orphans=True)
        counts.append(len(modules))

    # Return single count if only one blueprint, otherwise return list
    data = counts[0] if len(blueprints) == 1 else counts

    return create_result(
        blueprint=blueprints[0],
        platform=Platform.MAKE_COM,
        function_name="blueprints.basic.module_count",
        data=data,
    )
