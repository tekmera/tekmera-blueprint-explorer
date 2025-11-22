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
    all_component_types = ["Filters", "Routers", "Error Handlers", "Workfront Modules", "Modules"]
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
    
    # Skip connection changes - they are handled in Connection Summary section
    if _is_connection_change_from_config(change):
        return None  # Don't categorize connection changes as components
    elif "filter" in module_type:
        return "Filters"
    elif "router" in module_type:
        return "Routers"
    elif "error" in module_type:
        return "Error Handlers"
    elif "workfront" in module_type:
        return "Workfront Modules"
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
    base_info = f'Module {item["module_id"]}: "{html.escape(item["module_name"])}"'
    
    # Get standardized change description
    change_detail = _get_standardized_change_description(item, comp_type)
    if change_detail:
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
    elif comp_type in ["Modules", "Workfront Modules"]:
        return _get_module_change_description(item)
    else:
        # Fallback to configuration changes
        return _get_generic_change_description(item)


def _get_filter_change_description(item: Dict[str, Any]) -> str:
    """Standardized filter change description using diff components."""
    raw_data = item.get('raw_data', {})
    raw_data_before = item.get('raw_data_before', {})
    
    # Use the proper filter diff components if we have raw data
    if raw_data_before and raw_data:
        try:
            # Import the filter diff analyzer
            from tekmera.functions.components.filters.diff import analyze_filter_differences
            from tekmera.functions.meta.types import Platform
            
            # Get filter data for analysis
            current_filter = raw_data.get('filter', {}) or raw_data.get('parameters', {}).get('filter', {})
            previous_filter = raw_data_before.get('filter', {}) or raw_data_before.get('parameters', {}).get('filter', {})
            
            if current_filter and previous_filter:
                platform = Platform.WORKFRONT_FUSION  # Default, could be improved
                
                # Get detailed filter differences
                differences = analyze_filter_differences(previous_filter, current_filter, platform)
                
                if differences:
                    # Use the most significant change
                    significant_change = None
                    for diff in differences:
                        if diff.significance in ['critical', 'important']:
                            significant_change = diff
                            break
                    if not significant_change and differences:
                        significant_change = differences[0]
                    
                    if significant_change:
                        # Format based on the logical impact
                        old_display = _format_value_for_description(significant_change.old_value)
                        new_display = _format_value_for_description(significant_change.new_value)
                        
                        if 'field' in significant_change.field_path:
                            return f'Condition field: {old_display} → {new_display}'
                        elif 'operator' in significant_change.field_path or significant_change.field_path.endswith('.o'):
                            return f'Condition operator: {old_display} → {new_display}'
                        elif 'value' in significant_change.field_path or significant_change.field_path.endswith('.b'):
                            return f'Condition value: {old_display} → {new_display}'
                        else:
                            return html.escape(significant_change.description)
        except Exception:
            # Fall back to manual analysis if diff components fail
            pass
    
    # Fallback to manual filter analysis
    current_filter = raw_data.get('filter', {}) or raw_data.get('parameters', {}).get('filter', {})
    previous_filter = raw_data_before.get('filter', {}) or raw_data_before.get('parameters', {}).get('filter', {}) if raw_data_before else {}
    
    # Extract condition information manually
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
                current_val = current_first.get('b', '')
                previous_val = previous_first.get('b', '')
                
                if current_field != previous_field:
                    return f'Condition field: {html.escape(previous_field)} → {html.escape(current_field)}'
                elif current_op != previous_op:
                    return f'Condition operator: {html.escape(previous_op)} → {html.escape(current_op)}'
                elif current_val != previous_val:
                    return f'Condition value: {html.escape(str(previous_val))} → {html.escape(str(current_val))}'
    
    return "Filter: Configuration updated"


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
    """Standardized module change description using diff components."""
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
                # Use the most significant change
                significant_change = None
                for diff in differences:
                    if diff.significance in ['critical', 'important']:
                        significant_change = diff
                        break
                if not significant_change and differences:
                    significant_change = differences[0]
                
                if significant_change:
                    # Format the change properly
                    if significant_change.change_type == 'modified':
                        old_display = _format_value_for_description(significant_change.old_value)
                        new_display = _format_value_for_description(significant_change.new_value)
                        field_name = significant_change.field_path.split('.')[-1]
                        return f'{field_name}: {old_display} → {new_display}'
                    else:
                        return html.escape(significant_change.description)
        except Exception:
            # Fall back to manual analysis if diff components fail
            pass
    
    # Fallback to existing configuration changes analysis
    config_changes = item.get('configuration_changes', [])
    for change in config_changes:
        if isinstance(change, dict):
            field = change.get('field', '')
            old_val = change.get('old_value', '')
            new_val = change.get('new_value', '')
            description = change.get('description', '')
            
            # Use the human description if it's detailed enough
            if description and len(description) > 20 and '→' in description:
                return html.escape(description)
            
            # Extract parameter name from various field path formats
            param_name = None
            if field.startswith('parameters.'):
                param_name = field.split('.')[-1]
            elif field.startswith('metadata.'):
                param_name = field.split('.')[-1]
            elif '.' in field:
                param_name = field.split('.')[-1]
            elif field:
                param_name = field
            
            if param_name and old_val != new_val:
                # Format values appropriately
                old_display = _format_value_for_description(old_val)
                new_display = _format_value_for_description(new_val)
                return f'{param_name}: {old_display} → {new_display}'
    
    # Fallback: try to extract from impact description
    impact_desc = item.get('impact_description', '')
    if impact_desc and impact_desc not in ['module configuration updated', 'Configuration updated']:
        return html.escape(impact_desc)
    
    # Final fallback: add context from module name if available
    module_name = item.get('module_name', '')
    if module_name and module_name != 'Unknown' and len(module_name) > 5:
        # Extract meaningful parts from module name for context
        if ' - ' in module_name:
            service_action = module_name.split(' - ', 1)[1]
            if service_action and service_action != module_name:
                return f"Module: {service_action} updated"
    
    return "Configuration: Updated"


def _get_generic_change_description(item: Dict[str, Any]) -> str:
    """Generic standardized change description."""
    config_changes = item.get('configuration_changes', [])
    
    if config_changes and len(config_changes) > 0:
        return "Configuration: Updated"
    
    return "Module: Updated"


def _format_value_for_description(value: any) -> str:
    """Format a value for display in change descriptions."""
    if value is None:
        return "null"
    elif isinstance(value, str):
        if len(value) > 30:
            return f'"{value[:27]}..."'
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