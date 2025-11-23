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
    connection_analysis = extract_connection_analysis(report_data)
    summary_data = extract_summary(report_data, connection_analysis)
    component_groups = extract_component_groups(report_data)
    
    # Generate HTML
    html_content = _generate_html(summary_data, overview_data, component_groups, connection_analysis)
    
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


def extract_summary(report_data: Any, connection_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
    """Extract summary metrics as structured dict."""
    summary = {
        'magnitude': 0.0,
        'magnitude_label': 'UNCHANGED',
        'total_changes': 0,
        'nodes_added': 0,
        'nodes_updated': 0,
        'nodes_removed': 0,
        'connections_updated': 0,
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
            
            # Count by component type (skip connection changes)
            comp_type = _get_component_type(change, report_data.metadata.platform)
            if comp_type is not None:
                summary['categories'][comp_type] = summary['categories'].get(comp_type, 0) + 1
    
    # Add connection change count from connection analysis
    if connection_analysis and connection_analysis.get('has_connection_changes'):
        # Count total modules affected by connections across all replacements
        total_affected_modules = 0
        if 'replacements' in connection_analysis:
            for replacement in connection_analysis['replacements']:
                total_affected_modules += len(replacement.get('modules', []))
        summary['connections_updated'] = total_affected_modules
    
    return summary


def extract_component_groups(report_data: Any) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """Extract component groups as structured dict."""
    # Initialize all possible component types (Connections handled separately in Connection Summary)
    all_component_types = ["Filters", "Routers", "Error Handlers", "Modules"]
    groups = {}
    
    # Initialize empty groups for all component types
    for comp_type in all_component_types:
        comp_id = _sanitize_component_id(comp_type)
        groups[comp_type] = {
            'component_id': comp_id,
            'added': [],
            'updated': [],
            'removed': []
        }
    
    if hasattr(report_data, 'module_changes'):
        changed_components = [c for c in report_data.module_changes if c.change_type.value != 'unchanged']
        
        for change in changed_components:
            comp_type = _get_component_type(change, report_data.metadata.platform)
            
            # Skip connection changes (handled in Connection Summary)
            if comp_type is None:
                continue
                
            # Ensure the component type exists (in case we missed any)
            if comp_type not in groups:
                comp_id = _sanitize_component_id(comp_type)
                groups[comp_type] = {
                    'component_id': comp_id,
                    'added': [],
                    'updated': [],
                    'removed': []
                }
            
            change_data = {
                'module_id': change.module_id,
                'module_name': change.module_name,
                'impact_description': change.impact_description,
                'configuration_changes': change.configuration_changes,
                'raw_data': change.raw_data,
                'raw_data_before': change.raw_data_before
            }
            
            if change.change_type.value == 'added':
                groups[comp_type]['added'].append(change_data)
            elif change.change_type.value == 'removed':
                groups[comp_type]['removed'].append(change_data)
            else:
                groups[comp_type]['updated'].append(change_data)
    
    return groups


def extract_connection_analysis(report_data: Any) -> Dict[str, Any]:
    """Extract connection analysis data from the report."""
    if hasattr(report_data, 'configuration_analysis'):
        config_analysis = report_data.configuration_analysis or {}
        return config_analysis.get('connection_analysis', {})
    return {}


def _get_component_type(change, platform):
    """Get component type for a change."""
    module_type = change.module_type.lower()
    
    # Prioritize component type over change content
    # This ensures filter/router/error handler nodes get categorized correctly
    # even if they also have connection changes
    if "filter" in module_type:
        return "Filters"
    elif "router" in module_type:
        return "Routers"
    elif "error" in module_type:
        return "Error Handlers"
    # Skip pure connection changes - they are handled in Connection Summary section
    elif _is_connection_change_from_config(change):
        return None  # Don't categorize connection changes as components
    else:
        return "Modules"


def _is_connection_change_from_config(change):
    """Check if this is a connection change based on configuration_changes content."""
    config_changes = getattr(change, 'configuration_changes', []) or []
    
    for config_change in config_changes:
        if isinstance(config_change, dict):
            description = config_change.get('description', '')
            field = config_change.get('field', '')
            
            # Look for connection-related descriptions from our diff components
            if 'connection' in description.lower() or '__IMTCONN__' in field or 'account' in field:
                return True
    
    return False


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
                   component_groups: Dict[str, Dict[str, Any]], 
                   connection_analysis: Dict[str, Any] = None) -> str:
    """Generate clean HTML from structured data."""
    
    # Generate individual template blocks
    html_head = _generate_html_head()
    sidebar = _generate_sidebar(component_groups, connection_analysis)
    header_block = _generate_header_block()
    summary_block = _generate_summary_section(summary_data)
    overview_block = _generate_overview_section(overview_data)
    connection_block = _generate_connection_summary_standalone(connection_analysis) if connection_analysis and connection_analysis.get('has_connection_changes') else ""
    details_block = _generate_details_section(component_groups, connection_analysis)
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
{connection_block}
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


def _generate_sidebar(component_groups: Dict[str, Dict[str, Any]], connection_analysis: Dict[str, Any] = None) -> str:
    """Generate sidebar navigation."""
    nav_items = [
        '<li><a href="#summary">Summary</a></li>',
        '<li><a href="#overview">Overview</a></li>'
    ]
    
    # Add connection summary as top-level if available
    if connection_analysis and connection_analysis.get('has_connection_changes'):
        nav_items.append('<li><a href="#connection-summary">Connection Summary</a></li>')
    
    nav_items.append('<li><a href="#details">Details</a></li>')
    
    # Add component subsections under Details
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
                    <p><strong>Connections Updated:</strong> {summary_data['connections_updated']}</p>
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


def _generate_details_section(component_groups: Dict[str, Dict[str, Any]], connection_analysis: Dict[str, Any] = None) -> str:
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
        
        # Generate header with counts
        added_count = len(comp_data['added'])
        updated_count = len(comp_data['updated']) 
        removed_count = len(comp_data['removed'])
        
        # Build count summary
        count_parts = []
        if added_count > 0:
            count_parts.append(f"{added_count} added")
        if updated_count > 0:
            count_parts.append(f"{updated_count} updated")
        if removed_count > 0:
            count_parts.append(f"{removed_count} removed")
        
        if count_parts:
            count_summary = f" ({', '.join(count_parts)})"
        else:
            count_summary = " (no changes)"
            
        details_content.append(f'                    <section id="{comp_id}">')
        details_content.append(f'                        <h3>{comp_type}{count_summary}</h3>')
        
        # Check if this component type has any changes
        has_changes = bool(comp_data['added'] or comp_data['updated'] or comp_data['removed'])
        
        # Wrap all content in a consistent card
        details_content.append('                        <div class="section-card">')
        
        if has_changes:
            # Show sections with items
            if comp_data['added']:
                details_content.append('                            <h4>Added</h4>')
                details_content.append('                            <ul>')
                for item in comp_data['added']:
                    details_content.append(f'                                <li>{_format_component_item(item, comp_type)}</li>')
                details_content.append('                            </ul>')
            
            if comp_data['updated']:
                details_content.append('                            <h4>Updated</h4>')
                details_content.append('                            <ul>')
                for item in comp_data['updated']:
                    details_content.append(f'                                <li>{_format_component_item(item, comp_type)}</li>')
                details_content.append('                            </ul>')
            
            if comp_data['removed']:
                details_content.append('                            <h4>Removed</h4>')
                details_content.append('                            <ul>')
                for item in comp_data['removed']:
                    details_content.append(f'                                <li>{_format_component_item(item, comp_type)}</li>')
                details_content.append('                            </ul>')
        else:
            # Show "No Changes Found" for empty component types
            details_content.append('                            <p class="no-changes">No changes found</p>')
            
        details_content.append('                        </div>')
        
        details_content.append('                    </section>')
    
    details_content.append('                </section>')
    return '\n'.join(details_content)


def _generate_connection_summary_section(connection_analysis: Dict[str, Any]) -> str:
    """Generate the connection summary section."""
    
    # Calculate total connection changes for header count
    replacement_count = len(connection_analysis.get('replacements', []))
    new_count = connection_analysis.get('new_connections_count', 0)
    removed_count = connection_analysis.get('removed_connections_count', 0)
    isolated_count = connection_analysis.get('isolated_changes_count', 0)
    
    # Build count summary for header
    count_parts = []
    if replacement_count > 0:
        # Count modules affected by replacements for more meaningful summary
        total_modules_affected = sum(repl['module_count'] for repl in connection_analysis.get('replacements', []))
        count_parts.append(f"{replacement_count} replacement pattern(s) affecting {total_modules_affected} modules")
    if new_count > 0:
        count_parts.append(f"{new_count} new")
    if removed_count > 0:
        count_parts.append(f"{removed_count} removed") 
    if isolated_count > 0:
        count_parts.append(f"{isolated_count} isolated changes")
        
    if count_parts:
        count_summary = f" ({', '.join(count_parts)})"
    else:
        count_summary = " (no changes)"
    
    content = [
        '',
        '                    <section id="connection-summary">',
        f'                        <h3>Connection Summary{count_summary}</h3>',
    ]
    
    replacements = connection_analysis.get('replacements', [])
    if replacements:
        content.append('                        <h4>Connection Replacements</h4>')
        for replacement in replacements:
            old_display = html.escape(replacement['old_display'])
            new_display = html.escape(replacement['new_display'])
            old_id = html.escape(str(replacement.get('old_connection_id', '')))
            new_id = html.escape(str(replacement.get('new_connection_id', '')))
            module_count = replacement['module_count']
            
            content.append(f'                        <div class="connection-replacement">')
            content.append('                            <p><strong>Connection replacement across {} module(s):</strong></p>'.format(module_count))
            content.append('                            <div class="connection-details">')
            content.append(f'                                <div><strong>From:</strong> {old_display} <span class="connection-id">(ID: {old_id})</span></div>')
            content.append(f'                                <div><strong>To:</strong> {new_display} <span class="connection-id">(ID: {new_id})</span></div>')
            content.append('                            </div>')
            content.append('                            <p><strong>Affected modules:</strong></p>')
            content.append('                            <ul>')
            
            for module in replacement['modules']:
                module_id = html.escape(str(module['id']))
                module_name = html.escape(module['name'])
                content.append(f'                                <li>Module {module_id}: "{module_name}"</li>')
            
            content.append('                            </ul>')
            content.append('                        </div>')
    
    # Add counts for other connection changes
    new_count = connection_analysis.get('new_connections_count', 0)
    removed_count = connection_analysis.get('removed_connections_count', 0)
    isolated_count = connection_analysis.get('isolated_changes_count', 0)
    
    if new_count or removed_count or isolated_count:
        content.append('                        <h4>Other Connection Changes</h4>')
        content.append('                        <ul>')
        if new_count > 0:
            content.append(f'                            <li>{new_count} module(s) got new connections</li>')
        if removed_count > 0:
            content.append(f'                            <li>{removed_count} module(s) lost connections</li>')
        if isolated_count > 0:
            content.append(f'                            <li>{isolated_count} isolated connection change(s)</li>')
        content.append('                        </ul>')
    
    content.append('                    </section>')
    return '\n'.join(content)


def _generate_connection_summary_standalone(connection_analysis: Dict[str, Any]) -> str:
    """Generate Connection Summary as a standalone top-level section."""
    if not connection_analysis or not connection_analysis.get('has_connection_changes'):
        return ""
    
    # Calculate total connection changes for header count
    replacement_count = len(connection_analysis.get('replacements', []))
    new_count = connection_analysis.get('new_connections_count', 0)
    removed_count = connection_analysis.get('removed_connections_count', 0)
    isolated_count = connection_analysis.get('isolated_changes_count', 0)
    
    # Build count summary for header
    count_parts = []
    if replacement_count > 0:
        # Count modules affected by replacements for more meaningful summary
        total_modules_affected = sum(repl['module_count'] for repl in connection_analysis.get('replacements', []))
        count_parts.append(f"{replacement_count} replacement pattern(s) affecting {total_modules_affected} modules")
    if new_count > 0:
        count_parts.append(f"{new_count} new")
    if removed_count > 0:
        count_parts.append(f"{removed_count} removed") 
    if isolated_count > 0:
        count_parts.append(f"{isolated_count} isolated changes")
        
    if count_parts:
        count_summary = f" ({', '.join(count_parts)})"
    else:
        count_summary = " (no changes)"
    
    content = [
        f'                <section id="connection-summary">',
        f'                    <h2>Connection Summary{count_summary}</h2>',
    ]
    
    replacements = connection_analysis.get('replacements', [])
    if replacements:
        content.append('                    <h4>Connection Replacements</h4>')
        for replacement in replacements:
            old_display = html.escape(replacement['old_display'])
            new_display = html.escape(replacement['new_display'])
            old_id = html.escape(str(replacement.get('old_connection_id', '')))
            new_id = html.escape(str(replacement.get('new_connection_id', '')))
            module_count = replacement['module_count']
            
            content.append(f'                    <div class="connection-replacement">')
            content.append('                        <p><strong>Connection replacement across {} module(s):</strong></p>'.format(module_count))
            content.append('                        <div class="connection-details">')
            content.append(f'                            <div><strong>From:</strong> {old_display} <span class="connection-id">(ID: {old_id})</span></div>')
            content.append(f'                            <div><strong>To:</strong> {new_display} <span class="connection-id">(ID: {new_id})</span></div>')
            content.append('                        </div>')
            content.append('                        <p><strong>Affected modules:</strong></p>')
            content.append('                        <ul>')
            
            for module in replacement['modules']:
                module_id = html.escape(str(module['id']))
                module_name = html.escape(module['name'])
                module_type = html.escape(module.get('type', ''))
                
                # Build display with type if available and meaningful
                if module_type and module_type.lower() != module_name.lower():
                    display_text = f'Module {module_id}: "{module_name}" ({module_type})'
                else:
                    display_text = f'Module {module_id}: "{module_name}"'
                
                content.append(f'                            <li>{display_text}</li>')
            
            content.append('                        </ul>')
            content.append('                    </div>')
    
    # Add counts for other connection changes
    new_count = connection_analysis.get('new_connections_count', 0)
    removed_count = connection_analysis.get('removed_connections_count', 0)
    isolated_count = connection_analysis.get('isolated_changes_count', 0)
    
    if new_count or removed_count or isolated_count:
        content.append('                    <h4>Other Connection Changes</h4>')
        content.append('                    <ul>')
        if new_count > 0:
            content.append(f'                        <li>{new_count} module(s) got new connections</li>')
        if removed_count > 0:
            content.append(f'                        <li>{removed_count} module(s) lost connections</li>')
        if isolated_count > 0:
            content.append(f'                        <li>{isolated_count} isolated connection change(s)</li>')
        content.append('                    </ul>')
    
    content.append('                </section>')
    return '\n'.join(content)


def _format_component_item(item: Dict[str, Any], comp_type: str) -> str:
    """Format a component item with detailed information based on type."""
    module_id = item["module_id"]
    module_name = html.escape(item["module_name"])
    base_info = f'Module {module_id}: "{module_name}"'
    
    # Get standardized change description
    change_detail = _get_standardized_change_description(item, comp_type)
    if change_detail:
        # For modules with detailed changes (cards/tables), wrap in accordion
        if comp_type == "Modules" and ('<div class="module-changes-cards">' in change_detail or '<div class="module-changes-table">' in change_detail):
            # Generate a concise summary for the accordion header
            change_summary = _generate_change_summary(item, change_detail)
            summary_line = f'{base_info} ({change_summary})'
            return f'''<details class="module-accordion">
                <summary class="module-summary">{summary_line}</summary>
                <div class="accordion-content">
                    {change_detail}
                </div>
            </details>'''
        else:
            # For simple changes, keep the original format
            return f'{base_info}<br><span class="component-detail">{change_detail}</span>'
    
    return base_info


def _get_standardized_change_description(item: Dict[str, Any], comp_type: str) -> str:
    """Generate standardized change descriptions using 'What changed: from → to' format."""
    
    # Handle additions first (no from/to comparison needed)
    if not item.get('raw_data_before'):
        return "Added to workflow"
    
    # Component-specific standardized descriptions
    if comp_type == "Connections":
        return _get_connection_change_description(item)
    elif comp_type == "Filters":
        return _get_filter_change_description(item)
    elif comp_type == "Routers":
        return _get_router_change_description(item)
    elif comp_type == "Error Handlers":
        return _get_error_handler_change_description(item)
    elif comp_type == "Modules":
        return _get_module_change_description(item)
    else:
        # Fallback to configuration changes
        return _get_generic_change_description(item)


def _get_filter_change_description(item: Dict[str, Any]) -> str:
    """Display filter changes from pre-computed configuration_changes."""
    return _display_configuration_changes(item.get('configuration_changes', []))


def _display_configuration_changes(config_changes: List[Dict]) -> str:
    """Display all configuration changes as field: old_value → new_value format."""
    if not config_changes:
        return "Configuration updated"
    
    descriptions = []
    for change in config_changes:  # Show ALL changes, no limit
        field = change.get('field', 'unknown')
        old_val = change.get('old_value', '')
        new_val = change.get('new_value', '')
        change_type = change.get('change_type', 'modified')
        description = change.get('description', '')
        
        # Use the analyzer's description if available, otherwise format field change
        if description and description != f"Parameter '{field}' changed":
            descriptions.append(description)
        else:
            if change_type == "added":
                descriptions.append(f"{field}: added {_format_change_value(new_val)}")
            elif change_type == "removed":
                descriptions.append(f"{field}: removed {_format_change_value(old_val)}")
            else:
                # Use smart JSON detection for modified values
                formatted_change = _detect_and_format_change_value(old_val, new_val, field)
                descriptions.append(formatted_change)
    
    return "; ".join(descriptions) if descriptions else "Configuration updated"


def _format_change_value(value) -> str:
    """Format a value for configuration change display."""
    if value is None:
        return "null"
    elif isinstance(value, str):
        return f'"{value}"' if value else '""'
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, (list, dict)):
        import json
        try:
            return json.dumps(value, separators=(',', ':'))
        except:
            return str(value)
    else:
        return str(value)


def _get_router_change_description(item: Dict[str, Any]) -> str:
    """Standardized router change description."""
    raw_data = item.get('raw_data', {})
    raw_data_before = item.get('raw_data_before', {})
    
    current_routes = raw_data.get('routes', [])
    previous_routes = raw_data_before.get('routes', []) if raw_data_before else []
    
    current_count = len(current_routes) if current_routes else 0
    previous_count = len(previous_routes) if previous_routes else 0
    
    if current_count != previous_count:
        return f'Routes: {previous_count} → {current_count}'
    else:
        return f'Routes: {current_count} (reconfigured)'


def _get_error_handler_change_description(item: Dict[str, Any]) -> str:
    """Standardized error handler change description."""
    if not item.get('raw_data_before'):
        return "Added to workflow"
    
    # Try to get meaningful configuration changes for error handlers too
    config_changes = item.get('configuration_changes', [])
    for change in config_changes:
        if isinstance(change, dict):
            description = change.get('description', '')
            if description and len(description) > 15 and description != 'Error handler configuration changed':
                return html.escape(description)
            
            field = change.get('field', '')
            old_val = change.get('old_value', '')
            new_val = change.get('new_value', '')
            
            if field and old_val != new_val:
                param_name = field.split('.')[-1] if '.' in field else field
                old_display = _format_value_for_description(old_val)
                new_display = _format_value_for_description(new_val)
                return f'{param_name}: {old_display} → {new_display}'
    
    return "Error handler: Configuration updated"


def _get_module_change_description(item: Dict[str, Any]) -> str:
    """Generate module change description as a table for field-level changes."""
    raw_data = item.get('raw_data', {})
    raw_data_before = item.get('raw_data_before', {})
    
    # Use the proper diff components if we have raw data
    if raw_data_before and raw_data:
        try:
            # Import the module diff analyzer
            from tekmera.functions.components.modules.diff import analyze_module_differences
            from tekmera.functions.meta.types import Platform
            
            # Determine platform (this could be passed in, but let's detect)
            platform = Platform.WORKFRONT_FUSION  # Default, could be improved
            
            # Get detailed module differences
            differences = analyze_module_differences(raw_data_before, raw_data, platform)
            
            if differences:
                return _format_module_changes_table(differences)
        except Exception:
            # Fall back to manual analysis if diff components fail
            pass
    
    # Fallback to existing configuration changes analysis
    config_changes = item.get('configuration_changes', [])
    if config_changes:
        return _format_config_changes_table(config_changes)
    
    # Final fallback
    return "Configuration updated"


def _format_module_changes_table(differences: list) -> str:
    """Format module differences as clean cards."""
    if not differences:
        return "No changes detected"
    
    cards = []
    for diff in differences:
        field_name = diff.field_path.split('.')[-1] if '.' in diff.field_path else diff.field_path
        
        # Format values with diff highlighting
        old_display, new_display = _format_card_values_with_diff(diff.old_value, diff.new_value)
        
        change_type = diff.change_type.capitalize()
        
        cards.append(f'''
            <div class="change-card">
                <div class="change-header">
                    <strong>{change_type} {html.escape(field_name)}</strong>
                </div>
                <div class="change-content">
                    <div class="change-line">
                        <span class="label">Before:</span>
                    </div>
                    <div class="value-content old-value">{old_display}</div>
                    <div class="change-line">
                        <span class="label">After:</span>
                    </div>
                    <div class="value-content new-value">{new_display}</div>
                </div>
            </div>''')
    
    return f'''<div class="module-changes-cards">
        {''.join(cards)}
    </div>'''


def _format_config_changes_table(config_changes: list) -> str:
    """Format configuration changes as clean cards (same as module changes)."""
    if not config_changes:
        return "No changes detected"
    
    cards = []
    for change in config_changes:
        field = change.get('field', 'unknown')
        field_name = field.split('.')[-1] if '.' in field else field
        change_type = change.get('change_type', 'modified').capitalize()
        old_val = change.get('old_value', '')
        new_val = change.get('new_value', '')
        
        # Format values with diff highlighting
        old_display, new_display = _format_card_values_with_diff(old_val, new_val)
        
        cards.append(f'''
            <div class="change-card">
                <div class="change-header">
                    <strong>{change_type} {html.escape(field_name)}</strong>
                </div>
                <div class="change-content">
                    <div class="change-line">
                        <span class="label">Before:</span>
                    </div>
                    <div class="value-content old-value">{old_display}</div>
                    <div class="change-line">
                        <span class="label">After:</span>
                    </div>
                    <div class="value-content new-value">{new_display}</div>
                </div>
            </div>''')
    
    return f'''<div class="module-changes-cards">
        {''.join(cards)}
    </div>'''


def _format_table_value(value) -> str:
    """Format a value for table display - clean and truncated if needed."""
    if value is None:
        return '<span class="null-value">null</span>'
    elif isinstance(value, bool):
        return f'<span class="bool-value">{"true" if value else "false"}</span>'
    elif isinstance(value, (int, float)):
        return f'<span class="number-value">{value}</span>'
    elif isinstance(value, str):
        # Truncate long strings to keep table readable
        if len(value) > 60:
            display_value = value[:57] + "..."
        else:
            display_value = value
        return f'<span class="string-value">{html.escape(display_value)}</span>'
    elif isinstance(value, (list, dict)):
        return f'<span class="complex-value">{type(value).__name__} ({len(value)} items)</span>'
    else:
        str_value = str(value)
        if len(str_value) > 60:
            str_value = str_value[:57] + "..."
        return f'<span class="other-value">{html.escape(str_value)}</span>'


def _format_card_value(value) -> str:
    """Format a value for card display - no truncation, italicized values."""
    if value is None:
        return '<em class="null-value">null</em>'
    elif isinstance(value, bool):
        return f'<em class="bool-value">{"true" if value else "false"}</em>'
    elif isinstance(value, (int, float)):
        return f'<em class="number-value">{value}</em>'
    elif isinstance(value, str):
        # No truncation for cards - let them wrap properly, italicize the value
        return f'<em class="string-value">{html.escape(value)}</em>'
    elif isinstance(value, (list, dict)):
        return f'<em class="complex-value">{type(value).__name__} ({len(value)} items)</em>'
    else:
        return f'<em class="other-value">{html.escape(str(value))}</em>'


def _generate_change_summary(item: Dict[str, Any], change_detail: str) -> str:
    """Generate a concise summary of what changed in a module."""
    # Handle additions
    if not item.get('raw_data_before'):
        return "added"
    
    # Try to extract meaningful information from the change detail
    summary_parts = []
    
    # Look for card headers to identify what fields changed
    if 'Modified url' in change_detail:
        summary_parts.append("url modified")
    if 'Modified connection' in change_detail:
        summary_parts.append("connection modified")
    if 'Modified mapper' in change_detail:
        summary_parts.append("mapper modified")
    if 'Modified parameters' in change_detail:
        summary_parts.append("parameters modified")
    if 'Added ' in change_detail:
        summary_parts.append("fields added")
    if 'Removed ' in change_detail:
        summary_parts.append("fields removed")
    
    # Count the number of change cards for field count
    card_count = change_detail.count('<div class="change-card">')
    
    # Generate summary
    if summary_parts:
        if len(summary_parts) == 1:
            return f"updated — {summary_parts[0]}"
        elif len(summary_parts) <= 3:
            return f"updated — {', '.join(summary_parts)}"
        else:
            return f"updated — {card_count} field changes"
    elif card_count > 0:
        if card_count == 1:
            return "updated — 1 field change"
        else:
            return f"updated — {card_count} field changes"
    else:
        return "updated"


def _format_card_values_with_diff(old_value, new_value) -> tuple[str, str]:
    """Format old and new values with diff highlighting."""
    # For string values, highlight character-level differences
    if isinstance(old_value, str) and isinstance(new_value, str):
        old_highlighted, new_highlighted = _highlight_string_diff(old_value, new_value)
        return f'<em class="string-value">{old_highlighted}</em>', f'<em class="string-value">{new_highlighted}</em>'
    else:
        # For non-strings, use regular formatting
        return _format_card_value(old_value), _format_card_value(new_value)


def _highlight_string_diff(old_str: str, new_str: str) -> tuple[str, str]:
    """Highlight differences between two strings using character-level comparison."""
    import difflib
    
    # Use difflib to find differences
    matcher = difflib.SequenceMatcher(None, old_str, new_str)
    
    old_highlighted = []
    new_highlighted = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # Same parts - no highlighting
            old_part = html.escape(old_str[i1:i2])
            new_part = html.escape(new_str[j1:j2])
        elif tag == 'delete':
            # Removed from old
            old_part = f'<span class="diff-removed">{html.escape(old_str[i1:i2])}</span>'
            new_part = ''  # Nothing added to new string
        elif tag == 'insert':
            # Added to new
            old_part = ''  # Nothing in old string
            new_part = f'<span class="diff-added">{html.escape(new_str[j1:j2])}</span>'
        elif tag == 'replace':
            # Changed content
            old_part = f'<span class="diff-removed">{html.escape(old_str[i1:i2])}</span>'
            new_part = f'<span class="diff-added">{html.escape(new_str[j1:j2])}</span>'
        
        old_highlighted.append(old_part)
        new_highlighted.append(new_part)
    
    return ''.join(old_highlighted), ''.join(new_highlighted)


def _get_generic_change_description(item: Dict[str, Any]) -> str:
    """Generic standardized change description."""
    config_changes = item.get('configuration_changes', [])
    
    if config_changes and len(config_changes) > 0:
        return "Configuration: Updated"
    
    return "Module: Updated"


def _format_json_content(value: Any) -> str:
    """Format a value showing actual JSON content for diffs."""
    if value is None:
        return "null"
    elif isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, list):
        # Show actual list content for small lists, summary for large ones
        if len(value) <= 2:
            import json
            return json.dumps(value, separators=(',', ':'))
        else:
            return f"[{len(value)} items]"
    elif isinstance(value, dict):
        # Show actual dict content for small dicts, summary for large ones  
        if len(value) <= 3:
            import json
            return json.dumps(value, separators=(',', ':'))
        else:
            return f"{{{len(value)} fields}}"
    else:
        return str(value)


def _format_json_value(value: Any) -> str:
    """Format a value for JSON diff display."""
    if value is None:
        return "null"
    elif isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, list):
        return f"[{len(value)} items]"
    elif isinstance(value, dict):
        return f"{{{len(value)} fields}}"
    else:
        return str(value)


def _format_value_for_description(value: any) -> str:
    """Format a value for display in change descriptions."""
    if value is None:
        return "null"
    elif isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (dict, list)):
        return f"{type(value).__name__} ({len(value)} items)"
    else:
        return str(value)


def _extract_filter_details(item: Dict[str, Any]) -> str:
    """Extract detailed before/after information for filter changes."""
    raw_data = item.get('raw_data', {})
    raw_data_before = item.get('raw_data_before', {})
    
    # Get filter data from both versions
    current_filter = raw_data.get('filter', {}) or raw_data.get('parameters', {}).get('filter', {})
    previous_filter = raw_data_before.get('filter', {}) or raw_data_before.get('parameters', {}).get('filter', {}) if raw_data_before else {}
    
    # Extract condition information
    if current_filter and previous_filter:
        current_conditions = current_filter.get('conditions', [])
        previous_conditions = previous_filter.get('conditions', [])
        
        if current_conditions and previous_conditions:
            # Get the first condition for comparison (most common case)
            current_first = current_conditions[0][0] if current_conditions and current_conditions[0] else {}
            previous_first = previous_conditions[0][0] if previous_conditions and previous_conditions[0] else {}
            
            if current_first and previous_first:
                current_field = current_first.get('a', '')
                previous_field = previous_first.get('a', '')
                current_op = current_first.get('o', '')
                previous_op = previous_first.get('o', '')
                
                if current_field != previous_field:
                    return f'Condition field changed: <strong>{html.escape(previous_field)}</strong> → <strong>{html.escape(current_field)}</strong>'
                elif current_op != previous_op:
                    return f'Condition operator changed: <strong>{html.escape(previous_op)}</strong> → <strong>{html.escape(current_op)}</strong>'
                else:
                    # Check for value changes
                    current_val = current_first.get('b', '')
                    previous_val = previous_first.get('b', '')
                    if current_val != previous_val:
                        return f'Condition value changed: <strong>{html.escape(str(previous_val))}</strong> → <strong>{html.escape(str(current_val))}</strong>'
    
    # Fallback to checking configuration changes for detailed info
    config_changes = item.get('configuration_changes', [])
    for change in config_changes:
        if isinstance(change, dict) and change.get('field', '').startswith('conditions.'):
            old_val = html.escape(str(change.get('old_value', '')))
            new_val = html.escape(str(change.get('new_value', '')))
            field = change.get('field', '').split('.')[-1]
            if field == 'a':
                return f'Condition field changed: <strong>{old_val}</strong> → <strong>{new_val}</strong>'
            elif field == 'b':
                return f'Condition value changed: <strong>{old_val}</strong> → <strong>{new_val}</strong>'
            elif field == 'o':
                return f'Condition operator changed: <strong>{old_val}</strong> → <strong>{new_val}</strong>'
    
    return 'Filter configuration updated'


def _get_connection_change_description(item: Dict[str, Any]) -> str:
    """Standardized connection change description."""
    # Check configuration changes for specific connection details from diff components
    config_changes = item.get('configuration_changes', [])
    
    for change in config_changes:
        if isinstance(change, dict):
            description = change.get('description', '')
            
            # Use the human description from the connection diff components
            if description and 'connection' in description.lower():
                return html.escape(description)
    
    # Fallback for generic connection changes
    impact_desc = item.get('impact_description', '')
    if 'connection' in impact_desc.lower():
        return html.escape(impact_desc)
    
    return "Connection: Configuration updated"


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
        
        /* Module Changes Card Styles */
        .module-changes-cards {
            margin: 15px 0;
        }
        
        .change-card {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            margin: 12px 0;
            padding: 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .change-header {
            margin-bottom: 12px;
        }
        
        .change-header strong {
            color: var(--tekmera-blue);
            font-size: 1em;
            font-weight: bold;
        }
        
        .change-content {
            margin-left: 20px;
        }
        
        .change-line {
            margin: 8px 0 4px 0;
        }
        
        .change-line .label {
            font-weight: 600;
            color: #6c757d;
            font-style: normal;
        }
        
        .value-content {
            margin: 4px 0 12px 20px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            word-wrap: break-word;
            white-space: pre-wrap;
            line-height: 1.4;
            font-style: normal;
        }
        
        .value-content em {
            font-style: italic;
        }
        
        .string-value {
            color: #d73a49;
        }
        
        .number-value {
            color: #005cc5;
        }
        
        .bool-value {
            color: #e36209;
        }
        
        .null-value {
            color: #6f42c1;
            font-style: italic;
        }
        
        .complex-value {
            color: #28a745;
            font-style: italic;
        }
        
        .other-value {
            color: #6c757d;
        }
        
        /* Diff highlighting styles */
        .diff-removed {
            background-color: #ffeef0;
            text-decoration: line-through;
            color: #d1242f;
            font-weight: 600;
        }
        
        .diff-added {
            background-color: #e6ffed;
            color: #28a745;
            font-weight: 600;
        }
        
        /* Module Accordion Styles */
        .module-accordion {
            margin: 8px 0;
            border: 1px solid #e1e5e9;
            border-radius: 6px;
            background: #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        }
        
        .module-accordion[open] {
            border-color: var(--tekmera-sky);
            box-shadow: 0 2px 8px rgba(66, 184, 230, 0.15);
        }
        
        .module-summary {
            padding: 12px 16px;
            cursor: pointer;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 6px;
            font-weight: 600;
            color: var(--tekmera-blue);
            transition: all 0.2s ease;
            position: relative;
            list-style: none;
            outline: none;
        }
        
        .module-summary .change-summary {
            color: #6c757d;
            font-weight: 500;
            font-size: 0.9em;
        }
        
        .module-summary:hover {
            background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
            color: var(--tekmera-sky);
        }
        
        .module-summary::-webkit-details-marker {
            display: none;
        }
        
        .module-summary::before {
            content: '▶';
            position: absolute;
            right: 16px;
            top: 50%;
            transform: translateY(-50%);
            transition: transform 0.2s ease;
            font-size: 0.8em;
            color: var(--tekmera-sky);
        }
        
        .module-accordion[open] .module-summary::before {
            transform: translateY(-50%) rotate(90deg);
        }
        
        .accordion-content {
            padding: 0 16px 16px 16px;
            animation: slideDown 0.2s ease-out;
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Override component-detail styling when inside accordion */
        .accordion-content .component-detail {
            color: inherit;
            font-size: inherit;
            margin-left: 0;
            padding-left: 0;
            border-left: none;
            font-style: normal;
            display: block;
            margin-top: 12px;
        }
        
        /* Responsive design for cards */
        @media (max-width: 768px) {
            .change-values {
                grid-template-columns: 1fr;
            }
        }
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