"""Workfront Fusion blueprint text search implementation."""

from typing import Any, Dict, List

from ....components.filters.content.text_content import text_content as filter_text_content
from ....components.modules.content.text_content import text_content as module_text_content
from ....components.routers.content.text_content import text_content as router_text_content
from ....meta.types import Platform, ProjectionResult, create_result
from ....meta.utils.workfront_fusion.extract_components import extract_all_components


def text_content(
    blueprints: List[Dict[str, Any]],
    queries: List[str],
    case_sensitive: bool = False,
    regex: bool = False,
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
        result["blueprint_name"] = blueprints[0].get("name", "Unnamed Blueprint")
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
    matches_by_type = {"modules": 0, "routers": 0}

    # Search modules
    for module_component in all_components["modules"]:
        try:
            text_result = module_text_content(module_component, Platform.WORKFRONT_FUSION)

            # Use structured entries if available, fallback to text search
            if hasattr(text_result, "entries") and text_result.entries:
                field_matches = _find_matches_in_entries(
                    text_result.entries, queries, case_sensitive, regex
                )
                if field_matches:
                    matches_by_type["modules"] += 1
                    matches.append(
                        {
                            "component_type": "modules",
                            "component_id": module_component.id,
                            "context": module_component.extraction_context,
                            "matches": field_matches,
                            "literal_entries": text_result.entries,  # <<< ADD THIS
                        }
                    )
            else:
                # Fallback to text-based search for backward compatibility
                text_content = text_result.data
                matched_query = _text_contains_queries(text_content, queries, case_sensitive, regex)
                if matched_query:
                    matches_by_type["modules"] += 1
                    matches.append(
                        {
                            "component_type": "modules",
                            "component_id": module_component.id,
                            "context": module_component.extraction_context,
                            "matches": [
                                {
                                    "field_path": "component",
                                    "value": (
                                        text_content[:200] + "..."
                                        if len(text_content) > 200
                                        else text_content
                                    ),
                                    "matched_query": matched_query,
                                    "match_context": _extract_match_context(
                                        text_content, matched_query, case_sensitive, regex
                                    ),
                                    "start": -1,
                                    "end": -1,
                                }
                            ],
                            "literal_entries": text_result.entries or [],  # <<< ADD THIS
                        }
                    )

        except Exception:
            # Skip components that can't be processed
            continue

    # Note: Filters are excluded from search as they are sub-components of modules

    # Search routers (but exclude nested content that's already searched)
    for router_component in all_components["routers"]:
        try:
            text_result = router_text_content(router_component, Platform.WORKFRONT_FUSION)

            # Use structured entries if available, fallback to text search
            if hasattr(text_result, "entries") and text_result.entries:
                # Filter out entries that come from nested flows to avoid duplicates
                router_only_entries = [
                    (path, value)
                    for path, value in text_result.entries
                    if not _is_nested_flow_content(path)
                ]
                field_matches = _find_matches_in_entries(
                    router_only_entries, queries, case_sensitive, regex
                )
                if field_matches:
                    matches_by_type["routers"] += 1
                    matches.append(
                        {
                            "component_type": "routers",
                            "component_id": router_component.id,
                            "context": router_component.extraction_context,
                            "matches": field_matches,
                            "literal_entries": router_only_entries,
                        }
                    )
            else:
                # Fallback to text-based search for backward compatibility
                text_content = text_result.data
                # Filter out nested flow content from text search too
                filtered_text = _filter_router_text_content(text_content)
                matched_query = _text_contains_queries(
                    filtered_text, queries, case_sensitive, regex
                )
                if matched_query:
                    matches_by_type["routers"] += 1
                    matches.append(
                        {
                            "component_type": "routers",
                            "component_id": router_component.id,
                            "context": router_component.extraction_context,
                            "matches": [
                                {
                                    "field_path": "component",
                                    "value": (
                                        filtered_text[:200] + "..."
                                        if len(filtered_text) > 200
                                        else filtered_text
                                    ),
                                    "matched_query": matched_query,
                                    "match_context": _extract_match_context(
                                        filtered_text, matched_query, case_sensitive, regex
                                    ),
                                    "start": -1,
                                    "end": -1,
                                }
                            ],
                            "literal_entries": [],
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
            "filters": len(all_components["filters"]),
            "routers": len(all_components["routers"]),
        },
        "matches": matches,
    }


def _find_matches_in_entries(
    entries: List[tuple], queries: List[str], case_sensitive: bool, regex: bool
) -> List[Dict[str, Any]]:
    """
    Find matches in structured field entries with precise position data.

    Returns list of match objects with field_path, value, matched_query,
    match_context, start, and end positions.
    """
    results = []
    for field_path, value in entries:
        matched_query = _text_contains_queries(value, queries, case_sensitive, regex)
        if matched_query:
            # Find match position in the field value
            start, end = _find_match_position(value, matched_query, case_sensitive, regex)
            match_context = value[start:end] if start != -1 else matched_query

            results.append(
                {
                    "field_path": field_path,
                    "value": value,
                    "matched_query": matched_query,
                    "match_context": match_context,
                    "start": start,
                    "end": end,
                }
            )
    return results


def _find_match_position(
    text: str, query: str, case_sensitive: bool, regex: bool
) -> tuple[int, int]:
    """
    Find start and end positions of the match within the text.

    Returns (start, end) tuple. Returns (-1, -1) if no match found.
    """
    import re

    if regex:
        try:
            pattern = query if case_sensitive else f"(?i){query}"
            match = re.search(pattern, text)
            return (match.start(), match.end()) if match else (-1, -1)
        except re.error:
            # Fall back to literal search if regex fails
            pass

    # Literal string search
    search_text = text if case_sensitive else text.lower()
    search_query = query if case_sensitive else query.lower()
    start = search_text.find(search_query)
    return (start, start + len(query)) if start != -1 else (-1, -1)


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


def _is_nested_flow_content(path: str) -> bool:
    """
    Check if a field path refers to content from nested flows within a router.

    Router-specific fields we want to keep:
    - id, module (router type)
    - filter.* (router-level filters)
    - metadata.designer.* (router naming)

    Fields to exclude (nested content):
    - routes[*].flow[*].* (content from modules within routes)
    """
    # Keep router-level fields
    if not any(x in path for x in ["routes", "flow"]):
        return False

    # Exclude nested flow content
    if "routes[" in path and "flow[" in path:
        return True

    return False


def _filter_router_text_content(text_content: str) -> str:
    """
    Filter out nested flow content from router text content.
    This is a simple implementation that removes lines containing route flow paths.
    """
    lines = text_content.split("\n")
    filtered_lines = []

    for line in lines:
        # Skip lines that contain nested flow references
        if "routes[" in line and "flow[" in line:
            continue
        filtered_lines.append(line)

    return "\n".join(filtered_lines)
