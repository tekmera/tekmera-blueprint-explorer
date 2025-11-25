"""
HTML formatter for search results (refactored, maintainable version).
"""

import html
import re
from pathlib import Path
from typing import List, Dict, Any

from tekmera.functions.meta.types import ProjectionResult


# ---------------------------------------------
# Utility Helpers
# ---------------------------------------------

def _sanitize_id(text: str) -> str:
    """Generate stable, safe HTML IDs by normalizing text."""
    safe = re.sub(r'[^a-zA-Z0-9]+', '-', text)
    safe = re.sub(r'-+', '-', safe).strip('-')
    return safe.lower()


def _escape(text: str) -> str:
    """Shortcut for HTML escaping."""
    return html.escape(text) if text else ""


def _format_datetime(dt) -> str:
    """Make timestamp human-readable."""
    try:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(dt)


def _component_display_name(comp_type: str) -> str:
    """Convert raw component_type into UI label."""
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
    """Public entry point for rendering."""
    return _generate_html(result)


# ---------------------------------------------
# HTML Generator (Top-Level)
# ---------------------------------------------

def _generate_html(result: ProjectionResult) -> str:
    """Generate full HTML document."""
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
    """Load CSS from file with fallback."""
    try:
        css_path = Path(__file__).parent / "styles.css"
        css = css_path.read_text(encoding="utf-8")
        return f"<style>\n{css}\n</style>"
    except FileNotFoundError:
        return "<style>body{font-family:sans-serif}</style>"


# ---------------------------------------------
# Sidebar Generation
# ---------------------------------------------

def _generate_sidebar(result: ProjectionResult) -> str:
    """Builds left navigation pane."""
    search_results = result.data if isinstance(result.data, list) else [result.data]

    total_blueprints = len(search_results)
    blueprints_with_matches = sum(1 for r in search_results if r.get("total_matches", 0) > 0)
    total_matches = sum(r.get("total_matches", 0) for r in search_results)

    blueprint_links = []

    for r in search_results:
        name = r.get("blueprint_name", "Unnamed Blueprint")
        display = name[:20] + "..." if len(name) > 20 else name
        anchor = _sanitize_id(name)
        blueprint_links.append(f'<a href="#blueprint-{anchor}">{_escape(display)}</a>')

    blueprint_html = "<br>".join(blueprint_links)

    return f"""
<div class="sidebar">
    <h3>Navigation</h3>
    <ul>
        <li><a href="#overview">Search Overview</a></li>
        <li><a href="#blueprints">Blueprint Information</a></li>
        <li>
            <a href="#results">Detailed Results</a>
            <div class="subsection">{blueprint_html}</div>
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

    return f"""
<section id="overview">
    <h2>Search Overview</h2>
    <div class="section-card">
        <div class="info-item"><strong>Search Query:</strong> {_escape(query_str)}</div>
        <div class="info-item"><strong>Case Sensitive:</strong> {"Yes" if r0.get("case_sensitive") else "No"}</div>
        <div class="info-item"><strong>Regex Mode:</strong> {"Yes" if r0.get("regex") else "No"}</div>
        <div class="info-item"><strong>Total Blueprints:</strong> {total_blueprints}</div>
        <div class="info-item"><strong>Blueprints with Matches:</strong> {blueprints_with_matches}</div>
        <div class="info-item"><strong>Total Matches:</strong> {total_matches}</div>
        <div class="info-item"><strong>Platform:</strong> {result.platform.value.replace('_', ' ').title()}</div>
        <div class="info-item"><strong>Generated:</strong> {_format_datetime(result.metadata.computed_at)}</div>
    </div>
</section>
"""


# ---------------------------------------------
# Blueprint Information Section
# ---------------------------------------------

def _generate_blueprint_section(result: ProjectionResult) -> str:
    search_results = result.data if isinstance(result.data, list) else [result.data]

    html_parts = ['<section id="blueprints">', '<h2>Blueprint Information</h2>']

    for r in search_results:
        name = r.get("blueprint_name", "Unnamed Blueprint")
        matches = r.get("total_matches", 0)
        breakdown = r.get("matches_by_type", {})

        html_parts.append('<div class="section-card">')
        html_parts.append(f'<h3>{_escape(name)}</h3>')
        html_parts.append(f'<div class="info-item"><strong>Total Matches:</strong> {matches}</div>')

        if breakdown:
            parts = []
            for t, count in sorted(breakdown.items()):
                parts.append(f"{_component_display_name(t)}: {count}")
            html_parts.append(f'<div class="info-item"><strong>By Component Type:</strong> {", ".join(parts)}</div>')

        html_parts.append('</div>')

    html_parts.append('</section>')
    return "\n".join(html_parts)


# ---------------------------------------------
# Results Section
# ---------------------------------------------

def _generate_results_section(result: ProjectionResult) -> str:
    search_results = result.data if isinstance(result.data, list) else [result.data]
    total_matches = sum(r.get("total_matches", 0) for r in search_results)

    if total_matches == 0:
        return """
<section id="results">
    <h2>Search Results</h2>
    <div class="section-card"><div class="no-changes">No matches found</div></div>
</section>"""

    html = ['<section id="results">', '<h2>Search Results</h2>']

    # Use the same renderer for single/multi blueprint
    for r in search_results:
        html.extend(_render_blueprint_results(r))

    html.append("</section>")
    return "\n".join(html)


# ---------------------------------------------
# Per-Blueprint Results Renderer
# ---------------------------------------------

def _render_blueprint_results(r: Dict[str, Any]) -> List[str]:
    html = []

    name = r.get("blueprint_name", "Unnamed Blueprint")
    anchor = _sanitize_id(name)
    total = r.get("total_matches", 0)

    html.append(f'<h3 id="blueprint-{anchor}">{_escape(name)} ({total} matches)</h3>')

    if total == 0:
        html.append('<div class="section-card"><div class="no-changes">No matches found</div></div>')
        return html

    matches_by_type = r.get("matches_by_type", {})
    all_matches = r.get("matches", [])
    case_sensitive = r.get("case_sensitive", False)

    # Build typed groups once
    groups = {t: [] for t in matches_by_type.keys()}
    for m in all_matches:
        t = m.get("component_type", "unknown")
        if t in groups:
            groups[t].append(m)

    # Render each component type
    for t in sorted(groups.keys()):
        comp_name = _component_display_name(t)
        matches = groups[t]

        html.append(f'<h4 class="result-category-title">{comp_name} ({len(matches)} matches)</h4>')
        html.append('<div class="section-card">')

        if not matches:
            html.append('<div class="no-changes">No matches found</div>')
        else:
            for m in matches:
                html.extend(_render_match_card(m, case_sensitive))

        html.append('</div>')

    return html


# ---------------------------------------------
# Match Rendering
# ---------------------------------------------

def _render_match_card(match: Dict[str, Any], case_sensitive: bool) -> List[str]:
    comp_id = match.get("component_id", "?")
    context = match.get("context", "")
    match_text = match.get("match_text", "")
    query = match.get("matched_query", "")

    html = ['<div class="change-card">']

    # Header
    html.append('<div class="change-header">')
    html.append(f"<strong>Component #{comp_id}</strong>")
    if context:
        html.append(f'<span class="component-path">{_escape(context)}</span>')
    html.append('</div>')

    # Body
    html.append('<div class="change-content">')

    if query:
        html.append('<div class="change-line"><span class="label">Matched Query:</span></div>')
        html.append(f'<div class="value-content"><em>"{_escape(query)}"</em></div>')

    if match_text:
        html.append('<div class="change-line"><span class="label">Match Context:</span></div>')
        highlighted = _highlight_context(match_text, query, case_sensitive)
        html.append(f'<div class="value-content">{highlighted}</div>')

    html.append('</div></div>')
    return html


# ---------------------------------------------
# Highlighting Logic
# ---------------------------------------------

def _highlight_context(text: str, query: str, case_sensitive: bool) -> str:
    """Highlight ALL occurrences of query in text."""
    if not text or not query:
        return _escape(text)

    escaped_text = _escape(text)
    escaped_query = _escape(query)

    flags = 0 if case_sensitive else re.IGNORECASE

    # Use regex to highlight all matches
    pattern = re.compile(re.escape(escaped_query), flags)

    def repl(match):
        return f'<span class="highlight">{match.group(0)}</span>'

    return pattern.sub(repl, escaped_text)
