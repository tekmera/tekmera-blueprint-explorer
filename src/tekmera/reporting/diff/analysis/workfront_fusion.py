"""Workfront Fusion-specific module diff analysis.

This module provides Workfront Fusion-specific algorithms for analyzing configuration
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
    # Check for filter components FIRST, before connection analysis
    if old_node.is_filter or new_node.is_filter or "filter" in old_config or "filter" in new_config:
        # This is a filter component
        from tekmera.functions.components.filters.diff import analyze_filter_differences, FilterDifference
        
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
    
    elif (hasattr(old_node, 'is_error_handler') and old_node.is_error_handler) or \
         (hasattr(new_node, 'is_error_handler') and new_node.is_error_handler) or \
         "_error" in str(old_node.id) or "_error" in str(new_node.id):
        # This is an error handler component - like filters, these are properties of modules
        # Skip connection analysis for error handlers since they inherit parent module connections
        pass
    
    elif old_node.is_router or new_node.is_router or "routes" in old_config or "routes" in new_config:
        # This is a router component
        from tekmera.functions.components.routers.diff import analyze_router_differences, RouterDifference
        
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
    
    elif _has_connection_changes(old_config, new_config):
        # This change involves connection configuration
        from tekmera.functions.components.connections.diff import analyze_connection_differences, ConnectionDifference
        
        # Analyze connection-specific differences
        connection_diffs = analyze_connection_differences(
            old_config, 
            new_config, 
            Platform.WORKFRONT_FUSION
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
    
    else:
        # This is a regular module component
        from tekmera.functions.components.modules.diff import analyze_module_differences, ModuleDifference
        
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


def _has_connection_changes(old_config: Dict[str, Any], new_config: Dict[str, Any]) -> bool:
    """
    Check if the configuration changes involve Workfront Fusion connections.
    
    Workfront Fusion connections use __IMTCONN__ parameter.
    """
    old_params = old_config.get("parameters", {})
    new_params = new_config.get("parameters", {})
    
    # Check if __IMTCONN__ parameter exists and has changed
    old_conn = old_params.get("__IMTCONN__")
    new_conn = new_params.get("__IMTCONN__")
    
    if old_conn != new_conn:
        return True
    
    # Check if connection metadata has changed
    old_restore = old_config.get("metadata", {}).get("restore", {}).get("__IMTCONN__", {})
    new_restore = new_config.get("metadata", {}).get("restore", {}).get("__IMTCONN__", {})
    
    if old_restore != new_restore:
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