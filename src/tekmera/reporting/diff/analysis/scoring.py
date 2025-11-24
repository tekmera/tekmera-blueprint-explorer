"""Structural change scoring and risk assessment algorithms.

This module provides algorithms for scoring the magnitude of changes
and assessing the risk level of blueprint modifications.
"""

from typing import Dict, List
import math

from tekmera.functions.components.topology.types import TopologyGraph
from ..diff import ModuleChange, ChangeType, ChangeScale
from .structural import GraphComparisonResult


def calculate_structural_change_score(
    graph1: TopologyGraph, 
    graph2: TopologyGraph, 
    comparison: GraphComparisonResult
) -> float:
    """
    Calculate a structural change score between 0.0 and 1.0.
    
    0.0 = identical graphs
    1.0 = completely different graphs
    
    The score considers:
    - Node additions/removals
    - Position changes (moved modules)
    - Edge changes (connection modifications)
    - Graph complexity changes
    
    Args:
        graph1: Original topology graph
        graph2: Updated topology graph
        comparison: Result of graph comparison
        
    Returns:
        Float between 0.0 and 1.0 representing change magnitude
    """
    if not graph1.nodes and not graph2.nodes:
        return 0.0  # Both graphs empty
    
    # Calculate component scores
    node_change_score = _calculate_node_change_score(graph1, graph2, comparison)
    edge_change_score = _calculate_edge_change_score(graph1, graph2, comparison)
    complexity_change_score = _calculate_complexity_change_score(graph1, graph2)
    
    # Weighted combination of scores
    weights = {
        "nodes": 0.5,      # Node changes are most important
        "edges": 0.3,      # Connection changes are significant
        "complexity": 0.2  # Overall complexity changes
    }
    
    final_score = (
        weights["nodes"] * node_change_score +
        weights["edges"] * edge_change_score +
        weights["complexity"] * complexity_change_score
    )
    
    # Ensure score is between 0.0 and 1.0
    return max(0.0, min(1.0, final_score))


def classify_change_scope(
    change_score: float,
    module_changes: List[ModuleChange],
    comparison: GraphComparisonResult
) -> ChangeScale:
    """
    Classify the scope of changes based on structural differences.
    
    Classification is factual and based on:
    - Percentage of components affected
    - Structural change coverage
    - Distribution of modifications
    
    Args:
        change_score: Structural change score (0.0-1.0)
        module_changes: List of all module changes
        comparison: Graph comparison result
        
    Returns:
        Change scope classification
    """
    # Classification based on change coverage
    if change_score == 0.0:
        return ChangeScale.UNCHANGED
    elif change_score < 0.05:
        return ChangeScale.LIMITED
    elif change_score < 0.10:
        return ChangeScale.MODERATE
    elif change_score < 0.40:
        return ChangeScale.SUBSTANTIAL
    elif change_score < 0.85:
        return ChangeScale.WIDESPREAD
    else:
        return ChangeScale.COMPREHENSIVE


def calculate_structural_similarity(change_score: float) -> float:
    """
    Calculate structural similarity as the inverse of change score.
    
    Args:
        change_score: Structural change score (0.0-1.0)
        
    Returns:
        Structural similarity score (0.0-1.0)
    """
    return 1.0 - change_score


def _calculate_node_change_score(
    graph1: TopologyGraph, 
    graph2: TopologyGraph, 
    comparison: GraphComparisonResult
) -> float:
    """Calculate score based on node additions, removals, and modifications."""
    total_nodes = max(len(graph1.nodes), len(graph2.nodes), 1)
    
    # Weight different types of changes
    added_weight = len(comparison.added_nodes) * 0.6
    removed_weight = len(comparison.removed_nodes) * 0.8  # Removals are more impactful
    modified_weight = len(comparison.modified_nodes) * 0.4
    moved_weight = len(comparison.moved_nodes) * 0.3
    
    total_change_impact = added_weight + removed_weight + modified_weight + moved_weight
    
    # Normalize by total nodes
    score = total_change_impact / total_nodes
    
    # Apply scaling for dramatic changes
    if len(comparison.removed_nodes) > total_nodes * 0.3:  # >30% removed
        score *= 1.5
    
    return min(1.0, score)


def _calculate_edge_change_score(
    graph1: TopologyGraph, 
    graph2: TopologyGraph, 
    comparison: GraphComparisonResult
) -> float:
    """Calculate score based on edge (connection) changes."""
    total_edges = max(len(graph1.edges), len(graph2.edges), 1)
    
    # Edge changes represent connection modifications
    added_edges = comparison.added_edges_count
    removed_edges = comparison.removed_edges_count
    changed_edges = comparison.changed_edges_count
    
    # Calculate proportional change in connections
    edge_change_count = (
        added_edges +
        removed_edges + 
        changed_edges
    )
    
    return min(1.0, edge_change_count / total_edges)


def _calculate_complexity_change_score(graph1: TopologyGraph, graph2: TopologyGraph) -> float:
    """Calculate score based on overall complexity changes."""
    # Get complexity metrics
    metrics1 = _get_complexity_metrics(graph1)
    metrics2 = _get_complexity_metrics(graph2)
    
    # Calculate relative changes in key metrics
    changes = []
    
    for metric in ["node_count", "edge_count", "max_depth", "branch_count"]:
        old_val = metrics1.get(metric, 0)
        new_val = metrics2.get(metric, 0)
        
        if old_val == 0 and new_val == 0:
            continue
        
        if old_val == 0:
            relative_change = 1.0  # New complexity introduced
        else:
            relative_change = abs(new_val - old_val) / old_val
        
        changes.append(relative_change)
    
    # Average the relative changes
    if not changes:
        return 0.0
    
    avg_change = sum(changes) / len(changes)
    
    # Scale complexity changes (they're usually less critical than direct changes)
    return min(1.0, avg_change * 0.5)


def _get_complexity_metrics(graph: TopologyGraph) -> Dict[str, int]:
    """Extract complexity metrics from a topology graph."""
    return {
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "max_depth": graph.max_depth,
        "branch_count": _count_branches(graph),
        "trigger_count": len([n for n in graph.nodes if n.is_trigger]),
        "router_count": len([n for n in graph.nodes if n.is_router])
    }


def _count_branches(graph: TopologyGraph) -> int:
    """Count the number of branches in the topology graph."""
    branch_count = 0
    for node in graph.nodes:
        if node.is_router:
            # Count outgoing edges from router nodes
            outgoing_edges = [e for e in graph.edges if e.source == node.id]
            if len(outgoing_edges) > 1:
                branch_count += len(outgoing_edges) - 1  # Additional branches beyond linear flow
    
    return branch_count


def _analyze_change_factors(
    change_score: float,
    module_changes: List[ModuleChange],
    comparison: GraphComparisonResult
) -> Dict[str, int]:
    """Analyze various change factors from the differences."""
    factors = {
        "configuration_changes": 0,
        "trigger_modules_affected": 0,
        "router_modules_affected": 0,
        "added_modules": len(comparison.added_nodes),
        "removed_modules": len(comparison.removed_nodes),
        "moved_modules": len(comparison.moved_nodes)
    }
    
    # Analyze change type distribution
    for change in module_changes:
        if change.change_type == ChangeType.ADDED:
            factors["added_modules"] += 1
        elif change.change_type == ChangeType.REMOVED:
            factors["removed_modules"] += 1
        elif change.change_type == ChangeType.CONFIGURATION_CHANGED:
            factors["configuration_changes"] += 1
        elif change.change_type == ChangeType.STRUCTURALLY_MOVED:
            factors["moved_modules"] += 1
    
    # Count trigger and router changes (for analysis)
    for change in module_changes:
        if change.change_type != ChangeType.UNCHANGED:
            # Check if it affects key node types
            if "trigger" in change.module_type.lower():
                factors["trigger_modules_affected"] += 1
            elif "router" in change.module_type.lower():
                factors["router_modules_affected"] += 1
    
    return factors


def calculate_change_counts(module_changes: List[ModuleChange]) -> Dict[str, int]:
    """Calculate counts of different change types for summary reporting."""
    counts = {
        "unchanged": 0,
        "configuration_changed": 0,
        "structurally_moved": 0,
        "added": 0,
        "removed": 0
    }
    
    for change in module_changes:
        change_type_key = change.change_type.value
        if change_type_key in counts:
            counts[change_type_key] += 1
    
    return counts