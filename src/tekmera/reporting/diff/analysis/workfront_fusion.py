"""Workfront Fusion-specific module diff analysis.

This module provides Workfront Fusion-specific algorithms for analyzing configuration
changes across different component types (modules, triggers, routers, filters, connections).
"""

from dataclasses import dataclass
from typing import Any, Dict, List

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


def analyze_workfront_fusion_differences(
    old_node: TopologyNode, new_node: TopologyNode
) -> List[FieldChange]:
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

    # Run ALL analyzers independently and accumulate results
    # Each analyzer has specific expertise and should examine every module

    # 1. Connection Analysis - let analyzer determine if there are changes
    from tekmera.functions.components.connections.diff import (
        analyze_connection_differences,
    )

    connection_diffs = analyze_connection_differences(
        old_config, new_config, Platform.WORKFRONT_FUSION
    )

    # Convert ConnectionDifference to FieldChange
    for diff in connection_diffs:
        changes.append(
            FieldChange(
                field_path=diff.field_path,
                old_value=diff.old_value,
                new_value=diff.new_value,
                change_type=diff.change_type,
                significance=diff.significance,
                human_description=diff.description,
            )
        )

    # 2. Filter Analysis - check for filter configuration changes
    from tekmera.functions.components.filters.diff import (
        analyze_filter_differences,
    )

    # For filter nodes, raw_data IS the filter data directly
    # For module nodes, filter data is nested under "filter" key
    if old_node.module_type == "filter" and new_node.module_type == "filter":
        # This is a dedicated filter node - raw_data contains filter config directly
        filter_diffs = analyze_filter_differences(old_config, new_config, Platform.WORKFRONT_FUSION)
    else:
        # This is a module node - check for filter nested inside
        filter_diffs = analyze_filter_differences(
            old_config.get("filter", {}), new_config.get("filter", {}), Platform.WORKFRONT_FUSION
        )

    # Convert FilterDifference to FieldChange
    for diff in filter_diffs:
        changes.append(
            FieldChange(
                field_path=diff.field_path,
                old_value=diff.old_value,
                new_value=diff.new_value,
                change_type=diff.change_type,
                significance=diff.significance,
                human_description=diff.description,
            )
        )

    # 3. Router Analysis - check for routing changes
    from tekmera.functions.components.routers.diff import (
        analyze_router_differences,
    )

    router_diffs = analyze_router_differences(old_config, new_config, Platform.WORKFRONT_FUSION)

    # Convert RouterDifference to FieldChange
    for diff in router_diffs:
        changes.append(
            FieldChange(
                field_path=diff.field_path,
                old_value=diff.old_value,
                new_value=diff.new_value,
                change_type=diff.change_type,
                significance=diff.significance,
                human_description=diff.description,
            )
        )

    # 4. Module Analysis - check for general module configuration changes
    from tekmera.functions.components.modules.diff import (
        analyze_module_differences,
    )

    module_diffs = analyze_module_differences(old_config, new_config, Platform.WORKFRONT_FUSION)

    # Convert ModuleDifference to FieldChange
    for diff in module_diffs:
        changes.append(
            FieldChange(
                field_path=diff.field_path,
                old_value=diff.old_value,
                new_value=diff.new_value,
                change_type=diff.change_type,
                significance=diff.significance,
                human_description=diff.description,
            )
        )

    return changes


def convert_field_changes_to_module_change_format(
    field_changes: List[FieldChange],
) -> List[Dict[str, Any]]:
    """Convert FieldChange objects to the format expected by ModuleChange.configuration_changes."""
    return [
        {
            "field": change.field_path,
            "old_value": change.old_value,
            "new_value": change.new_value,
            "change_type": change.change_type,
            "significance": change.significance,
            "description": change.human_description,
        }
        for change in field_changes
    ]
