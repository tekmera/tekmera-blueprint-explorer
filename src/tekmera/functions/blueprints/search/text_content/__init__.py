"""
Blueprint text content search function.

## Function-Specific Contract
*Inherits baseline projection function contract*

### Purpose
Searches for text content across all components in blueprint(s), providing
detailed results showing where matches were found and in which component types.

### Input
Accepts Union[Dict, List[Dict]] to handle both single and multiple blueprints.

### Platform-Specific Input Structures

#### Workfront Fusion & Make.com
Standard blueprint JSON structure. Search is performed across all component types
extracted from the blueprint using the component extraction utilities.

### Function-Specific Analysis
**Search Process**:
1. Extract all components (modules, routers, filters, error_handlers)
2. Extract text content from each component
3. Search text content for query string
4. Return structured results with match locations

### Output Data Type
- Single blueprint: `ProjectionResult[SearchResults]`
- Multiple blueprints: `ProjectionResult[List[SearchResults]]`

### SearchResults Structure
```python
{
    "query": "search_term",
    "case_sensitive": False,
    "total_matches": 5,
    "matches_by_type": {
        "modules": 3,
        "routers": 1,
        "filters": 1,
        "error_handlers": 0
    },
    "matches": [
        {
            "component_type": "module",
            "component_id": "22",
            "match_text": "...containing search_term...",
            "context": "main"
        }
    ]
}
```
"""

from typing import Any, Dict, List, Union

from ....meta.platform_detection import detect_platform
from ....meta.types import BlueprintInput, Platform, ProjectionResult, normalize_blueprint_input
from . import make_com, workfront_fusion

IMPLEMENTATIONS = {
    Platform.WORKFRONT_FUSION: workfront_fusion.text_content,
    Platform.MAKE_COM: make_com.text_content,
}


def text_content(
    blueprints: BlueprintInput, queries: List[str], case_sensitive: bool = False, regex: bool = False, platform: Platform = None
) -> ProjectionResult[Union[Dict[str, Any], List[Dict[str, Any]]]]:
    """
    Search for text content across all components in blueprint(s).

    Args:
        blueprints: Single blueprint or list of blueprints
        queries: List of text strings to search for (OR logic)
        case_sensitive: Whether search should be case sensitive
        regex: Whether to treat queries as regex patterns
        platform: Optional platform override

    Returns:
        ProjectionResult containing search results
    """
    normalized_blueprints = normalize_blueprint_input(blueprints)

    if platform is None:
        platform = detect_platform(normalized_blueprints[0])

    if platform in IMPLEMENTATIONS:
        return IMPLEMENTATIONS[platform](normalized_blueprints, queries, case_sensitive, regex)

    raise ValueError(f"Platform {platform.value} not supported for text search")
