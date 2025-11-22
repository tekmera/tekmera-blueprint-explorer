"""Workfront Fusion specific reporting functionality."""

from datetime import datetime
from typing import Dict, Any
from ...diff.diff import ModuleChange, BlueprintDiffReport, DiffSummary, ChangeScale
from tekmera.projections.meta.types import Platform, ProjectionResult, create_result


class WorkfrontFusionReportingHelper:
    """Helper class for Workfront Fusion specific reporting logic."""
    
    @staticmethod
    def get_component_type(change: ModuleChange) -> str:
        """Get Workfront Fusion component type for reporting display."""
        module_type = change.module_type.lower()
        
        # Use component-specific logic
        if module_type == "filters" or "filter" in module_type:
            return "Filters"
        elif module_type == "routers" or "router" in module_type:
            return "Routers"
        elif "trigger" in module_type or "watch" in module_type:
            return "Triggers"
        elif "error" in module_type or "onerror" in module_type:
            return "Error Handlers"
        elif "workfront" in module_type:
            return "Workfront Modules"
        elif "http" in module_type or "webhook" in module_type:
            return "HTTP/API"
        elif "json" in module_type or "xml" in module_type:
            return "Data Transform"
        else:
            return "Modules"
    
    @staticmethod
    def analyze_components(blueprint: Dict[str, Any]) -> Dict[str, int]:
        """Analyze components in a Workfront Fusion blueprint."""
        from tekmera.projections.meta.utils.workfront_fusion.extract_components import extract_all_components
        
        # Extract all components and count them
        all_components = extract_all_components(blueprint, include_orphans=True)
        
        return {
            "modules": len(all_components["modules"]),
            "routers": len(all_components["routers"]), 
            "filters": len(all_components["filters"]),
            "error_handlers": len(all_components["error_handlers"])
        }
    
    @staticmethod
    def detect_trigger(blueprint: Dict[str, Any]):
        """Detect trigger information for Workfront Fusion blueprint."""
        try:
            from tekmera.projections.components.triggers.detection.workfront_fusion import detect_trigger
            trigger_result = detect_trigger(blueprint)
            return trigger_result.data
        except Exception:
            # If trigger detection fails, continue without trigger info
            return None
    
    @staticmethod
    def generate_diff_report(blueprint1: Dict[str, Any], blueprint2: Dict[str, Any]) -> ProjectionResult[BlueprintDiffReport]:
        """Generate diff report for Workfront Fusion blueprints using topology analysis."""
        
        # Extract basic metadata
        blueprint1_name = blueprint1.get("name", "Unnamed Blueprint 1")
        blueprint2_name = blueprint2.get("name", "Unnamed Blueprint 2")
        
        # Extract topology graphs using projections
        from tekmera.projections.components.topology import extract_topology
        
        topology1_result = extract_topology(blueprint1)
        topology2_result = extract_topology(blueprint2)
        topology1 = topology1_result.data
        topology2 = topology2_result.data
        
        # Use reporting analysis for comparison
        from ...diff.analysis import compare_graphs, detect_node_changes, calculate_structural_change_score, classify_change_magnitude, calculate_change_counts
        
        # Perform graph comparison
        graph_comparison = compare_graphs(topology1, topology2)
        
        # Convert to module changes
        module_changes = detect_node_changes(graph_comparison)
        
        # Calculate metrics
        structural_change_score = calculate_structural_change_score(topology1, topology2, graph_comparison)
        change_counts = calculate_change_counts(module_changes)
        change_scale = classify_change_magnitude(structural_change_score, module_changes, graph_comparison)
        
        
        # Create summary
        summary = DiffSummary(
            total_changes=len([c for c in module_changes if c.change_type.value != "unchanged"]),
            change_counts=change_counts,
            structural_change_score=structural_change_score,
            change_scale=change_scale,
            change_magnitude=structural_change_score
        )
        
        # Create topology analysis data
        topology_analysis = {
            "topology_extracted": True,
            "nodes_blueprint1": len(topology1.nodes),
            "edges_blueprint1": len(topology1.edges),
            "entry_points_blueprint1": len(topology1.entry_points),
            "nodes_blueprint2": len(topology2.nodes), 
            "edges_blueprint2": len(topology2.edges),
            "entry_points_blueprint2": len(topology2.entry_points),
            # Enhanced visualization removed as requested
        }
        
        # Create diff report
        report = BlueprintDiffReport(
            blueprint1_name=blueprint1_name,
            blueprint2_name=blueprint2_name,
            platform=Platform.WORKFRONT_FUSION,
            summary=summary,
            module_changes=module_changes,
            structural_changes=[],  # TODO: Extract from graph_comparison
            generated_at=datetime.now(),
            topology_analysis=topology_analysis,
            configuration_analysis={}
        )
        
        return create_result(
            blueprint=blueprint1,
            platform=Platform.WORKFRONT_FUSION,
            function_name="reporting.platforms.workfront_fusion",
            data=report
        )