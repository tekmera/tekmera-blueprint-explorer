"""Make.com-specific module diff analysis.

This module provides Make.com-specific algorithms for analyzing configuration
changes across different component types (modules, triggers, routers, filters, connections).
"""

from typing import Any, Dict, List
from dataclasses import dataclass

from ..diff import ModuleChange, ChangeType, ChangeImpact
from tekmera.functions.components.topology.types import TopologyNode
from tekmera.functions.meta.types import Platform


@dataclass
class FieldChange:
    """Represents a specific field change within a module configuration."""
    field_path: str  # e.g., "parameters.url" or "metadata.notes"
    old_value: Any
    new_value: Any
    change_type: str  # "added", "removed", "modified"
    significance: str  # "critical", "important", "minor", "cosmetic"
    human_description: str  # Human-readable description of the change


def analyze_make_com_differences(old_node: TopologyNode, new_node: TopologyNode) -> List[FieldChange]:
    """
    Analyze configuration differences for Make.com components.
    
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
    if _has_connection_changes(old_config, new_config):
        # This change involves connection configuration
        from tekmera.functions.components.connections.diff import analyze_connection_differences, ConnectionDifference
        
        # Analyze connection-specific differences
        connection_diffs = analyze_connection_differences(
            old_config, 
            new_config, 
            Platform.MAKE_COM
        )
        
        # Convert ConnectionDifference to FieldChange
        for diff in connection_diffs:
            changes.append(FieldChange(
                field_path=diff.field_path,
                old_value=diff.old_value,
                new_value=diff.new_value,
                change_type=diff.change_type,
                significance=diff.significance,
                human_description=diff.description
            ))
    
    elif old_node.is_filter or new_node.is_filter or "filter" in old_config or "filter" in new_config:
        # This is a filter component
        from tekmera.functions.components.filters.diff import analyze_filter_differences, FilterDifference
        
        # Analyze filter-specific differences
        filter_diffs = analyze_filter_differences(
            old_config.get("filter", {}), 
            new_config.get("filter", {}), 
            Platform.MAKE_COM
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
        from tekmera.functions.components.routers.diff import analyze_router_differences, RouterDifference
        
        # Analyze router-specific differences
        router_diffs = analyze_router_differences(
            old_config, 
            new_config, 
            Platform.MAKE_COM
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
        from tekmera.functions.components.modules.diff import analyze_module_differences, ModuleDifference
        
        # Analyze module-specific differences
        module_diffs = analyze_module_differences(
            old_config, 
            new_config, 
            Platform.MAKE_COM
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


def _has_connection_changes(old_config: Dict[str, Any], new_config: Dict[str, Any]) -> bool:
    """
    Check if the configuration changes involve Make.com connections.
    
    Make.com connections use account-type parameters.
    """
    old_params = old_config.get("parameters", {})
    new_params = new_config.get("parameters", {})
    
    # Get parameter definitions to find connection parameters
    old_meta = old_config.get("metadata", {})
    new_meta = new_config.get("metadata", {})
    old_param_defs = old_meta.get("parameters", [])
    new_param_defs = new_meta.get("parameters", [])
    
    # Find connection parameters in either version
    connection_params = set()
    
    for param_def in old_param_defs + new_param_defs:
        param_name = param_def.get("name", "")
        param_type = param_def.get("type", "")
        
        if param_type.startswith("account:"):
            connection_params.add(param_name)
    
    # Check if any connection parameters have changed
    for param_name in connection_params:
        old_value = old_params.get(param_name)
        new_value = new_params.get(param_name)
        
        if old_value != new_value:
            return True
    
    # Check if connection metadata has changed
    old_restore = old_meta.get("restore", {}).get("parameters", {})
    new_restore = new_meta.get("restore", {}).get("parameters", {})
    
    for param_name in connection_params:
        old_restore_data = old_restore.get(param_name, {})
        new_restore_data = new_restore.get(param_name, {})
        
        if old_restore_data != new_restore_data:
            return True
    
    return False


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