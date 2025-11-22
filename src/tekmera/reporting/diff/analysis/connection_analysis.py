"""Connection-level diff analysis for blueprint-wide insights.

This module analyzes connection changes across an entire blueprint to provide
high-level insights like connection replacements, new connections, and removed connections.
"""

from typing import Any, Dict, List, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict

from ..diff import ModuleChange, ChangeType


@dataclass
class ConnectionReplacement:
    """Represents a connection replacement pattern across multiple modules."""
    old_connection_id: str
    new_connection_id: str
    old_connection_display: str
    new_connection_display: str
    affected_modules: List[Dict[str, str]]  # [{"id": "1", "name": "Data Import"}, ...]
    platform: str
    
    @property
    def module_count(self) -> int:
        return len(self.affected_modules)


@dataclass
class ConnectionSummary:
    """Summary of all connection changes in a blueprint diff."""
    replacements: List[ConnectionReplacement]
    new_connections: List[Dict[str, Any]]  # Modules that got connections for first time
    removed_connections: List[Dict[str, Any]]  # Modules that lost connections
    isolated_changes: List[Dict[str, Any]]  # Individual connection changes that don't fit patterns


def analyze_connection_changes(module_changes: List[ModuleChange], platform: str) -> ConnectionSummary:
    """
    Analyze connection changes across all modules to identify patterns.
    
    Args:
        module_changes: List of all module changes from diff analysis
        platform: Platform name for connection extraction
        
    Returns:
        ConnectionSummary with high-level connection insights
    """
    # Extract connection-related changes
    connection_changes = _extract_connection_changes(module_changes, platform)
    
    # Group changes by connection transition pattern
    replacement_groups = _group_connection_replacements(connection_changes)
    
    # Identify different types of connection changes
    replacements = _create_replacement_summaries(replacement_groups, platform)
    new_connections = _identify_new_connections(connection_changes)
    removed_connections = _identify_removed_connections(connection_changes)
    isolated_changes = _identify_isolated_changes(connection_changes, replacement_groups)
    
    return ConnectionSummary(
        replacements=replacements,
        new_connections=new_connections,
        removed_connections=removed_connections,
        isolated_changes=isolated_changes
    )


def _extract_connection_changes(module_changes: List[ModuleChange], platform: str) -> List[Dict[str, Any]]:
    """Extract modules that have connection-related changes."""
    connection_changes = []
    
    for change in module_changes:
        connection_change = _extract_connection_change_from_module(change, platform)
        if connection_change:
            connection_changes.append(connection_change)
    
    return connection_changes


def _extract_connection_change_from_module(change: ModuleChange, platform: str) -> Dict[str, Any] | None:
    """Extract connection change details from a single module change."""
    # Look for connection-related configuration changes
    config_changes = change.configuration_changes or []
    
    for config_change in config_changes:
        if not isinstance(config_change, dict):
            continue
            
        field = config_change.get('field', '')
        description = config_change.get('description', '')
        
        # Check if this is a connection change based on platform patterns
        is_connection_change = False
        
        if platform.lower() == 'workfront_fusion':
            # Be more specific - only actual connection parameter changes, not URL parameters
            is_connection_change = '__IMTCONN__' in field
        elif platform.lower() == 'make_com':
            is_connection_change = 'account' in field or 'make.com connection changed' in description.lower()
        else:
            is_connection_change = 'connection' in description.lower()
        
        if is_connection_change:
            return {
                'module_id': change.module_id,
                'module_name': change.module_name,
                'module_type': change.module_type,
                'change_type': change.change_type.value,
                'old_connection_id': config_change.get('old_value'),
                'new_connection_id': config_change.get('new_value'),
                'description': description,
                'raw_change': change
            }
    
    return None


def _group_connection_replacements(connection_changes: List[Dict[str, Any]]) -> Dict[Tuple[str, str], List[Dict[str, Any]]]:
    """Group connection changes by (old_id, new_id) transition pattern."""
    replacement_groups = defaultdict(list)
    
    for change in connection_changes:
        old_id = str(change.get('old_connection_id', ''))
        new_id = str(change.get('new_connection_id', ''))
        
        # Only group actual replacements (not additions or removals)
        if old_id and new_id and old_id != new_id:
            replacement_groups[(old_id, new_id)].append(change)
    
    # Only return groups with multiple modules (patterns)
    return {k: v for k, v in replacement_groups.items() if len(v) > 1}


def _create_replacement_summaries(replacement_groups: Dict[Tuple[str, str], List[Dict[str, Any]]], platform: str) -> List[ConnectionReplacement]:
    """Create ConnectionReplacement objects for each replacement pattern."""
    replacements = []
    
    for (old_id, new_id), modules in replacement_groups.items():
        # Extract connection display names from the first module's description
        old_display, new_display = _extract_connection_displays(modules[0]['description'], old_id, new_id)
        
        # Build affected modules list
        affected_modules = []
        for module in modules:
            affected_modules.append({
                'id': module['module_id'],
                'name': module['module_name'],
                'type': module['module_type']
            })
        
        replacements.append(ConnectionReplacement(
            old_connection_id=old_id,
            new_connection_id=new_id,
            old_connection_display=old_display,
            new_connection_display=new_display,
            affected_modules=affected_modules,
            platform=platform
        ))
    
    # Sort by number of affected modules (largest patterns first)
    return sorted(replacements, key=lambda r: r.module_count, reverse=True)


def _extract_connection_displays(description: str, old_id: str, new_id: str) -> Tuple[str, str]:
    """Extract connection display names from change description."""
    # Try to parse connection display names from descriptions like:
    # "Workfront connection changed from 'PROD Connection' (2835) to 'TEST Connection' (3757)"
    
    import re
    
    # Pattern to match quoted connection names with IDs
    pattern = r"from '([^']+)' \((\d+)\) to '([^']+)' \((\d+)\)"
    match = re.search(pattern, description)
    
    if match:
        old_display = match.group(1)
        new_display = match.group(3)
        return old_display, new_display
    
    # Fallback to just IDs
    return old_id, new_id


def _identify_new_connections(connection_changes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identify modules that got connections for the first time."""
    new_connections = []
    
    for change in connection_changes:
        old_id = change.get('old_connection_id')
        new_id = change.get('new_connection_id')
        
        # Connection was added (no old connection)
        if not old_id and new_id:
            new_connections.append({
                'module_id': change['module_id'],
                'module_name': change['module_name'],
                'connection_id': new_id,
                'description': change['description']
            })
    
    return new_connections


def _identify_removed_connections(connection_changes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identify modules that lost their connections."""
    removed_connections = []
    
    for change in connection_changes:
        old_id = change.get('old_connection_id')
        new_id = change.get('new_connection_id')
        
        # Connection was removed (had connection, now doesn't)
        if old_id and not new_id:
            removed_connections.append({
                'module_id': change['module_id'],
                'module_name': change['module_name'],
                'connection_id': old_id,
                'description': change['description']
            })
    
    return removed_connections


def _identify_isolated_changes(connection_changes: List[Dict[str, Any]], replacement_groups: Dict[Tuple[str, str], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Identify connection changes that don't fit replacement patterns."""
    # Get modules that are part of replacement patterns
    grouped_module_ids = set()
    for modules in replacement_groups.values():
        for module in modules:
            grouped_module_ids.add(module['module_id'])
    
    # Find changes not in any replacement pattern
    isolated = []
    for change in connection_changes:
        module_id = change['module_id']
        old_id = change.get('old_connection_id')
        new_id = change.get('new_connection_id')
        
        # Skip if part of replacement pattern, addition, or removal
        if (module_id in grouped_module_ids or 
            not old_id or not new_id):
            continue
            
        isolated.append(change)
    
    return isolated


def format_connection_summary_for_html(summary: ConnectionSummary) -> Dict[str, Any]:
    """Format connection summary for HTML display."""
    return {
        'has_connection_changes': bool(summary.replacements or summary.new_connections or 
                                      summary.removed_connections or summary.isolated_changes),
        'replacements': [
            {
                'old_display': repl.old_connection_display,
                'new_display': repl.new_connection_display,
                'old_connection_id': repl.old_connection_id,
                'new_connection_id': repl.new_connection_id,
                'module_count': repl.module_count,
                'modules': repl.affected_modules
            }
            for repl in summary.replacements
        ],
        'new_connections_count': len(summary.new_connections),
        'removed_connections_count': len(summary.removed_connections),
        'isolated_changes_count': len(summary.isolated_changes),
        'total_connection_changes': (len(summary.replacements) + 
                                   len(summary.new_connections) + 
                                   len(summary.removed_connections) + 
                                   len(summary.isolated_changes))
    }