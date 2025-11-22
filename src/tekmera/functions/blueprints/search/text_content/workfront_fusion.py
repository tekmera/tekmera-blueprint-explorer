"""Workfront Fusion blueprint text search implementation."""

from typing import Any, Dict, List

from ....components.error_handlers.content.text_content import (
    text_content as error_handler_text_content,
)
from ....components.filters.content.text_content import text_content as filter_text_content
from ....components.modules.content.text_content import text_content as module_text_content
from ....components.routers.content.text_content import text_content as router_text_content
from ....meta.types import Platform, ProjectionResult, create_result
from ....meta.utils.workfront_fusion.extract_components import extract_all_components


def text_content(blueprints: List[Dict[str, Any]], query: str, case_sensitive: bool = False) -> ProjectionResult:
    """
    Search for text content across all components in Workfront Fusion blueprints.

    This function demonstrates the full stack:
    1. Blueprint input
    2. Component extraction (typed components)
    3. Text content extraction from each component
    4. Search across all text content
    5. Structured result output
    """
    # Handle single blueprint
    if len(blueprints) == 1:
        result = _search_single_blueprint(blueprints[0], query, case_sensitive)
        return create_result(
            blueprint=blueprints[0],
            platform=Platform.WORKFRONT_FUSION,
            function_name="blueprints.search.text_content",
            data=result
        )

    # Handle multiple blueprints
    results = []
    for blueprint in blueprints:
        search_result = _search_single_blueprint(blueprint, query, case_sensitive)
        search_result["blueprint_name"] = blueprint.get("name", "Unnamed Blueprint")
        results.append(search_result)

    return create_result(
        blueprint={"name": f"Search across {len(blueprints)} blueprints"},
        platform=Platform.WORKFRONT_FUSION,
        function_name="blueprints.search.text_content",
        data=results
    )


def _search_single_blueprint(blueprint: Dict[str, Any], query: str, case_sensitive: bool) -> Dict[str, Any]:
    """Search within a single blueprint."""
    # Step 1: Extract all typed components
    all_components = extract_all_components(blueprint, include_orphans=True)

    # Step 2: Extract text content from each component type
    matches = []
    matches_by_type = {"modules": 0, "routers": 0, "filters": 0, "error_handlers": 0}

    # Search modules
    for module_component in all_components["modules"]:
        try:
            text_result = module_text_content(module_component, Platform.WORKFRONT_FUSION)
            text_content = text_result.data

            if _text_contains_query(text_content, query, case_sensitive):
                matches_by_type["modules"] += 1
                matches.append({
                    "component_type": "module",
                    "component_id": module_component.id,
                    "match_text": _extract_match_context(text_content, query, case_sensitive),
                    "context": module_component.extraction_context
                })
        except Exception:
            # Skip components that can't be processed
            continue

    # Search routers
    for router_component in all_components["routers"]:
        try:
            text_result = router_text_content(router_component, Platform.WORKFRONT_FUSION)
            text_content = text_result.data

            if _text_contains_query(text_content, query, case_sensitive):
                matches_by_type["routers"] += 1
                matches.append({
                    "component_type": "router",
                    "component_id": router_component.id,
                    "match_text": _extract_match_context(text_content, query, case_sensitive),
                    "context": router_component.extraction_context
                })
        except Exception:
            continue

    # Search filters
    for filter_component in all_components["filters"]:
        try:
            text_result = filter_text_content(filter_component, Platform.WORKFRONT_FUSION)
            text_content = text_result.data

            if _text_contains_query(text_content, query, case_sensitive):
                matches_by_type["filters"] += 1
                matches.append({
                    "component_type": "filter",
                    "component_id": filter_component.id,
                    "match_text": _extract_match_context(text_content, query, case_sensitive),
                    "context": filter_component.extraction_context
                })
        except Exception:
            continue

    # Search error handlers
    for error_handler_component in all_components["error_handlers"]:
        try:
            text_result = error_handler_text_content(error_handler_component, Platform.WORKFRONT_FUSION)
            text_content = text_result.data

            if _text_contains_query(text_content, query, case_sensitive):
                matches_by_type["error_handlers"] += 1
                matches.append({
                    "component_type": "error_handler",
                    "component_id": error_handler_component.id,
                    "match_text": _extract_match_context(text_content, query, case_sensitive),
                    "context": error_handler_component.extraction_context
                })
        except Exception:
            continue

    # Step 3: Return structured results
    total_matches = sum(matches_by_type.values())

    return {
        "query": query,
        "case_sensitive": case_sensitive,
        "total_matches": total_matches,
        "matches_by_type": matches_by_type,
        "component_counts": {
            "modules": len(all_components["modules"]),
            "routers": len(all_components["routers"]),
            "filters": len(all_components["filters"]),
            "error_handlers": len(all_components["error_handlers"])
        },
        "matches": matches
    }


def _text_contains_query(text: str, query: str, case_sensitive: bool) -> bool:
    """Check if text contains the query string."""
    if case_sensitive:
        return query in text
    else:
        return query.lower() in text.lower()


def _extract_match_context(text: str, query: str, case_sensitive: bool, context_chars: int = 100) -> str:
    """Extract context around the first match."""
    search_text = text if case_sensitive else text.lower()
    search_query = query if case_sensitive else query.lower()

    match_index = search_text.find(search_query)
    if match_index == -1:
        return text[:context_chars] + "..." if len(text) > context_chars else text

    start = max(0, match_index - context_chars // 2)
    end = min(len(text), match_index + len(query) + context_chars // 2)

    context = text[start:end]
    if start > 0:
        context = "..." + context
    if end < len(text):
        context = context + "..."

    return context
