"""Platform-specific module diff analysis.

This module provides platform-specific algorithms for analyzing configuration
changes across different component types (modules, triggers, routers, filters).
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from ..diff import ModuleChange, ChangeType, ChangeImpact
from tekmera.projections.components.topology.types import TopologyNode
from tekmera.projections.meta.types import Platform


@dataclass
class FieldChange:
    """Represents a specific field change within a module configuration."""
    field_path: str  # e.g., "parameters.url" or "metadata.notes"
    old_value: Any
    new_value: Any
    change_type: str  # "added", "removed", "modified"
    significance: str  # "critical", "important", "minor", "cosmetic"
    human_description: str  # Human-readable description of the change


def analyze_workfront_fusion_differences(old_node: TopologyNode, new_node: TopologyNode) -> List[FieldChange]:
    """
    Analyze configuration differences for Workfront Fusion components.
    
    Routes to component-specific analyzers based on component type.
    
    Args:
        old_node: Original component configuration
        new_node: Updated component configuration
        
    Returns:
        List of detailed field changes with significance assessment
    """
    changes = []
    
    # Get raw configuration data
    old_config = old_node.raw_data
    new_config = new_node.raw_data
    
    # Determine component type and route to specific analyzer
    if old_node.is_filter or new_node.is_filter or "filter" in old_config or "filter" in new_config:
        # This is a filter component
        from tekmera.projections.components.filters.diff import analyze_filter_differences, FilterDifference
        from tekmera.projections.meta.types import Platform
        
        # Analyze filter-specific differences
        filter_diffs = analyze_filter_differences(
            old_config.get("filter", {}), 
            new_config.get("filter", {}), 
            Platform.WORKFRONT_FUSION
        )
        
        # Convert FilterDifference to FieldChange
        for diff in filter_diffs:
            changes.append(FieldChange(
                field_path=diff.field_path,
                old_value=diff.old_value,
                new_value=diff.new_value,
                change_type=diff.change_type,
                significance=diff.significance,
                human_description=diff.description
            ))
    
    elif old_node.is_router or new_node.is_router or "routes" in old_config or "routes" in new_config:
        # This is a router component
        from tekmera.projections.components.routers.diff import analyze_router_differences, RouterDifference
        from tekmera.projections.meta.types import Platform
        
        # Analyze router-specific differences
        router_diffs = analyze_router_differences(
            old_config, 
            new_config, 
            Platform.WORKFRONT_FUSION
        )
        
        # Convert RouterDifference to FieldChange
        for diff in router_diffs:
            changes.append(FieldChange(
                field_path=diff.field_path,
                old_value=diff.old_value,
                new_value=diff.new_value,
                change_type=diff.change_type,
                significance=diff.significance,
                human_description=diff.description
            ))
    
    else:
        # This is a regular module component
        from tekmera.projections.components.modules.diff import analyze_module_differences, ModuleDifference
        from tekmera.projections.meta.types import Platform
        
        # Analyze module-specific differences
        module_diffs = analyze_module_differences(
            old_config, 
            new_config, 
            Platform.WORKFRONT_FUSION
        )
        
        # Convert ModuleDifference to FieldChange
        for diff in module_diffs:
            changes.append(FieldChange(
                field_path=diff.field_path,
                old_value=diff.old_value,
                new_value=diff.new_value,
                change_type=diff.change_type,
                significance=diff.significance,
                human_description=diff.description
            ))
    
    return changes


def analyze_make_com_differences(old_node: TopologyNode, new_node: TopologyNode) -> List[FieldChange]:
    """
    Analyze configuration differences for Make.com modules.
    
    Provides deep analysis tailored to Make.com's blueprint structure
    and configuration patterns.
    
    Args:
        old_node: Original module configuration
        new_node: Updated module configuration
        
    Returns:
        List of detailed field changes with significance assessment
    """
    changes = []
    
    # Get raw configuration data
    old_config = old_node.raw_data
    new_config = new_node.raw_data
    
    # Analyze module type changes
    if old_node.module_type != new_node.module_type:
        changes.append(FieldChange(
            field_path="module",
            old_value=old_node.module_type,
            new_value=new_node.module_type,
            change_type="modified",
            significance="critical",
            human_description=f"Module type changed from {old_node.module_type} to {new_node.module_type}"
        ))
    
    # Analyze Make.com-specific configuration sections
    changes.extend(_analyze_make_parameters(old_config.get("parameters", {}), new_config.get("parameters", {})))
    changes.extend(_analyze_make_settings(old_config.get("settings", {}), new_config.get("settings", {})))
    changes.extend(_analyze_make_connections(old_config.get("connection", {}), new_config.get("connection", {})))
    changes.extend(_analyze_make_filters(old_config.get("filter", {}), new_config.get("filter", {})))
    
    return changes


def _analyze_fusion_parameters(old_params: Dict[str, Any], new_params: Dict[str, Any]) -> List[FieldChange]:
    """Analyze Workfront Fusion parameter changes."""
    changes = []
    
    # Get all unique parameter keys
    all_keys = set(old_params.keys()) | set(new_params.keys())
    
    for key in all_keys:
        old_value = old_params.get(key)
        new_value = new_params.get(key)
        
        if old_value != new_value:
            field_path = f"parameters.{key}"
            
            # Determine change type
            if key not in old_params:
                change_type = "added"
            elif key not in new_params:
                change_type = "removed"
            else:
                change_type = "modified"
            
            # Assess significance based on parameter name and content
            significance = _assess_fusion_parameter_significance(key, old_value, new_value)
            
            # Generate human description
            description = _generate_fusion_parameter_description(key, old_value, new_value, change_type)
            
            changes.append(FieldChange(
                field_path=field_path,
                old_value=old_value,
                new_value=new_value,
                change_type=change_type,
                significance=significance,
                human_description=description
            ))
    
    return changes


def _analyze_fusion_metadata(old_meta: Dict[str, Any], new_meta: Dict[str, Any]) -> List[FieldChange]:
    """Analyze Workfront Fusion metadata changes."""
    changes = []
    
    # Focus on important metadata fields
    important_fields = ["notes", "name", "enabled", "scenario"]
    
    for field in important_fields:
        old_value = old_meta.get(field)
        new_value = new_meta.get(field)
        
        if old_value != new_value:
            field_path = f"metadata.{field}"
            
            if field not in old_meta:
                change_type = "added"
            elif field not in new_meta:
                change_type = "removed"
            else:
                change_type = "modified"
            
            # Metadata changes are typically cosmetic unless it's enabled status
            significance = "critical" if field == "enabled" else "cosmetic"
            
            description = f"Module {field} changed"
            if field == "enabled":
                description = f"Module {'enabled' if new_value else 'disabled'}"
            
            changes.append(FieldChange(
                field_path=field_path,
                old_value=old_value,
                new_value=new_value,
                change_type=change_type,
                significance=significance,
                human_description=description
            ))
    
    return changes


def _analyze_fusion_filters(old_filter: Dict[str, Any], new_filter: Dict[str, Any]) -> List[FieldChange]:
    """Analyze Workfront Fusion filter configuration changes."""
    changes = []
    
    if not old_filter and not new_filter:
        return changes
    
    # Check if filter was added or removed entirely
    if not old_filter and new_filter:
        changes.append(FieldChange(
            field_path="filter",
            old_value=None,
            new_value="filter_added",
            change_type="added",
            significance="important",
            human_description="Filter condition added to module"
        ))
    elif old_filter and not new_filter:
        changes.append(FieldChange(
            field_path="filter",
            old_value="filter_present",
            new_value=None,
            change_type="removed",
            significance="important",
            human_description="Filter condition removed from module"
        ))
    elif old_filter != new_filter:
        changes.append(FieldChange(
            field_path="filter",
            old_value=old_filter,
            new_value=new_filter,
            change_type="modified",
            significance="important",
            human_description="Filter condition logic modified"
        ))
    
    return changes


def _analyze_fusion_routes(old_routes: List[Dict], new_routes: List[Dict]) -> List[FieldChange]:
    """Analyze Workfront Fusion routing changes."""
    changes = []
    
    old_count = len(old_routes) if old_routes else 0
    new_count = len(new_routes) if new_routes else 0
    
    if old_count != new_count:
        changes.append(FieldChange(
            field_path="routes",
            old_value=old_count,
            new_value=new_count,
            change_type="modified",
            significance="critical",
            human_description=f"Router paths changed from {old_count} to {new_count} routes"
        ))
    
    return changes


def _analyze_fusion_error_handlers(old_errors: List[Dict], new_errors: List[Dict]) -> List[FieldChange]:
    """Analyze Workfront Fusion error handler changes."""
    changes = []
    
    old_count = len(old_errors) if old_errors else 0
    new_count = len(new_errors) if new_errors else 0
    
    if old_count != new_count:
        changes.append(FieldChange(
            field_path="onerror",
            old_value=old_count,
            new_value=new_count,
            change_type="modified",
            significance="important",
            human_description=f"Error handlers changed from {old_count} to {new_count} handlers"
        ))
    
    return changes


def _analyze_make_parameters(old_params: Dict[str, Any], new_params: Dict[str, Any]) -> List[FieldChange]:
    """Analyze Make.com parameter changes."""
    changes = []
    
    all_keys = set(old_params.keys()) | set(new_params.keys())
    
    for key in all_keys:
        old_value = old_params.get(key)
        new_value = new_params.get(key)
        
        if old_value != new_value:
            field_path = f"parameters.{key}"
            
            if key not in old_params:
                change_type = "added"
            elif key not in new_params:
                change_type = "removed"
            else:
                change_type = "modified"
            
            significance = _assess_make_parameter_significance(key, old_value, new_value)
            description = _generate_make_parameter_description(key, old_value, new_value, change_type)
            
            changes.append(FieldChange(
                field_path=field_path,
                old_value=old_value,
                new_value=new_value,
                change_type=change_type,
                significance=significance,
                human_description=description
            ))
    
    return changes


def _analyze_make_settings(old_settings: Dict[str, Any], new_settings: Dict[str, Any]) -> List[FieldChange]:
    """Analyze Make.com settings changes."""
    changes = []
    
    # Make.com specific settings analysis
    important_fields = ["enabled", "timeout", "retries", "schedule"]
    
    for field in important_fields:
        old_value = old_settings.get(field)
        new_value = new_settings.get(field)
        
        if old_value != new_value:
            field_path = f"settings.{field}"
            
            if field not in old_settings:
                change_type = "added"
            elif field not in new_settings:
                change_type = "removed"
            else:
                change_type = "modified"
            
            significance = "critical" if field in ["enabled", "schedule"] else "minor"
            description = f"Module {field} setting changed"
            
            changes.append(FieldChange(
                field_path=field_path,
                old_value=old_value,
                new_value=new_value,
                change_type=change_type,
                significance=significance,
                human_description=description
            ))
    
    return changes


def _analyze_make_connections(old_conn: Dict[str, Any], new_conn: Dict[str, Any]) -> List[FieldChange]:
    """Analyze Make.com connection changes."""
    changes = []
    
    if old_conn != new_conn:
        changes.append(FieldChange(
            field_path="connection",
            old_value=old_conn.get("name", "unknown"),
            new_value=new_conn.get("name", "unknown"),
            change_type="modified",
            significance="critical",
            human_description="Connection configuration changed"
        ))
    
    return changes


def _analyze_make_filters(old_filter: Dict[str, Any], new_filter: Dict[str, Any]) -> List[FieldChange]:
    """Analyze Make.com filter configuration changes."""
    changes = []
    
    if not old_filter and not new_filter:
        return changes
    
    if not old_filter and new_filter:
        changes.append(FieldChange(
            field_path="filter",
            old_value=None,
            new_value="filter_added",
            change_type="added",
            significance="important",
            human_description="Filter condition added to module"
        ))
    elif old_filter and not new_filter:
        changes.append(FieldChange(
            field_path="filter",
            old_value="filter_present",
            new_value=None,
            change_type="removed",
            significance="important",
            human_description="Filter condition removed from module"
        ))
    elif old_filter != new_filter:
        changes.append(FieldChange(
            field_path="filter",
            old_value=old_filter,
            new_value=new_filter,
            change_type="modified",
            significance="important",
            human_description="Filter condition logic modified"
        ))
    
    return changes


def _assess_fusion_parameter_significance(param_name: str, old_value: Any, new_value: Any) -> str:
    """Assess the significance of a Workfront Fusion parameter change."""
    param_lower = param_name.lower()
    
    # Critical changes that can break functionality
    if param_lower in ["url", "endpoint", "method", "connection", "objecttype", "recordtype"]:
        return "critical"
    
    # Important changes that affect behavior
    elif param_lower in ["filter", "limit", "outputfields", "fields", "query", "search"]:
        return "important"
    
    # Minor changes in configuration
    elif param_lower in ["name", "notes", "description", "label"]:
        return "cosmetic"
    
    # Default to minor for unknown parameters
    else:
        return "minor"


def _assess_make_parameter_significance(param_name: str, old_value: Any, new_value: Any) -> str:
    """Assess the significance of a Make.com parameter change."""
    param_lower = param_name.lower()
    
    # Critical changes
    if param_lower in ["url", "endpoint", "method", "connection", "type"]:
        return "critical"
    
    # Important changes
    elif param_lower in ["filter", "limit", "fields", "query", "body", "headers"]:
        return "important"
    
    # Cosmetic changes
    elif param_lower in ["name", "label", "description"]:
        return "cosmetic"
    
    else:
        return "minor"


def _generate_fusion_parameter_description(param_name: str, old_value: Any, new_value: Any, change_type: str) -> str:
    """Generate human-readable description for Fusion parameter changes."""
    if change_type == "added":
        return f"Parameter '{param_name}' added with value: {_format_value_for_display(new_value)}"
    elif change_type == "removed":
        return f"Parameter '{param_name}' removed (was: {_format_value_for_display(old_value)})"
    else:
        return f"Parameter '{param_name}' changed from {_format_value_for_display(old_value)} to {_format_value_for_display(new_value)}"


def _generate_make_parameter_description(param_name: str, old_value: Any, new_value: Any, change_type: str) -> str:
    """Generate human-readable description for Make.com parameter changes."""
    if change_type == "added":
        return f"Parameter '{param_name}' added with value: {_format_value_for_display(new_value)}"
    elif change_type == "removed":
        return f"Parameter '{param_name}' removed (was: {_format_value_for_display(old_value)})"
    else:
        return f"Parameter '{param_name}' changed from {_format_value_for_display(old_value)} to {_format_value_for_display(new_value)}"


def _format_value_for_display(value: Any) -> str:
    """Format a value for human-readable display."""
    if value is None:
        return "None"
    elif isinstance(value, str):
        if len(value) > 50:
            return f"'{value[:47]}...'"
        return f"'{value}'"
    elif isinstance(value, (dict, list)):
        return f"{type(value).__name__} with {len(value)} items"
    else:
        return str(value)


def get_platform_specific_analyzer(platform: Platform):
    """Get the appropriate platform-specific analyzer function."""
    if platform == Platform.WORKFRONT_FUSION:
        return analyze_workfront_fusion_differences
    elif platform == Platform.MAKE_COM:
        return analyze_make_com_differences
    else:
        # Fallback to generic analysis
        return analyze_workfront_fusion_differences


def convert_field_changes_to_module_change_format(field_changes: List[FieldChange]) -> List[Dict[str, Any]]:
    """Convert FieldChange objects to the format expected by ModuleChange.configuration_changes."""
    return [
        {
            "field": change.field_path,
            "old_value": change.old_value,
            "new_value": change.new_value,
            "change_type": change.change_type,
            "significance": change.significance,
            "description": change.human_description
        }
        for change in field_changes
    ]