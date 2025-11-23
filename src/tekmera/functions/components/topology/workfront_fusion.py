"""Workfront Fusion topology extraction."""

from typing import Any, Dict
from ...meta.types import Platform, ProjectionResult, create_result
from ...meta.utils.workfront_fusion.extract_components import extract_all_components
from .types import TopologyGraph, TopologyNode, TopologyEdge, EdgeType, GraphPosition


def extract_workfront_topology(blueprint: Dict[str, Any]) -> ProjectionResult[TopologyGraph]:
    """Extract topology graph from a Workfront Fusion blueprint."""
    
    # Extract all components
    components = extract_all_components(blueprint, include_orphans=True)
    
    # Create nodes
    nodes = []
    edges = []
    entry_points = []
    
    # Build nodes from all component types
    # Module nodes
    for component in components["modules"]:
        node = TopologyNode(
            id=component.id,
            module_type=component.module_type,
            name=component.raw_data.get("label", f"Module {component.id}"),
            platform=Platform.WORKFRONT_FUSION,
            raw_data=component.raw_data
        )
        nodes.append(node)
    
    # Filter nodes
    for component in components["filters"]:
        # For filter nodes, raw_data should contain ONLY the filter configuration
        filter_data = component.raw_data.get("filter", {})
        if component.source_router_id:
            filter_data['source_router_id'] = component.source_router_id
        
        node = TopologyNode(
            id=f"{component.id}_filter",
            module_type="filter",
            name=component.filter_name,
            platform=Platform.WORKFRONT_FUSION,
            raw_data=filter_data
        )
        nodes.append(node)
    
    # Router nodes
    for component in components["routers"]:
        node = TopologyNode(
            id=f"{component.id}_router",
            module_type="router",
            name=component.raw_data.get("name", f"Router {component.id}"),
            platform=Platform.WORKFRONT_FUSION,
            raw_data=component.raw_data
        )
        nodes.append(node)
    
    # Error handlers are processed as regular modules through recursive extraction
    # No need for separate error handler nodes - they get their own module IDs
    
    # Simple edge creation based on flow order
    # This is a simplified implementation - real implementation would parse flow structure
    for i, component in enumerate(components["modules"]):
        if i > 0:
            prev_component = components["modules"][i-1]
            edge = TopologyEdge(
                source=prev_component.id,
                target=component.id,
                edge_type=EdgeType.NORMAL
            )
            edges.append(edge)
    
    # First module is entry point
    if components["modules"]:
        entry_points.append(components["modules"][0].id)
    
    graph = TopologyGraph(
        nodes=nodes,
        edges=edges,
        entry_points=entry_points,
        platform=Platform.WORKFRONT_FUSION
    )
    
    return create_result(
        blueprint=blueprint,
        platform=Platform.WORKFRONT_FUSION,
        function_name="topology.workfront_fusion",
        data=graph
    )