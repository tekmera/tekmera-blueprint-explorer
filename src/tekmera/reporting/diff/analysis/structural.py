"""Structural graph comparison algorithms.

This module provides platform-agnostic algorithms for comparing topology graphs
and detecting additions, removals, and structural changes.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

from tekmera.functions.components.topology.types import TopologyGraph, TopologyNode

from ..descriptions import generate_component_addition_description
from ..diff import ChangeType, ModuleChange


@dataclass
class GraphComparisonResult:
    """Result of comparing two topology graphs."""

    added_nodes: List[TopologyNode]
    removed_nodes: List[TopologyNode]
    unchanged_nodes: List[Tuple[TopologyNode, TopologyNode]]  # (old, new) pairs
    modified_nodes: List[Tuple[TopologyNode, TopologyNode]]  # (old, new) pairs with changes
    moved_nodes: List[Tuple[TopologyNode, TopologyNode]]  # (old, new) pairs that moved position

    added_edges_count: int
    removed_edges_count: int
    changed_edges_count: int


def compare_graphs(graph1: TopologyGraph, graph2: TopologyGraph) -> GraphComparisonResult:
    """
    Compare two topology graphs and detect all structural changes.

    This is the main entry point for graph comparison. It performs:
    1. Node matching between graphs (handles ID changes)
    2. Classification of nodes as added/removed/unchanged/modified/moved
    3. Edge comparison for connection changes

    Args:
        graph1: The original/before topology graph
        graph2: The updated/after topology graph

    Returns:
        Detailed comparison result with categorized changes
    """
    # Step 1: Match nodes between graphs using multiple strategies
    node_matches = _match_nodes_between_graphs(graph1, graph2)
    
    # Step 2: Classify nodes based on matching results
    added_nodes = []
    removed_nodes = []
    unchanged_nodes = []
    modified_nodes = []
    moved_nodes = []

    # Find nodes that exist in graph2 but not in graph1 (added)
    matched_ids_graph2 = {match[1].id for match in node_matches if match[1] is not None}
    for node in graph2.nodes:
        if node.id not in matched_ids_graph2:
            added_nodes.append(node)
    
    # Find nodes that exist in graph1 but not in graph2 (removed)
    matched_ids_graph1 = {match[0].id for match in node_matches if match[0] is not None}
    for node in graph1.nodes:
        if node.id not in matched_ids_graph1:
            removed_nodes.append(node)
    count = 1
    # Analyze matched nodes for changes
    for old_node, new_node in node_matches:
        if old_node is None or new_node is None:
            continue
        
        # Check if node configuration changed
        config_changed = _has_configuration_changed(old_node, new_node)
        
        # Check if node moved position in the flow
        position_changed = _has_position_changed(old_node, new_node)

        if config_changed and position_changed:
            modified_nodes.append((old_node, new_node))
        elif config_changed:
            modified_nodes.append((old_node, new_node))
        elif position_changed:
            moved_nodes.append((old_node, new_node))
        else:
            unchanged_nodes.append((old_node, new_node))

    # Step 3: Analyze edge changes
    edge_changes = _compare_edges(graph1, graph2)
   
    return GraphComparisonResult(
        added_nodes=added_nodes,
        removed_nodes=removed_nodes,
        unchanged_nodes=unchanged_nodes,
        modified_nodes=modified_nodes,
        moved_nodes=moved_nodes,
        added_edges_count=edge_changes["added"],
        removed_edges_count=edge_changes["removed"],
        changed_edges_count=edge_changes["changed"],
    )


def detect_node_changes(comparison: GraphComparisonResult) -> List[ModuleChange]:
    """
    Convert graph comparison results into ModuleChange objects.

    This transforms the low-level graph comparison into the structured
    ModuleChange format used in diff reports.

    Args:
        comparison: Result from compare_graphs()

    Returns:
        List of ModuleChange objects describing each change
    """
    changes = []

    # Process added nodes
    for node in comparison.added_nodes:
        # Extract component metadata for filters
        component_metadata = None
        if node.is_filter and "source_router_id" in node.raw_data:
            component_metadata = {"source_router_id": node.raw_data.get("source_router_id")}
        elif node.is_filter and hasattr(node.raw_data, "source_router_id"):
            component_metadata = {"source_router_id": getattr(node.raw_data, "source_router_id")}

        change = ModuleChange(
            module_id=node.id,
            module_type=node.module_type,
            module_name=node.name,
            change_type=ChangeType.ADDED,
            description=generate_component_addition_description(node),
            component_metadata=component_metadata,
            raw_data=node.raw_data,
        )
        changes.append(change)

    # Process removed nodes
    for node in comparison.removed_nodes:
        # Extract component metadata for filters
        component_metadata = None
        if node.is_filter and "source_router_id" in node.raw_data:
            component_metadata = {"source_router_id": node.raw_data.get("source_router_id")}
        elif node.is_filter and hasattr(node.raw_data, "source_router_id"):
            component_metadata = {"source_router_id": getattr(node.raw_data, "source_router_id")}

        change = ModuleChange(
            module_id=node.id,
            module_type=node.module_type,
            module_name=node.name,
            change_type=ChangeType.REMOVED,
            description=f"{_get_node_type_description(node)} removed from workflow",
            component_metadata=component_metadata,
            raw_data=node.raw_data,
        )
        changes.append(change)

    # Process modified nodes
    for old_node, new_node in comparison.modified_nodes:
        config_changes = _analyze_configuration_changes(old_node, new_node)
        # Extract component metadata for filters
        component_metadata = None
        if new_node.is_filter and "source_router_id" in new_node.raw_data:
            component_metadata = {"source_router_id": new_node.raw_data.get("source_router_id")}
        elif new_node.is_filter and hasattr(new_node.raw_data, "source_router_id"):
            component_metadata = {
                "source_router_id": getattr(new_node.raw_data, "source_router_id")
            }
            
        change = ModuleChange(
            module_id=new_node.id,
            module_type=new_node.module_type,
            module_name=new_node.name,
            change_type=ChangeType.CONFIGURATION_CHANGED,
            configuration_changes=config_changes,
            description=f"{_get_node_type_description(new_node)} configuration updated",
            component_metadata=component_metadata,
            raw_data=new_node.raw_data,
            raw_data_before=old_node.raw_data,
        )
        changes.append(change)

    # Process moved nodes
    for old_node, new_node in comparison.moved_nodes:
        # Extract component metadata for filters
        component_metadata = None
        if new_node.is_filter and "source_router_id" in new_node.raw_data:
            component_metadata = {"source_router_id": new_node.raw_data.get("source_router_id")}
        elif new_node.is_filter and hasattr(new_node.raw_data, "source_router_id"):
            component_metadata = {
                "source_router_id": getattr(new_node.raw_data, "source_router_id")
            }

        change = ModuleChange(
            module_id=new_node.id,
            module_type=new_node.module_type,
            module_name=new_node.name,
            change_type=ChangeType.STRUCTURALLY_MOVED,
            old_position={"path": old_node.position.path, "depth": old_node.position.depth},
            new_position={"path": new_node.position.path, "depth": new_node.position.depth},
            description=f"{_get_node_type_description(new_node)} moved in workflow structure",
            component_metadata=component_metadata,
            raw_data=new_node.raw_data,
            raw_data_before=old_node.raw_data,
        )
        changes.append(change)

    # Process unchanged nodes
    for old_node, new_node in comparison.unchanged_nodes:
        # Extract component metadata for filters
        component_metadata = None
        if new_node.is_filter and "source_router_id" in new_node.raw_data:
            component_metadata = {"source_router_id": new_node.raw_data.get("source_router_id")}
        elif new_node.is_filter and hasattr(new_node.raw_data, "source_router_id"):
            component_metadata = {
                "source_router_id": getattr(new_node.raw_data, "source_router_id")
            }

        change = ModuleChange(
            module_id=new_node.id,
            module_type=new_node.module_type,
            module_name=new_node.name,
            change_type=ChangeType.UNCHANGED,
            description="No changes detected",
            component_metadata=component_metadata,
            raw_data=new_node.raw_data,
        )
        changes.append(change)

    return changes


def _match_nodes_between_graphs(
    graph1: TopologyGraph, graph2: TopologyGraph
) -> List[Tuple[TopologyNode, TopologyNode]]:
    """
    Match nodes between two graphs using multiple strategies.

    Strategies used in order:
    1. Exact ID matching
    2. Module type + position matching
    3. Module type + name matching (fuzzy)

    Returns:
        List of (old_node, new_node) tuples. Either element can be None for unmatched nodes.
    """
    matches = []
    used_graph1_ids = set()
    used_graph2_ids = set()

    # Strategy 1: Exact ID matching
    graph1_by_id = {node.id: node for node in graph1.nodes}
    graph2_by_id = {node.id: node for node in graph2.nodes}

    for node_id in graph1_by_id:
        if node_id in graph2_by_id:
            matches.append((graph1_by_id[node_id], graph2_by_id[node_id]))
            used_graph1_ids.add(node_id)
            used_graph2_ids.add(node_id)
    
    # Strategy 2: Module type + position matching for unmatched nodes
    remaining_graph1 = [node for node in graph1.nodes if node.id not in used_graph1_ids]
    remaining_graph2 = [node for node in graph2.nodes if node.id not in used_graph2_ids]

    for node1 in remaining_graph1[:]:
        best_match = None
        best_score = 0

        for node2 in remaining_graph2:
            if node2.id in used_graph2_ids:
                continue

            # Score based on module type and position similarity
            score = 0
            if node1.module_type == node2.module_type:
                score += 50
            if node1.position.path == node2.position.path:
                score += 30
            if abs(node1.position.depth - node2.position.depth) <= 1:
                score += 10
            if node1.name == node2.name:
                score += 10

            if score > best_score and score >= 60:  # Minimum threshold
                best_match = node2
                best_score = score

        if best_match:
            matches.append((node1, best_match))
            remaining_graph1.remove(node1)
            used_graph2_ids.add(best_match.id)
    return matches


def _has_configuration_changed(node1: TopologyNode, node2: TopologyNode) -> bool:
    """Check if two matched nodes have configuration changes."""
    # Compare module types
    
    if node1.module_type != node2.module_type:
        return True
    
    # Compare node classifications
    if (
        node1.is_trigger != node2.is_trigger
        or node1.is_router != node2.is_router
        or node1.is_filter != node2.is_filter
        or node1.is_error_handler != node2.is_error_handler
    ):
        return True
    
    # Compare raw data (excluding position/metadata changes)
    raw1 = node1.raw_data.copy()
    raw2 = node2.raw_data.copy()
    
    # Remove position-related metadata
    for data in [raw1, raw2]:
        data.pop("_extraction_context", None)
        if "metadata" in data:
            metadata = data["metadata"]
            metadata.pop("designer", None)
            
        # Remove route info if is a router (router config hasn't changed)
        if data.get("module", None) == "builtin:BasicRouter":
            data.pop("routes", None)
    
    return raw1 != raw2


def _has_position_changed(node1: TopologyNode, node2: TopologyNode) -> bool:
    """Check if two matched nodes have moved positions."""
    return (
        node1.position.path != node2.position.path or node1.position.depth != node2.position.depth
    )


def _compare_edges(graph1: TopologyGraph, graph2: TopologyGraph) -> Dict[str, int]:
    """Compare edges between two graphs and count changes."""
    # Create edge signatures for comparison
    edges1 = {_edge_signature(edge) for edge in graph1.edges}
    edges2 = {_edge_signature(edge) for edge in graph2.edges}

    added = len(edges2 - edges1)
    removed = len(edges1 - edges2)

    # For changed edges, we need to look at edges with same source/target but different properties
    changed = 0
    # This is a simplified version - a more sophisticated implementation would
    # track edges that have same endpoints but different properties

    return {"added": added, "removed": removed, "changed": changed}


def _edge_signature(edge) -> str:
    """Create a signature string for edge comparison."""
    return f"{edge.source}->{edge.target}:{edge.edge_type.value}"


def _get_node_type_description(node: TopologyNode) -> str:
    """Get a human-readable description of a node's type."""
    if node.is_trigger:
        return "trigger"
    elif node.is_router:
        return "router"
    elif node.is_filter:
        return "filter"
    elif node.is_error_handler:
        return "error handler"
    else:
        return "module"


def _analyze_configuration_changes(
    old_node: TopologyNode, new_node: TopologyNode
) -> List[Dict[str, any]]:
    """Analyze specific configuration changes between two nodes."""
    from tekmera.functions.meta.types import Platform

    # Determine platform from node metadata
    platform = old_node.platform if hasattr(old_node, "platform") else new_node.platform

    # Route to platform-specific analyzer
    if platform == Platform.WORKFRONT_FUSION:
        from .workfront_fusion import (
            analyze_workfront_fusion_differences,
            convert_field_changes_to_module_change_format,
        )

        field_changes = analyze_workfront_fusion_differences(old_node, new_node)
        return convert_field_changes_to_module_change_format(field_changes)
    elif platform == Platform.MAKE_COM:
        from .make_com import (
            analyze_make_com_differences,
            convert_field_changes_to_module_change_format,
        )

        field_changes = analyze_make_com_differences(old_node, new_node)
        return convert_field_changes_to_module_change_format(field_changes)
    else:
        # Fallback to basic comparison for unknown platforms
        return _compare_dict_fields(old_node.raw_data, new_node.raw_data)


def _compare_dict_fields(
    old_dict: Dict[str, any], new_dict: Dict[str, any], prefix: str = "", max_depth: int = 3
) -> List[Dict[str, any]]:
    """
    Compare two dictionaries and return a list of field changes.

    Args:
        old_dict: Original configuration dict
        new_dict: Updated configuration dict
        prefix: Field name prefix for nested objects
        max_depth: Maximum recursion depth to prevent infinite loops

    Returns:
        List of change dictionaries with field, old_value, new_value
    """
    changes = []

    if max_depth <= 0:
        return changes

    # Get all unique keys from both dicts
    all_keys = set(old_dict.keys()) | set(new_dict.keys())

    for key in all_keys:
        field_name = f"{prefix}.{key}" if prefix else key

        # Skip certain fields that are typically not user-configurable
        if key in ["id", "order", "_id", "metadata", "created", "updated", "position"]:
            continue

        old_value = old_dict.get(key)
        new_value = new_dict.get(key)

        if old_value != new_value:
            # Handle nested dictionaries
            if isinstance(old_value, dict) and isinstance(new_value, dict):
                nested_changes = _compare_dict_fields(
                    old_value, new_value, field_name, max_depth - 1
                )
                changes.extend(nested_changes)
            else:
                # Convert values to strings for display, handle None values
                old_str = str(old_value) if old_value is not None else "None"
                new_str = str(new_value) if new_value is not None else "None"

                # Only include meaningful changes (skip very long values)
                if len(old_str) < 100 and len(new_str) < 100:
                    changes.append(
                        {
                            "field": field_name,
                            "old_value": old_str,
                            "new_value": new_str,
                            "change_type": "modified",
                        }
                    )

    return changes
