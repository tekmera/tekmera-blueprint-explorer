"""
HTML formatter for search results (refactored, maintainable version).
"""

import html
import re
from pathlib import Path
from typing import Any, Dict, List

from tekmera.functions.meta.types import ProjectionResult

# ---------------------------------------------
# Utility Helpers
# ---------------------------------------------


def _sanitize_id(text: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9]+", "-", text)
    safe = re.sub(r"-+", "-", safe).strip("-")
    return safe.lower()


def _escape(text: str) -> str:
    return html.escape(text) if text else ""


def _format_datetime(dt) -> str:
    try:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(dt)


def _component_display_name(comp_type: str) -> str:
    mapping = {
        "error_handlers": "Error Handlers",
        "filters": "Filters",
        "modules": "Modules",
        "routers": "Routers",
    }
    return mapping.get(comp_type, comp_type.replace("_", " ").title())


# ---------------------------------------------
# Public Entry Point
# ---------------------------------------------


def format_search_html(result: ProjectionResult) -> str:
    return _generate_html(result)


# ---------------------------------------------
# HTML Generator
# ---------------------------------------------


def _generate_html(result: ProjectionResult) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tekmera Search Results</title>
    {_load_css()}
</head>
<body>
    <div class="page-container">
        {_generate_sidebar(result)}
        <main class="main-content">
            <div class="container">
                <header>
                    <h1>Search Results</h1>
                </header>
                {_generate_overview_section(result)}
                {_generate_blueprint_section(result)}
                {_generate_results_section(result)}
            </div>
        </main>
    </div>
</body>
</html>"""


# ---------------------------------------------
# CSS Loader
# ---------------------------------------------


def _load_css() -> str:
    try:
        css_path = Path(__file__).parent / "styles.css"
        css = css_path.read_text(encoding="utf-8")
        return f"<style>\n{css}\n</style>"
    except FileNotFoundError:
        return "<style>body{font-family:sans-serif}</style>"


# ---------------------------------------------
# Sidebar
# ---------------------------------------------


def _generate_sidebar(result: ProjectionResult) -> str:
    search_results = result.data if isinstance(result.data, list) else [result.data]

    total_blueprints = len(search_results)
    blueprints_with_matches = sum(1 for r in search_results if r.get("total_matches", 0) > 0)
    total_matches = sum(r.get("total_matches", 0) for r in search_results)

    # Only include blueprints with matches in sidebar links
    links = []
    for r in search_results:
        if r.get("total_matches", 0) > 0:  # Only show blueprints with matches
            name = r.get("blueprint_name", "Unnamed Blueprint")
            anchor = _sanitize_id(name)
            links.append(f'<a href="#blueprint-{anchor}">{_escape(name)}</a>')

    return f"""
<div class="sidebar">
    <h3>Navigation</h3>
    <ul>
        <li><a href="#overview">Search Overview</a></li>
        <li><a href="#blueprints">Blueprint Information</a></li>
        <li>
            <a href="#results">Detailed Results</a>
            <div class="subsection">{'<br>'.join(links)}</div>
        </li>
    </ul>
    <div style="margin-top:20px;">
        <div class="info-item">Total Blueprints: {total_blueprints}</div>
        <div class="info-item">With Matches: {blueprints_with_matches}</div>
        <div class="info-item">Total Matches: {total_matches}</div>
        <div class="info-item">Platform: {result.platform.value.replace('_', ' ').title()}</div>
    </div>
</div>
"""


# ---------------------------------------------
# Overview Section
# ---------------------------------------------


def _generate_overview_section(result: ProjectionResult) -> str:
    search_results = result.data if isinstance(result.data, list) else [result.data]
    if not search_results:
        return """
<section id="overview">
    <h2>Search Overview</h2>
    <div class="section-card">No search results available</div>
</section>"""

    r0 = search_results[0]
    query_str = ", ".join(f'"{q}"' for q in r0.get("queries", []))

    total_blueprints = len(search_results)
    blueprints_with_matches = sum(1 for r in search_results if r.get("total_matches", 0) > 0)
    total_matches = sum(r.get("total_matches", 0) for r in search_results)
    total_modules = sum(r.get("component_counts", {}).get("modules", 0) for r in search_results)
    matched_modules = sum(r.get("matches_by_type", {}).get("modules", 0) for r in search_results)

    return f"""
<section id="overview">
    <h2>Search Overview</h2>
    <div class="section-card">
        <div class="info-item"><strong>Search Query:</strong> {_escape(query_str)}</div>
        <div class="info-item"><strong>Case Sensitive:</strong> {"Yes" if r0.get("case_sensitive") else "No"}</div>
        <div class="info-item"><strong>Regex Mode:</strong> {"Yes" if r0.get("regex") else "No"}</div>

        <div class="info-item" style="margin-top: 20px;"><strong>Total Blueprints:</strong> {total_blueprints}</div>
        <div class="info-item"><strong>Total Modules:</strong> {total_modules}</div>

        <div class="info-item" style="margin-top: 20px;"><strong>Blueprints with Matches:</strong> {blueprints_with_matches}</div>
        <div class="info-item"><strong>Modules with Matches:</strong> {matched_modules}</div>
        <div class="info-item"><strong>Total Matches:</strong> {total_matches}</div>
        <div class="info-item"><strong>Platform:</strong> {result.platform.value.replace('_', ' ').title()}</div>
        <div class="info-item"><strong>Generated:</strong> {_format_datetime(result.metadata.computed_at)}</div>
    </div>
</section>
"""


# ---------------------------------------------
# Blueprint Section
# ---------------------------------------------


def _generate_blueprint_section(result: ProjectionResult) -> str:
    search_results = result.data if isinstance(result.data, list) else [result.data]

    out = ['<section id="blueprints">', "<h2>Blueprint Information</h2>"]

    # Only show blueprints with matches
    blueprints_with_matches = [r for r in search_results if r.get("total_matches", 0) > 0]

    if not blueprints_with_matches:
        out.append('<div class="section-card">')
        out.append('<div class="no-changes">No blueprints with matches found</div>')
        out.append("</div>")
    else:
        for r in blueprints_with_matches:
            name = r.get("blueprint_name", "Unnamed Blueprint")
            matches = r.get("total_matches", 0)
            breakdown = r.get("matches_by_type", {})

            out.append('<div class="section-card">')
            out.append(f"<h3>{_escape(name)}</h3>")
            out.append(f'<div class="info-item"><strong>Total Matches:</strong> {matches}</div>')

            if breakdown:
                labels = []
                for t, count in sorted(breakdown.items()):
                    labels.append(f"{_component_display_name(t)}: {count}")
                out.append(
                    f'<div class="info-item"><strong>By Component Type:</strong> {", ".join(labels)}</div>'
                )

            out.append("</div>")

    out.append("</section>")
    return "\n".join(out)


# ---------------------------------------------
# Results
# ---------------------------------------------


def _generate_results_section(result: ProjectionResult) -> str:
    search_results = result.data if isinstance(result.data, list) else [result.data]
    total = sum(r.get("total_matches", 0) for r in search_results)

    if total == 0:
        return """
<section id="results">
    <h2>Search Results</h2>
    <div class="section-card"><div class="no-changes">No matches found</div></div>
</section>"""

    out = ['<section id="results">', "<h2>Search Results</h2>"]

    # Only show blueprints with matches
    for r in search_results:
        if r.get("total_matches", 0) > 0:  # Only render blueprints with matches
            out.extend(_render_blueprint_results(r))

    out.append("</section>")
    return "\n".join(out)


# ---------------------------------------------
# Per-blueprint renderer
# ---------------------------------------------


def _render_blueprint_results(r: Dict[str, Any]) -> List[str]:
    out = []

    name = r.get("blueprint_name", "Unnamed Blueprint")
    anchor = _sanitize_id(name)
    total = r.get("total_matches", 0)

    out.append(f'<h3 id="blueprint-{anchor}">{_escape(name)} ({total} matches)</h3>')

    if total == 0:
        out.append('<div class="section-card"><div class="no-changes">No matches found</div></div>')
        return out

    matches_by_type = r.get("matches_by_type", {})
    all_matches = r.get("matches", [])
    case_sensitive = r.get("case_sensitive", False)

    groups = {t: [] for t in matches_by_type.keys()}
    for m in all_matches:
        t = m.get("component_type", "unknown")
        if t in groups:
            groups[t].append(m)

    # Only show component types that have matches
    for t in sorted(groups.keys()):
        matches = groups[t]
        if not matches:  # Skip component types with no matches
            continue

        comp_name = _component_display_name(t)
        out.append(f'<h4 class="result-category-title">{comp_name} ({len(matches)} matches)</h4>')
        out.append('<div class="section-card">')

        for m in sorted(matches, key=lambda x: int(x.get("component_id", 0))):
            out.extend(_render_match_card(m, case_sensitive))

        out.append("</div>")

    return out


# ---------------------------------------------
# Structural Context Grouping
# ---------------------------------------------


def _get_condition_prefix(path: str) -> str | None:
    if "filter.conditions" not in path:
        return None
    return path.rsplit(".", 1)[0]


def _collect_condition_entries(all_entries: List[tuple], prefix: str) -> List[tuple]:
    if not prefix:
        return []
    ctx = [(p, v) for p, v in all_entries if p.startswith(prefix + ".")]
    return sorted(ctx)


def _render_condition_block(entries: List[tuple], matched: str) -> str:
    if not entries:
        return ""

    out = [
        '<div class="condition-context">',
        '<div class="context-header">Filter Condition Context:</div>',
        '<div class="context-entries">',
    ]

    for p, v in entries:
        suffix = p.split(".")[-1]
        cls = "context-entry matched" if p == matched else "context-entry"
        mark = " ← MATCHED" if p == matched else ""
        out.append(f'<div class="{cls}">├── {_escape(suffix)}: {_escape(v)}{mark}</div>')

    out.append("</div></div>")
    return "\n".join(out)


# ---------------------------------------------
# Match Card Rendering
# ---------------------------------------------


def _render_match_card(match: Dict[str, Any], case_sensitive: bool) -> List[str]:
    comp_id = match.get("component_id", "?")
    context = match.get("context", "")
    matches = match.get("matches", [])
    literal_entries = match.get("literal_entries", [])

    out = ['<details class="module-accordion">']

    if len(matches) > 1:
        title = f"Component #{comp_id} ({len(matches)} field matches)"
    else:
        title = f"Component #{comp_id}"

    out.append(f'<summary class="module-summary">{_escape(title)}</summary>')
    out.append('<div class="accordion-content">')

    if context:
        out.append(
            f'<div class="component-path" style="margin-bottom: 12px; font-weight: 600;">{_escape(context)}</div>'
        )

    out.append('<div class="change-content">')

    for i, m in enumerate(matches):
        field_path = m["field_path"]
        value = m["value"]
        query = m["matched_query"]

        # Structural context grouping
        prefix = _get_condition_prefix(field_path)
        if prefix:
            ctx_entries = _collect_condition_entries(literal_entries, prefix)
            block = _render_condition_block(ctx_entries, field_path)
            if block:
                out.append(f'<div class="value-content">{block}</div>')

        if i > 0:
            out.append('<hr class="field-separator">')

        out.append('<div class="field-match">')
        out.append(f'<div class="component-path">{_escape(field_path)}</div>')

        if query:
            out.append('<div class="change-line"><span class="label">Matched Query:</span></div>')
            out.append(f'<div class="value-content"><em>"{_escape(query)}"</em></div>')

        if value:
            out.append('<div class="change-line"><span class="label">Field Value:</span></div>')
            trimmed = _trim_field_value_around_match(
                value, query, case_sensitive, m.get("start", -1), m.get("end", -1)
            )
            high = _highlight_context(trimmed, query, case_sensitive)
            out.append(f'<div class="value-content">{high}</div>')

        out.append("</div>")  # field-match

    out.append("</div>")  # change-content
    out.append("</div>")  # accordion-content
    out.append("</details>")
    return out


# ---------------------------------------------
# Highlighting
# ---------------------------------------------


def _trim_field_value_around_match(
    text: str, query: str, case_sensitive: bool, start: int, end: int, context_chars: int = 150
) -> str:

    if not text or len(text) <= context_chars * 2:
        return text

    if start == -1 or end == -1:
        idx = text.find(query) if case_sensitive else text.lower().find(query.lower())
        if idx == -1:
            return text[:context_chars] + "..."
        start = idx
        end = idx + len(query)

    center = (start + end) // 2
    left = max(0, center - context_chars // 2)
    right = min(len(text), center + context_chars // 2)

    snippet = text[left:right]
    if left > 0:
        snippet = "..." + snippet
    if right < len(text):
        snippet += "..."
    return snippet


def _highlight_context(text: str, query: str, case_sensitive: bool) -> str:
    if not text or not query:
        return _escape(text)

    txt = _escape(text)
    q = _escape(query)
    flags = 0 if case_sensitive else re.IGNORECASE
    pat = re.compile(re.escape(q), flags)
    return pat.sub(lambda m: f'<span class="highlight">{m.group(0)}</span>', txt)
