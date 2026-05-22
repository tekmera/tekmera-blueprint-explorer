"""Make.com specific reporting functionality."""

from datetime import datetime
from typing import Any, Dict

from tekmera.functions.meta.types import Platform, ProjectionResult, create_result
# from tekmera.reporting import diff

from ...diff.diff import BlueprintDiffReport, DiffSummary, ModuleChange


class MakeComReportingHelper:
    """Helper class for Make.com specific reporting logic."""

    @staticmethod
    def get_component_type(change: ModuleChange) -> str:
        """Get Make.com component type for reporting display."""
        module_type = change.module_type.lower()

        # Based on real blueprint data analysis - stick to verified patterns
        if "filter" in module_type:
            return "Filters"
        elif "router" in module_type:
            return "Routers"
        elif "trigger" in module_type or "watch" in module_type:
            return "Triggers"
        elif "error" in module_type:
            return "Error Handlers"
        else:
            return "Modules"

    @staticmethod
    def analyze_components(blueprint: Dict[str, Any]) -> Dict[str, int]:
        """Analyze components in a Make.com blueprint."""
        from tekmera.functions.meta.utils.make_com.extract_components import extract_all_components

        # Extract all components and count them
        all_components = extract_all_components(blueprint, include_orphans=True)

        return {
            "modules": len(all_components["modules"]),
            "routers": len(all_components["routers"]),
            "filters": len(all_components["filters"]),
            "error_handlers": len(all_components["error_handlers"]),
        }

    @staticmethod
    def detect_trigger(blueprint: Dict[str, Any]):
        """Detect trigger information for Make.com blueprint."""
        try:
            from tekmera.functions.components.triggers.detection.make_com import detect_trigger

            trigger_result = detect_trigger(blueprint)
            return trigger_result.data
        except Exception:
            # If trigger detection fails, continue without trigger info
            return None

    @staticmethod
    def generate_diff_report(
        blueprint1: Dict[str, Any], blueprint2: Dict[str, Any]
    ) -> ProjectionResult[BlueprintDiffReport]:
        """Generate diff report for Make.com blueprints using topology analysis."""

        # Extract basic metadata
        blueprint1_name = blueprint1.get("name", "Unnamed Blueprint 1")
        blueprint2_name = blueprint2.get("name", "Unnamed Blueprint 2")

        # For now, create a simple stub report for Make.com
        # TODO: Implement topology analysis for Make.com similar to Workfront Fusion

        from tekmera.functions.components.topology import extract_topology

        topology1_result = extract_topology(blueprint1)
        topology2_result = extract_topology(blueprint2)
        topology1 = topology1_result.data
        topology2 = topology2_result.data

        from ...diff.analysis import (
            calculate_change_counts,
            calculate_structural_change_score,
            classify_change_scope,
            compare_graphs,
            detect_node_changes,
        )

        # Perform graph comparison
        graph_comparison = compare_graphs(topology1, topology2)

        # Convert to module changes
        module_changes = detect_node_changes(graph_comparison)

        # Connection analysis for Make.com (when topology analysis is implemented)
        from ...diff.analysis.connection_analysis import (
            analyze_connection_changes,
            format_connection_summary_for_html,
        )

        connection_summary = analyze_connection_changes(module_changes, "make_com")
        connection_analysis = format_connection_summary_for_html(connection_summary)

        # Calculate metrics
        structural_change_score = calculate_structural_change_score(
            topology1, topology2, graph_comparison
        )
        change_counts = calculate_change_counts(module_changes)
        change_scale = classify_change_scope(
            structural_change_score, module_changes, graph_comparison
        )

        # Create minimal summary
        summary = DiffSummary(
            total_changes=len([c for c in module_changes if c.change_type.value != "unchanged"]),
            change_counts=change_counts,
            structural_change_score=structural_change_score,
            change_scale=change_scale,
            change_magnitude=structural_change_score,
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

        # Create minimal diff report
        report = BlueprintDiffReport(
            blueprint1_name=blueprint1_name,
            blueprint2_name=blueprint2_name,
            platform=Platform.MAKE_COM,
            summary=summary,
            module_changes=module_changes,
            structural_changes=[],
            generated_at=datetime.now(),
            topology_analysis=topology_analysis,
            configuration_analysis={"connection_analysis": connection_analysis},
        )

        return create_result(
            blueprint=blueprint1,
            platform=Platform.MAKE_COM,
            function_name="reporting.platforms.make_com",
            data=report,
        )
