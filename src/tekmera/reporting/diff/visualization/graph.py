"""Topology graph visualization for diff reports.

This module provides ASCII-style graph rendering to visualize blueprint
topology changes in text-based diff reports.
"""

from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

from tekmera.functions.components.topology.types import TopologyGraph, TopologyNode, EdgeType
from ..analysis.structural import GraphComparisonResult


@dataclass
class GraphVisualizationConfig:
    """Configuration for graph visualization rendering."""
    max_width: int = 80
    max_nodes_per_level: int = 8
    show_node_ids: bool = True
    show_edge_types: bool = False
    highlight_changes: bool = True
    compact_mode: bool = False


def render_topology_comparison(
    graph1: TopologyGraph, 
    graph2: TopologyGraph, 
    comparison: GraphComparisonResult,
    config: GraphVisualizationConfig = None
) -> str:
    """
    Render a side-by-side comparison of two topology graphs.
    
    Shows before/after graphs with change highlights to visualize
    structural differences.
    
    Args:
        graph1: Original topology graph
        graph2: Updated topology graph  
        comparison: Graph comparison results
        config: Visualization configuration options
        
    Returns:
        Formatted ASCII visualization of the topology comparison
    """
    if config is None:
        config = GraphVisualizationConfig()
    
    lines = []
    
    # Header
    lines.append("TOPOLOGY COMPARISON")
    lines.append("=" * 60)
    lines.append("")
    
    # Summary statistics
    lines.extend(_render_topology_stats_comparison(graph1, graph2))
    lines.append("")
    
    # Side-by-side graphs (simplified for now)
    if config.compact_mode or (len(graph1.nodes) > 20 and len(graph2.nodes) > 20):
        # For large graphs, show simplified representation
        lines.extend(_render_compact_comparison(graph1, graph2, comparison, config))
    else:
        # For smaller graphs, show detailed structure
        lines.extend(_render_detailed_comparison(graph1, graph2, comparison, config))
    
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def render_topology_ascii(
    graph: TopologyGraph,
    title: str = "Topology Graph",
    config: GraphVisualizationConfig = None
) -> str:
    """
    Render a single topology graph as ASCII art.
    
    Creates a visual representation of the workflow structure showing
    nodes, connections, and flow hierarchy.
    
    Args:
        graph: Topology graph to visualize
        title: Title for the graph visualization
        config: Visualization configuration options
        
    Returns:
        Formatted ASCII representation of the topology graph
    """
    if config is None:
        config = GraphVisualizationConfig()
    
    lines = []
    
    # Header
    lines.append(title)
    lines.append("=" * len(title))
    lines.append("")
    
    if not graph.nodes:
        lines.append("(Empty graph)")
        return "\\n".join(lines)
    
    # Build graph structure
    graph_structure = _build_graph_structure(graph)
    
    # Render based on complexity
    if len(graph.nodes) > config.max_nodes_per_level * 3:
        lines.extend(_render_simplified_graph(graph, graph_structure, config))
    else:
        lines.extend(_render_detailed_graph(graph, graph_structure, config))
    
    return "\n".join(lines)


def _render_topology_stats_comparison(graph1: TopologyGraph, graph2: TopologyGraph) -> List[str]:
    """Render comparison statistics for two graphs."""
    lines = []
    
    lines.append("Graph Statistics Comparison:")
    lines.append(f"  Nodes:        {len(graph1.nodes):4d} → {len(graph2.nodes):4d}  (Δ {len(graph2.nodes) - len(graph1.nodes):+d})")
    lines.append(f"  Edges:        {len(graph1.edges):4d} → {len(graph2.edges):4d}  (Δ {len(graph2.edges) - len(graph1.edges):+d})")
    lines.append(f"  Max Depth:    {graph1.max_depth:4d} → {graph2.max_depth:4d}  (Δ {graph2.max_depth - graph1.max_depth:+d})")
    lines.append(f"  Branches:     {graph1.branch_count:4d} → {graph2.branch_count:4d}  (Δ {graph2.branch_count - graph1.branch_count:+d})")
    lines.append(f"  Entry Points: {len(graph1.entry_points):4d} → {len(graph2.entry_points):4d}  (Δ {len(graph2.entry_points) - len(graph1.entry_points):+d})")
    
    return lines


def _render_compact_comparison(
    graph1: TopologyGraph, 
    graph2: TopologyGraph, 
    comparison: GraphComparisonResult,
    config: GraphVisualizationConfig
) -> List[str]:
    """Render a compact comparison for large graphs."""
    lines = []
    
    lines.append("Compact Graph Overview:")
    lines.append("")
    
    # Before graph summary
    lines.append("BEFORE:")
    lines.extend(_render_compact_graph_summary(graph1, "  "))
    lines.append("")
    
    # After graph summary  
    lines.append("AFTER:")
    lines.extend(_render_compact_graph_summary(graph2, "  "))
    lines.append("")
    
    # Change highlights
    if comparison.added_nodes or comparison.removed_nodes:
        lines.append("KEY CHANGES:")
        if comparison.added_nodes:
            lines.append(f"  + {len(comparison.added_nodes)} nodes added")
            for node in comparison.added_nodes[:3]:  # Show first 3
                lines.append(f"    + {node.name} ({_get_node_type_symbol(node)})")
            if len(comparison.added_nodes) > 3:
                lines.append(f"    + ... and {len(comparison.added_nodes) - 3} more")
        
        if comparison.removed_nodes:
            lines.append(f"  - {len(comparison.removed_nodes)} nodes removed")
            for node in comparison.removed_nodes[:3]:  # Show first 3
                lines.append(f"    - {node.name} ({_get_node_type_symbol(node)})")
            if len(comparison.removed_nodes) > 3:
                lines.append(f"    - ... and {len(comparison.removed_nodes) - 3} more")
    
    return lines


def _render_detailed_comparison(
    graph1: TopologyGraph, 
    graph2: TopologyGraph, 
    comparison: GraphComparisonResult,
    config: GraphVisualizationConfig
) -> List[str]:
    """Render a detailed side-by-side comparison."""
    lines = []
    
    lines.append("Visual Graph Comparison:")
    lines.append("")
    
    # Create visual node grid representations
    visual_grid1 = _create_visual_node_grid(graph1, comparison, "before")
    visual_grid2 = _create_visual_node_grid(graph2, comparison, "after")
    
    # Render side by side
    max_lines = max(len(visual_grid1), len(visual_grid2))
    
    lines.append("BEFORE                    │ AFTER")
    lines.append("─" * 25 + "┼" + "─" * 25)
    
    for i in range(max_lines):
        left = visual_grid1[i] if i < len(visual_grid1) else ""
        right = visual_grid2[i] if i < len(visual_grid2) else ""
        
        lines.append(f"{left:25s} │ {right}")
        
    # Add legend
    lines.append("")
    lines.append("Legend:")
    lines.append("🔵 Unchanged  🟢 Added  🔴 Removed  🟡 Modified  🟠 Moved")
    
    return lines


def _render_compact_graph_summary(graph: TopologyGraph, indent: str = "") -> List[str]:
    """Render a compact summary of graph structure."""
    lines = []
    
    # Count node types
    node_counts = {}
    for node in graph.nodes:
        node_type = _get_node_type_name(node)
        node_counts[node_type] = node_counts.get(node_type, 0) + 1
    
    # Show node type distribution
    for node_type, count in sorted(node_counts.items()):
        lines.append(f"{indent}{count:3d} {node_type}{'s' if count != 1 else ''}")
    
    # Show flow characteristics
    if graph.entry_points:
        entry_types = []
        for entry_id in graph.entry_points:
            entry_node = next((n for n in graph.nodes if n.id == entry_id), None)
            if entry_node:
                entry_types.append(_get_node_type_symbol(entry_node))
        lines.append(f"{indent}Entry: {', '.join(entry_types)}")
    
    return lines


def _build_simplified_flow(graph: TopologyGraph, config: GraphVisualizationConfig) -> List[str]:
    """Build a simplified textual representation of the graph flow."""
    lines = []
    
    if not graph.nodes:
        return ["(empty)"]
    
    # Start from entry points
    processed = set()
    
    for entry_id in graph.entry_points[:3]:  # Limit to first 3 entry points
        entry_node = next((n for n in graph.nodes if n.id == entry_id), None)
        if entry_node and entry_node.id not in processed:
            flow_lines = _trace_flow_from_node(graph, entry_node, processed, config, depth=0)
            lines.extend(flow_lines)
    
    # Handle any remaining unprocessed nodes
    remaining = [n for n in graph.nodes if n.id not in processed]
    if remaining and len(lines) < 15:  # Don't show if already too long
        lines.append("...")
        for node in remaining[:2]:
            lines.append(f"○ {_format_node_compact(node)}")
    
    return lines[:15]  # Limit total lines


def _trace_flow_from_node(
    graph: TopologyGraph, 
    node: TopologyNode, 
    processed: Set[str], 
    config: GraphVisualizationConfig,
    depth: int = 0
) -> List[str]:
    """Trace the flow from a given node."""
    lines = []
    indent = "  " * min(depth, 4)  # Limit indentation
    
    if node.id in processed or depth > 6:  # Prevent infinite loops and deep nesting
        return lines
    
    processed.add(node.id)
    
    # Show current node
    symbol = _get_node_type_symbol(node)
    lines.append(f"{indent}{symbol} {_format_node_compact(node)}")
    
    # Find outgoing edges
    outgoing_edges = [e for e in graph.edges if e.source == node.id]
    
    # Limit branches to avoid explosion
    if len(outgoing_edges) > 3:
        lines.append(f"{indent}  └─ ... {len(outgoing_edges)} branches")
        return lines
    
    # Follow connections
    for edge in outgoing_edges[:2]:  # Limit to 2 connections per node
        target_node = next((n for n in graph.nodes if n.id == edge.target), None)
        if target_node:
            edge_symbol = "├─" if edge != outgoing_edges[-1] else "└─"
            if edge.edge_type == EdgeType.ROUTER_BRANCH:
                edge_symbol += "┬"
            elif edge.edge_type == EdgeType.ERROR_HANDLER:
                edge_symbol += "⚠"
            else:
                edge_symbol += "─"
            
            lines.append(f"{indent}  {edge_symbol}")
            child_lines = _trace_flow_from_node(graph, target_node, processed, config, depth + 1)
            lines.extend(child_lines)
    
    return lines


def _build_graph_structure(graph: TopologyGraph) -> Dict[str, any]:
    """Build a structure representation of the graph for rendering."""
    return {
        "nodes_by_depth": _group_nodes_by_depth(graph),
        "adjacency": _build_adjacency_lists(graph),
        "entry_points": graph.entry_points
    }


def _group_nodes_by_depth(graph: TopologyGraph) -> Dict[int, List[TopologyNode]]:
    """Group nodes by their depth level."""
    by_depth = {}
    for node in graph.nodes:
        depth = node.position.depth
        if depth not in by_depth:
            by_depth[depth] = []
        by_depth[depth].append(node)
    return by_depth


def _build_adjacency_lists(graph: TopologyGraph) -> Dict[str, List[str]]:
    """Build adjacency lists for the graph."""
    adjacency = {}
    for edge in graph.edges:
        if edge.source not in adjacency:
            adjacency[edge.source] = []
        adjacency[edge.source].append(edge.target)
    return adjacency


def _render_simplified_graph(
    graph: TopologyGraph, 
    structure: Dict[str, any], 
    config: GraphVisualizationConfig
) -> List[str]:
    """Render a simplified view for large graphs."""
    lines = []
    
    lines.append(f"Large graph with {len(graph.nodes)} nodes - showing simplified view:")
    lines.append("")
    
    # Show entry points
    lines.append("Entry Points:")
    for entry_id in graph.entry_points[:5]:
        entry_node = next((n for n in graph.nodes if n.id == entry_id), None)
        if entry_node:
            symbol = _get_node_type_symbol(entry_node)
            lines.append(f"  {symbol} {_format_node_compact(entry_node)}")
    
    if len(graph.entry_points) > 5:
        lines.append(f"  ... and {len(graph.entry_points) - 5} more")
    
    # Show depth distribution
    by_depth = structure["nodes_by_depth"]
    if by_depth:
        lines.append("")
        lines.append("Flow Depth Distribution:")
        for depth in sorted(by_depth.keys())[:8]:
            count = len(by_depth[depth])
            lines.append(f"  Level {depth}: {count} nodes")
    
    return lines


def _render_detailed_graph(
    graph: TopologyGraph, 
    structure: Dict[str, any], 
    config: GraphVisualizationConfig
) -> List[str]:
    """Render a detailed view for smaller graphs."""
    lines = []
    
    # Show flow structure
    processed = set()
    for entry_id in graph.entry_points:
        entry_node = next((n for n in graph.nodes if n.id == entry_id), None)
        if entry_node and entry_node.id not in processed:
            flow_lines = _trace_flow_from_node(graph, entry_node, processed, config)
            lines.extend(flow_lines)
            lines.append("")
    
    return lines


def _get_node_type_symbol(node: TopologyNode) -> str:
    """Get a symbol representing the node type."""
    if node.is_trigger:
        return "►"
    elif node.is_router:
        return "◆"
    elif node.is_filter:
        return "◊"
    elif node.is_error_handler:
        return "⚠"
    else:
        return "○"


def _get_node_type_name(node: TopologyNode) -> str:
    """Get a human-readable name for the node type."""
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


def _format_node_compact(node: TopologyNode) -> str:
    """Format a node for compact display."""
    name = node.name
    if len(name) > 20:
        name = name[:17] + "..."
    return f"{name} ({node.id})"


def _create_visual_node_grid(
    graph: TopologyGraph, 
    comparison: GraphComparisonResult, 
    side: str
) -> List[str]:
    """Create a visual grid representation of nodes with colors indicating changes."""
    lines = []
    
    if not graph.nodes:
        return ["(empty graph)"]
    
    # Group nodes by depth for better visualization
    nodes_by_depth = {}
    for node in graph.nodes:
        depth = node.position.depth
        if depth not in nodes_by_depth:
            nodes_by_depth[depth] = []
        nodes_by_depth[depth].append(node)
    
    # Sort depths
    sorted_depths = sorted(nodes_by_depth.keys())
    
    # Create visual representation
    for depth in sorted_depths[:5]:  # Limit to 5 levels to fit
        level_nodes = nodes_by_depth[depth][:8]  # Limit nodes per level
        
        if depth == 0:
            lines.append(f"Level {depth}: Entry")
        else:
            lines.append(f"Level {depth}:")
        
        # Create node line with colored indicators
        node_line = ""
        for i, node in enumerate(level_nodes):
            if i > 0:
                node_line += " "
            
            # Get color based on change status
            color = _get_node_color(node, comparison, side)
            symbol = _get_node_type_symbol(node)
            
            node_line += f"{color}{symbol}"
        
        # Add overflow indicator
        if len(nodes_by_depth[depth]) > 8:
            node_line += f" +{len(nodes_by_depth[depth]) - 8}"
        
        lines.append(f"  {node_line}")
    
    # Add overflow indicator for depths
    if len(sorted_depths) > 5:
        lines.append(f"  ... +{len(sorted_depths) - 5} more levels")
    
    return lines


def _get_node_color(node: TopologyNode, comparison: GraphComparisonResult, side: str) -> str:
    """Get color emoji for node based on its change status."""
    node_id = node.id
    
    # Check if node was added
    if any(n.id == node_id for n in comparison.added_nodes):
        return "🟢"  # Green for added
    
    # Check if node was removed (only relevant for 'before' side)
    if side == "before" and any(n.id == node_id for n in comparison.removed_nodes):
        return "🔴"  # Red for removed
    
    # Check if node was moved
    if any(n[1].id == node_id for n in comparison.moved_nodes):
        return "🟠"  # Orange for moved
    
    # Check if node was modified
    if any(n[1].id == node_id for n in comparison.modified_nodes):
        return "🟡"  # Yellow for modified
    
    # Default: unchanged
    return "🔵"  # Blue for unchanged