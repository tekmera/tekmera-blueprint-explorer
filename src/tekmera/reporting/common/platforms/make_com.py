"""Make.com specific reporting functionality."""

from datetime import datetime
from typing import Dict, Any
from ...diff.diff import ModuleChange, BlueprintDiffReport, DiffSummary, ChangeScale
from tekmera.functions.meta.types import Platform, ProjectionResult, create_result


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
            "error_handlers": len(all_components["error_handlers"])
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
    def generate_diff_report(blueprint1: Dict[str, Any], blueprint2: Dict[str, Any]) -> ProjectionResult[BlueprintDiffReport]:
        """Generate diff report for Make.com blueprints using topology analysis."""
        
        # Extract basic metadata
        blueprint1_name = blueprint1.get("name", "Unnamed Blueprint 1")
        blueprint2_name = blueprint2.get("name", "Unnamed Blueprint 2")
        
        # For now, create a simple stub report for Make.com
        # TODO: Implement topology analysis for Make.com similar to Workfront Fusion
        
        # Connection analysis for Make.com (when topology analysis is implemented)
        from ...diff.analysis.connection_analysis import analyze_connection_changes, format_connection_summary_for_html
        # For now, empty module changes until topology analysis is implemented
        connection_summary = analyze_connection_changes([], "make_com")
        connection_analysis = format_connection_summary_for_html(connection_summary)
        
        # Create minimal summary
        summary = DiffSummary(
            total_changes=0,
            change_counts={"unchanged": 0, "added": 0, "removed": 0, "modified": 0, "moved": 0},
            structural_change_score=0.0,
            change_scale=ChangeScale.UNCHANGED,
            change_magnitude=0.0
        )
        
        # Create minimal diff report
        report = BlueprintDiffReport(
            blueprint1_name=blueprint1_name,
            blueprint2_name=blueprint2_name,
            platform=Platform.MAKE_COM,
            summary=summary,
            module_changes=[],
            structural_changes=[],
            generated_at=datetime.now(),
            topology_analysis={"stub": "Make.com topology analysis not yet implemented"},
            configuration_analysis={
                "connection_analysis": connection_analysis
            }
        )
        
        return create_result(
            blueprint=blueprint1,
            platform=Platform.MAKE_COM,
            function_name="reporting.platforms.make_com",
            data=report
        )