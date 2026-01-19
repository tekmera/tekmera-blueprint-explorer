"""
Table formatter for CLI output.
"""

import json
from typing import Dict, List, Any, Callable


def format_result(result, format_type="table"):
    """Format projection result for CLI output."""

    if format_type == "json":
        # JSON output for scripting
        output = {
            "blueprint_id": result.blueprint_id,
            "blueprint_name": result.blueprint_name,
            "platform": result.platform.value,
            "data": result.data,
            "metadata": {
                "function": result.metadata.function,
                "version": result.metadata.version,
                "computed_at": result.metadata.computed_at,
                "input_hash": result.metadata.input_hash,
            },
        }
        print(json.dumps(output, indent=2))

    elif format_type == "html":
        # HTML output for function results
        function_name = result.metadata.function
        if function_name in HTML_FORMATTERS:
            # Generate HTML content
            html_content = HTML_FORMATTERS[function_name](result)

            # Create output file
            from pathlib import Path
            from datetime import datetime
            import platform
            import subprocess
            import os

            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)

            # Create filename based on function type
            if function_name == "blueprints.search.text_content":
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"search_{timestamp}.html"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"result_{timestamp}.html"

            output_path = reports_dir / filename

            # Write HTML file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            print(f"HTML results generated: {output_path}")

            # Auto-open the file
            try:
                if platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", str(output_path)], check=True)
                elif platform.system() == "Windows":  # Windows
                    os.startfile(str(output_path))
                else:  # Linux and others
                    subprocess.run(["xdg-open", str(output_path)], check=True)
            except (subprocess.CalledProcessError, FileNotFoundError, AttributeError):
                # If opening fails, just continue silently
                pass
        else:
            # Fallback to table format for unsupported functions
            print("HTML format not supported for this function, showing table format:")
            _format_as_table(result)

    else:
        # Table output for interactive use
        _format_as_table(result)


def _format_as_table(result):
    """Format result as table output."""
    print(f"Blueprint: {result.blueprint_name}")
    print(f"Platform:  {result.platform.value}")
    print(f"Function:  {result.metadata.function}")

    # Use function-specific formatter if available
    function_name = result.metadata.function
    if function_name in TABLE_FORMATTERS:
        TABLE_FORMATTERS[function_name](result)
    else:
        _default_table_format(result)

    print(f"Hash:      {result.metadata.input_hash}")


def _default_table_format(result):
    """Default table formatting for unrecognized function types."""
    if isinstance(result.data, list):
        print(f"Results:   ({len(result.data)} items)")
        for i, item in enumerate(result.data, 1):
            print(f"  {i:2d}. {item}")
    else:
        print(f"Result:    {result.data}")


def _format_search_table(result):
    """Format search results as a clean table grouped by blueprint then component types."""
    data = result.data
    search_results = data if isinstance(data, list) else [data]

    # Extract search info
    queries = search_results[0].get("queries", []) if search_results else []
    query_str = ", ".join(f'"{q}"' for q in queries)
    regex_str = " (regex)" if search_results and search_results[0].get("regex") else ""

    # Calculate totals
    total_blueprints = len(search_results)
    blueprints_with_matches = sum(1 for r in search_results if r.get("total_matches", 0) > 0)
    total_matches = sum(r.get("total_matches", 0) for r in search_results)

    print(f"")
    print(f"Search Query:  {query_str}{regex_str}")
    print(
        f"Results:       {total_matches} matches in {blueprints_with_matches}/{total_blueprints} blueprints"
    )

    if total_matches == 0:
        print("No matches found.")
        return

    # For single blueprint, group by components. For multiple, group by blueprint then components.
    if len(search_results) == 1:
        _format_single_blueprint_search(search_results[0])
    else:
        _format_multiple_blueprint_search(search_results)


def _format_single_blueprint_search(search_result):
    """Format search results for a single blueprint, grouped by component type."""
    matches_by_type = search_result.get("matches_by_type", {})
    all_matches = search_result.get("matches", [])

    # Group matches by component type (now consistent - everything is plural)
    component_groups = {}
    for comp_type in matches_by_type.keys():
        component_groups[comp_type] = []

    for match in all_matches:
        component_type = match.get("component_type", "unknown")
        if component_type in component_groups:
            component_groups[component_type].append(match)

    # Display each component type
    for component_type in sorted(matches_by_type.keys()):
        matches = component_groups[component_type]
        comp_display = component_type.replace("_", " ").title()
        print(f"")
        print(f"=== {comp_display} ({len(matches)} matches) ===")

        if not matches:
            print("No matches found")
            continue

        print(f"{'ID':<6} {'Context':<25} {'Match'}")
        print(f"{'-'*6} {'-'*25} {'-'*50}")

        for match in matches:
            component_id = match.get("component_id", "?")
            context = match.get("context", "")
            context_display = context[:22] + "..." if len(context) > 25 else context

            # Handle new match structure with field-level matches
            field_matches = match.get("matches", [])
            if field_matches:
                # Show first field match with count if multiple
                first_match = field_matches[0]
                field_path = first_match.get("field_path", "")
                value = first_match.get("value", "")
                query = first_match.get("matched_query", "")

                # Trim long field values for display
                if value and len(value) > 100:
                    # Find match position and extract context
                    start = first_match.get("start", -1)
                    end = first_match.get("end", -1)
                    trimmed_value = _trim_value_for_table(
                        value, query, start, end, context_chars=40
                    )
                    match_context = trimmed_value
                else:
                    match_context = first_match.get("match_context", value[:50])

                if len(field_matches) > 1:
                    match_display = (
                        f"{match_context} (+{len(field_matches)-1} more in {field_path})"
                    )
                else:
                    match_display = f"{match_context} in {field_path}"

                # Truncate if too long
                match_display = (
                    match_display[:47] + "..." if len(match_display) > 50 else match_display
                )
            else:
                # Fallback for old format (backward compatibility)
                match_text = match.get("match_text", "").replace("\n", " ").strip()
                match_display = match_text[:47] + "..." if len(match_text) > 50 else match_text

            print(f"{component_id:<6} {context_display:<25} {match_display}")


def _format_multiple_blueprint_search(search_results):
    """Format search results for multiple blueprints, grouped by blueprint then component type."""
    for search_result in search_results:
        blueprint_name = search_result.get("blueprint_name", "Unknown Blueprint")
        total_matches = search_result.get("total_matches", 0)
        matches_by_type = search_result.get("matches_by_type", {})
        all_matches = search_result.get("matches", [])

        print(f"")
        print(f"{'='*80}")
        print(f"Blueprint: {blueprint_name} ({total_matches} matches)")
        print(f"{'='*80}")

        if total_matches == 0:
            print("No matches found in this blueprint")
            continue

        # Group matches by component type
        component_groups = {}
        for comp_type in matches_by_type.keys():
            component_groups[comp_type] = []

        for match in all_matches:
            component_type = match.get("component_type", "unknown")
            if component_type in component_groups:
                component_groups[component_type].append(match)

        # Display each component type
        for component_type in sorted(matches_by_type.keys()):
            matches = component_groups[component_type]
            comp_display = component_type.replace("_", " ").title() + "s"
            print(f"")
            print(f"--- {comp_display} ({len(matches)} matches) ---")

            if not matches:
                print("No matches found")
                continue

            print(f"{'ID':<6} {'Context':<25} {'Match'}")
            print(f"{'-'*6} {'-'*25} {'-'*50}")

            for match in matches:
                component_id = match.get("component_id", "?")
                context = match.get("context", "")
                context_display = context[:22] + "..." if len(context) > 25 else context

                # Handle new match structure with field-level matches
                field_matches = match.get("matches", [])
                if field_matches:
                    # Show first field match with count if multiple
                    first_match = field_matches[0]
                    field_path = first_match.get("field_path", "")
                    value = first_match.get("value", "")
                    query = first_match.get("matched_query", "")

                    # Trim long field values for display
                    if value and len(value) > 100:
                        # Find match position and extract context
                        start = first_match.get("start", -1)
                        end = first_match.get("end", -1)
                        trimmed_value = _trim_value_for_table(
                            value, query, start, end, context_chars=40
                        )
                        match_context = trimmed_value
                    else:
                        match_context = first_match.get("match_context", value[:50])

                    if len(field_matches) > 1:
                        match_display = (
                            f"{match_context} (+{len(field_matches)-1} more in {field_path})"
                        )
                    else:
                        match_display = f"{match_context} in {field_path}"

                    # Truncate if too long
                    match_display = (
                        match_display[:47] + "..." if len(match_display) > 50 else match_display
                    )
                else:
                    # Fallback for old format (backward compatibility)
                    match_text = match.get("match_text", "").replace("\n", " ").strip()
                    match_display = match_text[:47] + "..." if len(match_text) > 50 else match_text

                print(f"{component_id:<6} {context_display:<25} {match_display}")


def _trim_value_for_table(
    text: str, query: str, start: int, end: int, context_chars: int = 40
) -> str:
    """
    Trim long field values for table display with context around the match.

    Args:
        text: Full field value
        query: Search query
        start: Match start position (-1 if not available)
        end: Match end position (-1 if not available)
        context_chars: Characters to show around the match (shorter for table)

    Returns:
        Trimmed text with context around the match
    """
    if not text or len(text) <= context_chars * 2:
        return text

    # Use provided positions if available, otherwise find the match
    if start == -1 or end == -1:
        match_pos = text.lower().find(query.lower())
        if match_pos == -1:
            # No match found, return beginning of text
            return text[:context_chars] + "..."
        start = match_pos
        end = match_pos + len(query)

    # Calculate context window around the match (shorter for table display)
    match_center = (start + end) // 2
    window_start = max(0, match_center - context_chars // 2)
    window_end = min(len(text), match_center + context_chars // 2)

    # Extend window if we have room
    if window_end - window_start < context_chars:
        if window_start == 0:
            window_end = min(len(text), window_start + context_chars)
        elif window_end == len(text):
            window_start = max(0, window_end - context_chars)

    # Extract the context window
    trimmed = text[window_start:window_end]

    # Add ellipsis indicators
    if window_start > 0:
        trimmed = "..." + trimmed
    if window_end < len(text):
        trimmed = trimmed + "..."

    return trimmed


# Function-specific formatter registry for ProjectionResult objects
TABLE_FORMATTERS: Dict[str, Callable] = {
    "blueprints.search.text_content": _format_search_table,
    # Add more function formatters here:
    # "blueprints.basic.module_count": _format_module_count_table,
    # "blueprints.basic.name": _format_name_table,
}

# HTML formatter registry for ProjectionResult objects
from .html_search import format_search_html

HTML_FORMATTERS: Dict[str, Callable] = {
    "blueprints.search.text_content": format_search_html,
    # Add more HTML formatters here:
    # "blueprints.basic.module_count": format_module_count_html,
}


def format_error(message: str, format_type="table"):
    """Format error message."""
    if format_type == "json":
        print(json.dumps({"error": message}))
    else:
        print(f"Error: {message}")
