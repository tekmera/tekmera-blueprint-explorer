"""
HTML formatter for report output.

Clean, simple HTML generation for Tekmera reports with proper separation of concerns.
"""

import html
import re
from pathlib import Path
from typing import Any, Dict, List


def render_report_to_html(report_data: Any, output_path: str) -> str:
    """
    Render a report to clean HTML format.
    
    Args:
        report_data: The report object with to_text() method
        output_path: Path where the HTML should be saved
        
    Returns:
        The path to the generated HTML file
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Extract structured data from report
    overview_data = extract_overview(report_data)
    summary_data = extract_summary(report_data)
    component_groups = extract_component_groups(report_data)
    
    # Generate HTML
    html_content = _generate_html(summary_data, overview_data, component_groups)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return str(output_file)


def extract_overview(report_data: Any) -> Dict[str, str]:
    """Extract overview data as structured dict."""
    overview = {}
    
    if hasattr(report_data, 'blueprint1_name'):
        overview['first_blueprint'] = report_data.blueprint1_name
        overview['second_blueprint'] = report_data.blueprint2_name
        overview['platform'] = _format_platform(report_data.metadata.platform)
        overview['generated'] = report_data.metadata.generated_at.strftime('%Y-%m-%d %H:%M:%S')
    
    return overview


def extract_summary(report_data: Any) -> Dict[str, Any]:
    """Extract summary metrics as structured dict."""
    summary = {
        'magnitude': 0.0,
        'magnitude_label': 'UNCHANGED',
        'total_changes': 0,
        'nodes_added': 0,
        'nodes_updated': 0,
        'nodes_removed': 0,
        'categories': {}
    }
    
    if hasattr(report_data, 'summary') and hasattr(report_data, 'module_changes'):
        report_summary = report_data.summary
        summary['magnitude'] = report_summary.change_magnitude
        summary['magnitude_label'] = report_summary.change_scale.value.upper()
        
        # Count changes by type
        changed_components = [c for c in report_data.module_changes if c.change_type.value != 'unchanged']
        summary['total_changes'] = len(changed_components)
        
        for change in changed_components:
            if change.change_type.value == 'added':
                summary['nodes_added'] += 1
            elif change.change_type.value == 'removed':
                summary['nodes_removed'] += 1
            else:
                summary['nodes_updated'] += 1
            
            # Count by component type
            comp_type = _get_component_type(change, report_data.metadata.platform)
            summary['categories'][comp_type] = summary['categories'].get(comp_type, 0) + 1
    
    return summary


def extract_component_groups(report_data: Any) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """Extract component groups as structured dict."""
    groups = {}
    
    if hasattr(report_data, 'module_changes'):
        changed_components = [c for c in report_data.module_changes if c.change_type.value != 'unchanged']
        
        for change in changed_components:
            comp_type = _get_component_type(change, report_data.metadata.platform)
            comp_id = _sanitize_component_id(comp_type)
            
            if comp_type not in groups:
                groups[comp_type] = {
                    'component_id': comp_id,
                    'added': [],
                    'updated': [],
                    'removed': []
                }
            
            change_data = {
                'module_id': change.module_id,
                'module_name': change.module_name
            }
            
            if change.change_type.value == 'added':
                groups[comp_type]['added'].append(change_data)
            elif change.change_type.value == 'removed':
                groups[comp_type]['removed'].append(change_data)
            else:
                groups[comp_type]['updated'].append(change_data)
    
    return groups


def _get_component_type(change, platform):
    """Get component type for a change."""
    module_type = change.module_type.lower()
    
    if "filter" in module_type:
        return "Filters"
    elif "router" in module_type:
        return "Routers"
    elif "error" in module_type:
        return "Error Handlers"
    elif "workfront" in module_type:
        return "Workfront Modules"
    else:
        return "Modules"


def _sanitize_component_id(component_type: str) -> str:
    """Generate safe HTML ID from component type."""
    # Lowercase, spaces to hyphens, remove invalid characters
    safe_id = component_type.lower().replace(' ', '-')
    safe_id = re.sub(r'[^a-z0-9-]', '', safe_id)
    return safe_id


def _format_platform(platform):
    """Format platform for display."""
    if hasattr(platform, 'value'):
        value = platform.value
    else:
        value = str(platform)
    
    if value == "workfront_fusion":
        return "Workfront Fusion"
    elif value == "make_com":
        return "Make.com"
    else:
        return value.replace('_', ' ').title()


def _generate_html(summary_data: Dict[str, Any], overview_data: Dict[str, str], 
                   component_groups: Dict[str, Dict[str, Any]]) -> str:
    """Generate clean HTML from structured data."""
    
    # Generate individual template blocks
    html_head = _generate_html_head()
    sidebar = _generate_sidebar(component_groups)
    header_block = _generate_header_block()
    summary_block = _generate_summary_section(summary_data)
    overview_block = _generate_overview_section(overview_data)
    details_block = _generate_details_section(component_groups)
    javascript_block = _get_javascript()
    
    # Assemble the complete document
    return f"""<!DOCTYPE html>
<html lang="en">
{html_head}
<body>
    <div class="page-container">
{sidebar}
        <div class="main-content">
            <div class="container">
{header_block}
{summary_block}
{overview_block}
{details_block}
            </div>
        </div>
    </div>
{javascript_block}
</body>
</html>"""


def _generate_html_head() -> str:
    """Generate HTML head section."""
    return f"""<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tekmera Structural Delta Report</title>
{_load_css()}
</head>"""


def _generate_header_block() -> str:
    """Generate header block."""
    return """                <header>
                    <h1>Tekmera Structural Delta Report</h1>
                </header>"""


def _generate_sidebar(component_groups: Dict[str, Dict[str, Any]]) -> str:
    """Generate sidebar navigation."""
    nav_items = [
        '<li><a href="#summary">Summary</a></li>',
        '<li><a href="#overview">Overview</a></li>',
        '<li><a href="#details">Details</a></li>'
    ]
    
    # Add component subsections
    for comp_type in sorted(component_groups.keys()):
        comp_id = component_groups[comp_type]['component_id']
        nav_items.append(f'<li class="subsection"><a href="#{comp_id}">{comp_type}</a></li>')
    
    nav_links = '\n'.join(f'                {item}' for item in nav_items)
    
    return f"""        <div class="sidebar">
            <h3>Navigation</h3>
            <ul>
{nav_links}
            </ul>
        </div>"""


def _generate_summary_section(summary_data: Dict[str, Any]) -> str:
    """Generate Summary section with exact specified format."""
    magnitude_pct = summary_data['magnitude'] * 100
    
    # Format categories as inline text
    if len(summary_data['categories']) <= 8:
        categories_text = ', '.join([
            f"{comp_type} ({count})" 
            for comp_type, count in sorted(summary_data['categories'].items())
        ])
    else:
        # If more than 8 categories, use a list (though this is unlikely)
        categories_text = "Multiple component types (see details below)"
    
    return f"""                <section id="summary">
                    <h2>Summary</h2>
                    <p><strong>Magnitude:</strong> {magnitude_pct:.1f}% ({summary_data['magnitude_label']})</p>
                    <p><strong>Total Differences:</strong> {summary_data['total_changes']}</p>
                    <p><strong>Nodes Added:</strong> {summary_data['nodes_added']}</p>
                    <p><strong>Nodes Updated:</strong> {summary_data['nodes_updated']}</p>
                    <p><strong>Nodes Removed:</strong> {summary_data['nodes_removed']}</p>
                    <p><strong>Component Types:</strong> {categories_text}</p>
                </section>"""


def _generate_overview_section(overview_data: Dict[str, str]) -> str:
    """Generate Overview section."""
    if not overview_data:
        return """                <section id="overview">
                    <h2>Overview</h2>
                    <p>No overview data available.</p>
                </section>"""
    
    return f"""                <section id="overview">
                    <h2>Overview</h2>
                    <div class="info-item">First: {html.escape(overview_data.get('first_blueprint', 'Unknown'))}</div>
                    <div class="info-item">Second: {html.escape(overview_data.get('second_blueprint', 'Unknown'))}</div>
                    <div class="info-item">Platform: {html.escape(overview_data.get('platform', 'Unknown'))}</div>
                    <div class="info-item">Generated: {html.escape(overview_data.get('generated', 'Unknown'))}</div>
                </section>"""


def _generate_details_section(component_groups: Dict[str, Dict[str, Any]]) -> str:
    """Generate Details section with component subsections."""
    if not component_groups:
        return """                <section id="details">
                    <h2>Details</h2>
                    <p>No changes detected.</p>
                </section>"""
    
    details_content = ['                <section id="details">']
    details_content.append('                    <h2>Details</h2>')
    
    # Generate subsection for each component type
    for comp_type in sorted(component_groups.keys()):
        comp_data = component_groups[comp_type]
        comp_id = comp_data['component_id']
        
        details_content.append(f'                    <section id="{comp_id}">')
        details_content.append(f'                        <h3>{comp_type}</h3>')
        
        # Only show sections with items (skip empty categories)
        if comp_data['added']:
            details_content.append('                        <h4>Added</h4>')
            details_content.append('                        <ul>')
            for item in comp_data['added']:
                details_content.append(f'                            <li>Module {item["module_id"]}: "{html.escape(item["module_name"])}"</li>')
            details_content.append('                        </ul>')
        
        if comp_data['updated']:
            details_content.append('                        <h4>Updated</h4>')
            details_content.append('                        <ul>')
            for item in comp_data['updated']:
                details_content.append(f'                            <li>Module {item["module_id"]}: "{html.escape(item["module_name"])}"</li>')
            details_content.append('                        </ul>')
        
        if comp_data['removed']:
            details_content.append('                        <h4>Removed</h4>')
            details_content.append('                        <ul>')
            for item in comp_data['removed']:
                details_content.append(f'                            <li>Module {item["module_id"]}: "{html.escape(item["module_name"])}"</li>')
            details_content.append('                        </ul>')
        
        details_content.append('                    </section>')
    
    details_content.append('                </section>')
    return '\n'.join(details_content)


def _load_css() -> str:
    """Load CSS styles from separate file."""
    try:
        css_path = Path(__file__).parent / "styles.css"
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        return f"    <style>\n{css_content}\n    </style>"
    except FileNotFoundError:
        # Fallback to minimal inline styles if CSS file not found
        return """    <style>
        :root { --tekmera-blue: #183664; --tekmera-sky: #42B8E6; }
        body { font-family: sans-serif; color: #333; margin: 0; padding: 20px; }
        h1, h2, h3 { color: var(--tekmera-blue); }
        .sidebar { background: var(--tekmera-blue); color: white; padding: 20px; }
    </style>"""


def _get_javascript() -> str:
    """Get navigation JavaScript with improved anchor handling."""
    return """    <script>
        document.querySelectorAll('.sidebar a').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.hash.substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    
                    document.querySelectorAll('.sidebar a').forEach(a => a.classList.remove('active'));
                    this.classList.add('active');
                }
            });
        });
    </script>"""