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


def text_content(
    blueprints: List[Dict[str, Any]], queries: List[str], case_sensitive: bool = False, regex: bool = False
) -> ProjectionResult:
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
        result = _search_single_blueprint(blueprints[0], queries, case_sensitive, regex)
        return create_result(
            blueprint=blueprints[0],
            platform=Platform.WORKFRONT_FUSION,
            function_name="blueprints.search.text_content",
            data=result,
        )

    # Handle multiple blueprints
    results = []
    for blueprint in blueprints:
        search_result = _search_single_blueprint(blueprint, queries, case_sensitive, regex)
        search_result["blueprint_name"] = blueprint.get("name", "Unnamed Blueprint")
        results.append(search_result)

    return create_result(
        blueprint={"name": f"Search across {len(blueprints)} blueprints"},
        platform=Platform.WORKFRONT_FUSION,
        function_name="blueprints.search.text_content",
        data=results,
    )


def _search_single_blueprint(
    blueprint: Dict[str, Any], queries: List[str], case_sensitive: bool, regex: bool
) -> Dict[str, Any]:
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

            matched_query = _text_contains_queries(text_content, queries, case_sensitive, regex)
            if matched_query:
                matches_by_type["modules"] += 1
                matches.append(
                    {
                        "component_type": "modules",
                        "component_id": module_component.id,
                        "match_text": _extract_match_context(text_content, matched_query, case_sensitive, regex),
                        "context": module_component.extraction_context,
                        "matched_query": matched_query,
                    }
                )
        except Exception:
            # Skip components that can't be processed
            continue

    # Search routers
    for router_component in all_components["routers"]:
        try:
            text_result = router_text_content(router_component, Platform.WORKFRONT_FUSION)
            text_content = text_result.data

            matched_query = _text_contains_queries(text_content, queries, case_sensitive, regex)
            if matched_query:
                matches_by_type["routers"] += 1
                matches.append(
                    {
                        "component_type": "routers",
                        "component_id": router_component.id,
                        "match_text": _extract_match_context(text_content, matched_query, case_sensitive, regex),
                        "context": router_component.extraction_context,
                        "matched_query": matched_query,
                    }
                )
        except Exception:
            continue

    # Search filters
    for filter_component in all_components["filters"]:
        try:
            text_result = filter_text_content(filter_component, Platform.WORKFRONT_FUSION)
            text_content = text_result.data

            matched_query = _text_contains_queries(text_content, queries, case_sensitive, regex)
            if matched_query:
                matches_by_type["filters"] += 1
                matches.append(
                    {
                        "component_type": "filters",
                        "component_id": filter_component.id,
                        "match_text": _extract_match_context(text_content, matched_query, case_sensitive, regex),
                        "context": filter_component.extraction_context,
                        "matched_query": matched_query,
                    }
                )
        except Exception:
            continue

    # Search error handlers
    for error_handler_component in all_components["error_handlers"]:
        try:
            text_result = error_handler_text_content(
                error_handler_component, Platform.WORKFRONT_FUSION
            )
            text_content = text_result.data

            matched_query = _text_contains_queries(text_content, queries, case_sensitive, regex)
            if matched_query:
                matches_by_type["error_handlers"] += 1
                matches.append(
                    {
                        "component_type": "error_handlers",
                        "component_id": error_handler_component.id,
                        "match_text": _extract_match_context(text_content, matched_query, case_sensitive, regex),
                        "context": error_handler_component.extraction_context,
                        "matched_query": matched_query,
                    }
                )
        except Exception:
            continue

    # Step 3: Return structured results
    total_matches = sum(matches_by_type.values())

    return {
        "queries": queries,
        "case_sensitive": case_sensitive,
        "regex": regex,
        "total_matches": total_matches,
        "matches_by_type": matches_by_type,
        "component_counts": {
            "modules": len(all_components["modules"]),
            "routers": len(all_components["routers"]),
            "filters": len(all_components["filters"]),
            "error_handlers": len(all_components["error_handlers"]),
        },
        "matches": matches,
    }


def _text_contains_queries(text: str, queries: List[str], case_sensitive: bool, regex: bool) -> str:
    """
    Check if text contains any of the query strings (OR logic).
    
    Returns the first matching query, or None if no match.
    """
    import re
    
    for query in queries:
        if regex:
            try:
                pattern = query if case_sensitive else f"(?i){query}"
                if re.search(pattern, text):
                    return query
            except re.error:
                # If regex is invalid, fall back to literal search
                pass
        
        # Literal string search
        if case_sensitive:
            if query in text:
                return query
        else:
            if query.lower() in text.lower():
                return query
    
    return None


def _extract_match_context(
    text: str, query: str, case_sensitive: bool, regex: bool, context_chars: int = 100
) -> str:
    """Extract context around the first match."""
    import re
    
    if regex:
        try:
            pattern = query if case_sensitive else f"(?i){query}"
            match = re.search(pattern, text)
            if match:
                match_index = match.start()
            else:
                return text[:context_chars] + "..." if len(text) > context_chars else text
        except re.error:
            # Fall back to literal search if regex fails
            search_text = text if case_sensitive else text.lower()
            search_query = query if case_sensitive else query.lower()
            match_index = search_text.find(search_query)
    else:
        # Literal search
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
