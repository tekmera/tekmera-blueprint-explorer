"""Enhanced summary statistics for diff reports.

This module provides advanced topology analysis and comparison statistics
to give deeper insights into blueprint structural changes.
"""

from typing import Dict, List, Any
from tekmera.projections.components.topology.types import TopologyGraph
from ..analysis.structural import GraphComparisonResult
from ..diff import ModuleChange, ChangeType, ChangeImpact


def generate_enhanced_summary(
    graph1: TopologyGraph,
    graph2: TopologyGraph, 
    comparison: GraphComparisonResult,
    module_changes: List[ModuleChange]
) -> str:
    """
    Generate an enhanced summary with topology insights and advanced statistics.
    
    Provides detailed analysis of structural changes, flow complexity,
    and risk factors beyond basic change counts.
    
    Args:
        graph1: Original topology graph
        graph2: Updated topology graph
        comparison: Graph comparison results
        module_changes: List of module changes
        
    Returns:
        Formatted enhanced summary string
    """
    lines = []
    
    lines.append("ENHANCED ANALYSIS")
    lines.append("═" * 50)
    lines.append("")
    
    # Topology comparison with insights
    lines.extend(format_topology_comparison(graph1, graph2, comparison))
    lines.append("")
    
    # Flow complexity analysis
    lines.extend(_format_flow_complexity_analysis(graph1, graph2))
    lines.append("")
    
    # Change impact analysis
    lines.extend(_format_change_impact_analysis(module_changes, comparison))
    lines.append("")
    
    # Risk factor breakdown
    lines.extend(_format_risk_factor_analysis(graph1, graph2, module_changes, comparison))
    
    return "\n".join(lines)


def format_topology_comparison(
    graph1: TopologyGraph,
    graph2: TopologyGraph,
    comparison: GraphComparisonResult
) -> List[str]:
    """
    Format detailed topology comparison with insights.
    
    Shows before/after statistics with analysis of structural changes
    and their implications for workflow execution.
    """
    lines = []
    
    lines.append("📊 Topology Comparison")
    lines.append("─" * 30)
    
    # Basic statistics with change indicators
    stats = [
        ("Nodes", len(graph1.nodes), len(graph2.nodes)),
        ("Edges", len(graph1.edges), len(graph2.edges)),
        ("Max Depth", graph1.max_depth, graph2.max_depth),
        ("Branches", graph1.branch_count, graph2.branch_count),
        ("Entry Points", len(graph1.entry_points), len(graph2.entry_points))
    ]
    
    for stat_name, before, after in stats:
        delta = after - before
        delta_str = f"({delta:+d})" if delta != 0 else ""
        trend = _get_trend_indicator(delta)
        lines.append(f"  {stat_name:12}: {before:4d} → {after:4d} {delta_str} {trend}")
    
    # Node type analysis
    lines.append("")
    lines.append("Node Type Changes:")
    node_type_changes = _analyze_node_type_changes(graph1, graph2)
    for node_type, (before, after) in node_type_changes.items():
        if before != after:
            delta = after - before
            trend = _get_trend_indicator(delta)
            lines.append(f"  {node_type:12}: {before:3d} → {after:3d} ({delta:+d}) {trend}")
    
    # Structural insights
    insights = _generate_structural_insights(graph1, graph2, comparison)
    if insights:
        lines.append("")
        lines.append("Structural Insights:")
        for insight in insights:
            lines.append(f"  • {insight}")
    
    return lines


def _format_flow_complexity_analysis(graph1: TopologyGraph, graph2: TopologyGraph) -> List[str]:
    """Format analysis of workflow complexity changes."""
    lines = []
    
    lines.append("🔀 Flow Complexity Analysis")
    lines.append("─" * 30)
    
    # Calculate complexity metrics
    complexity1 = _calculate_complexity_metrics(graph1)
    complexity2 = _calculate_complexity_metrics(graph2)
    
    # Complexity score comparison
    score1 = complexity1["total_score"]
    score2 = complexity2["total_score"]
    score_delta = score2 - score1
    
    lines.append(f"  Complexity Score: {score1:.1f} → {score2:.1f} ({score_delta:+.1f})")
    
    if abs(score_delta) > 5:
        if score_delta > 0:
            lines.append("  📈 Significant complexity increase - consider workflow optimization")
        else:
            lines.append("  📉 Complexity reduced - workflow simplified")
    
    # Detailed metrics
    lines.append("")
    lines.append("Detailed Metrics:")
    
    metrics = [
        ("Branching Factor", complexity1["avg_branching"], complexity2["avg_branching"]),
        ("Linear Chains", complexity1["linear_chains"], complexity2["linear_chains"]),
        ("Cyclomatic Complexity", complexity1["cyclomatic"], complexity2["cyclomatic"]),
        ("Error Handling Coverage", complexity1["error_coverage"], complexity2["error_coverage"])
    ]
    
    for metric_name, before, after in metrics:
        if isinstance(before, float):
            lines.append(f"  {metric_name:20}: {before:.2f} → {after:.2f}")
        else:
            lines.append(f"  {metric_name:20}: {before:4d} → {after:4d}")
    
    return lines


def _format_change_impact_analysis(
    module_changes: List[ModuleChange], 
    comparison: GraphComparisonResult
) -> List[str]:
    """Format analysis of change impacts on workflow execution."""
    lines = []
    
    lines.append("⚡ Change Impact Analysis")
    lines.append("─" * 30)
    
    # Categorize changes by impact type
    impact_categories = _categorize_changes_by_impact(module_changes)
    
    for category, changes in impact_categories.items():
        if changes:
            lines.append(f"  {category}: {len(changes)} change(s)")
            for change in changes[:2]:  # Show first 2 examples
                lines.append(f"    • {change.module_name}")
            if len(changes) > 2:
                lines.append(f"    ... and {len(changes) - 2} more")
    
    # Flow disruption analysis
    lines.append("")
    flow_disruptions = _analyze_flow_disruptions(module_changes, comparison)
    if flow_disruptions:
        lines.append("Flow Disruptions:")
        for disruption in flow_disruptions:
            lines.append(f"  ⚠️  {disruption}")
    
    return lines


def _format_risk_factor_analysis(
    graph1: TopologyGraph,
    graph2: TopologyGraph,
    module_changes: List[ModuleChange],
    comparison: GraphComparisonResult
) -> List[str]:
    """Format detailed risk factor analysis."""
    lines = []
    
    lines.append("🎯 Risk Factor Analysis")
    lines.append("─" * 30)
    
    risk_factors = _calculate_risk_factors(graph1, graph2, module_changes, comparison)
    
    # Overall risk score
    total_risk = sum(risk_factors.values())
    lines.append(f"  Total Risk Score: {total_risk:.1f}/10")
    
    # Risk level indication
    if total_risk >= 7:
        lines.append("  🔴 HIGH RISK - Extensive testing and review recommended")
    elif total_risk >= 4:
        lines.append("  🟡 MEDIUM RISK - Additional testing recommended")
    else:
        lines.append("  🟢 LOW RISK - Standard testing should suffice")
    
    lines.append("")
    lines.append("Risk Breakdown:")
    
    risk_descriptions = {
        "trigger_risk": "Trigger Module Changes",
        "flow_risk": "Flow Logic Changes", 
        "complexity_risk": "Complexity Changes",
        "volume_risk": "Change Volume",
        "dependency_risk": "Module Dependencies"
    }
    
    for factor, score in risk_factors.items():
        description = risk_descriptions.get(factor, factor)
        risk_bar = _generate_risk_bar(score, max_score=2, html_mode=False)  # TODO: Pass html_mode from config
        lines.append(f"  {description:20}: {risk_bar} ({score:.1f}/2.0)")
    
    return lines


def _get_trend_indicator(delta: int) -> str:
    """Get a visual trend indicator for numeric changes."""
    if delta > 0:
        return "📈" if delta > 3 else "↗"
    elif delta < 0:
        return "📉" if delta < -3 else "↘"
    else:
        return "→"


def _analyze_node_type_changes(graph1: TopologyGraph, graph2: TopologyGraph) -> Dict[str, tuple]:
    """Analyze changes in node type distribution."""
    def count_node_types(graph):
        counts = {"triggers": 0, "routers": 0, "filters": 0, "error_handlers": 0, "modules": 0}
        for node in graph.nodes:
            if node.is_trigger:
                counts["triggers"] += 1
            elif node.is_router:
                counts["routers"] += 1
            elif node.is_filter:
                counts["filters"] += 1
            elif node.is_error_handler:
                counts["error_handlers"] += 1
            else:
                counts["modules"] += 1
        return counts
    
    counts1 = count_node_types(graph1)
    counts2 = count_node_types(graph2)
    
    return {node_type: (counts1[node_type], counts2[node_type]) 
            for node_type in counts1.keys()}


def _generate_structural_insights(
    graph1: TopologyGraph, 
    graph2: TopologyGraph, 
    comparison: GraphComparisonResult
) -> List[str]:
    """Generate insights about structural changes."""
    insights = []
    
    # Analyze major structural changes
    if len(comparison.added_nodes) > 3:
        insights.append(f"Significant expansion: {len(comparison.added_nodes)} new modules added")
    
    if len(comparison.removed_nodes) > 1:
        insights.append(f"Workflow pruning: {len(comparison.removed_nodes)} modules removed")
    
    if len(comparison.moved_nodes) > 2:
        insights.append(f"Major restructuring: {len(comparison.moved_nodes)} modules repositioned")
    
    # Analyze depth changes
    depth_change = graph2.max_depth - graph1.max_depth
    if depth_change > 2:
        insights.append(f"Workflow deepened by {depth_change} levels - increased nesting")
    elif depth_change < -1:
        insights.append(f"Workflow flattened by {abs(depth_change)} levels - reduced complexity")
    
    # Analyze branching changes
    branch_change = graph2.branch_count - graph1.branch_count
    if branch_change > 2:
        insights.append(f"Increased branching: {branch_change} new decision points added")
    elif branch_change < -1:
        insights.append(f"Reduced branching: {abs(branch_change)} decision points removed")
    
    return insights


def _calculate_complexity_metrics(graph: TopologyGraph) -> Dict[str, float]:
    """Calculate various complexity metrics for a graph."""
    if not graph.nodes:
        return {"total_score": 0, "avg_branching": 0, "linear_chains": 0, 
                "cyclomatic": 0, "error_coverage": 0}
    
    # Average branching factor
    total_outgoing = sum(len([e for e in graph.edges if e.source == node.id]) for node in graph.nodes)
    avg_branching = total_outgoing / len(graph.nodes) if graph.nodes else 0
    
    # Count linear chains (nodes with exactly 1 input and 1 output)
    linear_chains = 0
    for node in graph.nodes:
        incoming = len([e for e in graph.edges if e.target == node.id])
        outgoing = len([e for e in graph.edges if e.source == node.id])
        if incoming == 1 and outgoing == 1:
            linear_chains += 1
    
    # Simplified cyclomatic complexity (edges - nodes + connected_components)
    # For workflow graphs, this approximates decision complexity
    connected_components = len(graph.entry_points) if graph.entry_points else 1
    cyclomatic = len(graph.edges) - len(graph.nodes) + connected_components
    
    # Error handling coverage (percentage of nodes with error handlers)
    error_coverage = len([n for n in graph.nodes if n.is_error_handler]) / len(graph.nodes) * 100
    
    # Total complexity score
    total_score = (avg_branching * 10) + (graph.max_depth * 2) + (cyclomatic * 3) + (error_coverage * 0.1)
    
    return {
        "total_score": total_score,
        "avg_branching": avg_branching,
        "linear_chains": linear_chains,
        "cyclomatic": max(1, cyclomatic),  # Minimum 1
        "error_coverage": error_coverage
    }


def _categorize_changes_by_impact(module_changes: List[ModuleChange]) -> Dict[str, List[ModuleChange]]:
    """Categorize module changes by their potential impact."""
    categories = {
        "High Impact": [],
        "Medium Impact": [],
        "Low Impact": []
    }
    
    for change in module_changes:
        if change.change_type == ChangeType.REMOVED:
            categories["High Impact"].append(change)
        elif change.change_impact in [ChangeImpact.ARCHITECTURAL, ChangeImpact.FUNCTIONAL]:
            categories["High Impact"].append(change)
        elif change.change_type == ChangeType.ADDED:
            categories["Medium Impact"].append(change)
        elif change.change_type == ChangeType.STRUCTURALLY_MOVED:
            categories["Medium Impact"].append(change)
        else:
            categories["Low Impact"].append(change)
    
    return categories


def _analyze_flow_disruptions(
    module_changes: List[ModuleChange], 
    comparison: GraphComparisonResult
) -> List[str]:
    """Analyze potential flow disruptions from changes."""
    disruptions = []
    
    # Check for trigger modifications
    trigger_changes = [c for c in module_changes 
                      if "trigger" in c.module_type.lower() or "watch" in c.module_type.lower()]
    if trigger_changes:
        disruptions.append(f"Trigger modifications may affect workflow initiation ({len(trigger_changes)} changes)")
    
    # Check for router changes
    router_changes = [c for c in module_changes if "router" in c.module_type.lower()]
    if router_changes:
        disruptions.append(f"Router changes may alter execution paths ({len(router_changes)} changes)")
    
    # Check for significant edge changes
    if comparison.removed_edges_count > 2:
        disruptions.append(f"Multiple connections removed ({comparison.removed_edges_count}) - flow continuity may be affected")
    
    return disruptions


def _calculate_risk_factors(
    graph1: TopologyGraph,
    graph2: TopologyGraph,
    module_changes: List[ModuleChange],
    comparison: GraphComparisonResult
) -> Dict[str, float]:
    """Calculate detailed risk factors."""
    
    # Trigger risk (changes to workflow initiation)
    trigger_changes = len([c for c in module_changes if "trigger" in c.module_type.lower()])
    trigger_risk = min(2.0, trigger_changes * 0.8)
    
    # Flow logic risk (routers, filters, structural changes)
    flow_changes = len([c for c in module_changes 
                       if c.change_type in [ChangeType.STRUCTURALLY_MOVED, ChangeType.REMOVED]])
    router_changes = len([c for c in module_changes if "router" in c.module_type.lower()])
    flow_risk = min(2.0, (flow_changes + router_changes) * 0.3)
    
    # Complexity risk (major complexity changes)
    complexity1 = _calculate_complexity_metrics(graph1)["total_score"]
    complexity2 = _calculate_complexity_metrics(graph2)["total_score"]
    complexity_change = abs(complexity2 - complexity1) / max(complexity1, 1)
    complexity_risk = min(2.0, complexity_change * 2)
    
    # Volume risk (too many changes at once)
    total_changes = len([c for c in module_changes if c.change_type != ChangeType.UNCHANGED])
    volume_risk = min(2.0, total_changes * 0.1)
    
    # Dependency risk (changes that might affect other modules)
    critical_changes = len([c for c in module_changes 
                           if c.change_impact in [ChangeImpact.ARCHITECTURAL, ChangeImpact.FUNCTIONAL]])
    dependency_risk = min(2.0, critical_changes * 0.5)
    
    return {
        "trigger_risk": trigger_risk,
        "flow_risk": flow_risk,
        "complexity_risk": complexity_risk,
        "volume_risk": volume_risk,
        "dependency_risk": dependency_risk
    }


def _generate_risk_bar(score: float, max_score: float = 2.0, html_mode: bool = False) -> str:
    """Generate a visual risk bar."""
    filled_blocks = int((score / max_score) * 5)
    empty_blocks = 5 - filled_blocks
    
    if html_mode:
        # Text-based indicators for HTML compatibility
        if filled_blocks >= 4:
            indicator = "[HIGH]"
        elif filled_blocks >= 3:
            indicator = "[MED+]"
        elif filled_blocks >= 2:
            indicator = "[MED ]"
        else:
            indicator = "[LOW ]"
        return indicator + "=" * filled_blocks + "-" * empty_blocks
    else:
        # Emoji-based indicators for terminal/text display
        if filled_blocks >= 4:
            color = "🔴"
        elif filled_blocks >= 3:
            color = "🟠"
        elif filled_blocks >= 2:
            color = "🟡"
        else:
            color = "🟢"
        
        return color + "█" * filled_blocks + "░" * empty_blocks