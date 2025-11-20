"""Make.com blueprint diff implementation."""

from datetime import datetime
from typing import Any, Dict

from ...meta.types import Platform, ProjectionResult, create_result
from .types import (
    BlueprintDiffReport,
    DiffSummary,
    ModuleChange,
    StructuralChange,
    ChangeType,
    ChangeSeverity,
    RiskLevel
)


def generate_diff_report(blueprint1: Dict[str, Any], blueprint2: Dict[str, Any]) -> ProjectionResult[BlueprintDiffReport]:
    """
    Generate diff report for Make.com blueprints.
    
    Currently returns a stub implementation with placeholder data.
    This will be replaced with real topology and configuration analysis.
    """
    # Extract basic metadata
    blueprint1_name = blueprint1.get("name", "Unnamed Blueprint 1")
    blueprint2_name = blueprint2.get("name", "Unnamed Blueprint 2")
    
    # STUB: Create placeholder diff report
    # In real implementation, this would:
    # 1. Extract topology from scenario.modules structure
    # 2. Compare module flows and connections
    # 3. Analyze configuration differences
    # 4. Classify changes by impact
    
    # Placeholder module changes
    module_changes = [
        ModuleChange(
            module_id="1",
            module_type="webhook:CustomWebHook",
            module_name="Order Webhook",
            change_type=ChangeType.CONFIGURATION_CHANGED,
            configuration_changes=[{"field": "data_structure", "old_value": "{}", "new_value": "enhanced"}],
            change_severity=ChangeSeverity.MINOR,
            impact_description="Updated webhook data structure validation"
        ),
        ModuleChange(
            module_id="4",
            module_type="json:ParseJSON",
            module_name="Parse Order Data",
            change_type=ChangeType.ADDED,
            change_severity=ChangeSeverity.MODERATE,
            impact_description="New JSON parser added for enhanced data validation"
        )
    ]
    
    # Placeholder structural changes
    structural_changes = [
        StructuralChange(
            change_description="Added data validation flow between webhook and processing",
            affected_modules=["1", "4", "5"],
            change_type="flow_extended",
            impact_level=ChangeSeverity.MODERATE
        )
    ]
    
    # Calculate summary
    change_counts = {
        "unchanged": 6,
        "configuration_changed": 1,
        "structurally_moved": 0,
        "added": 1,
        "removed": 0
    }
    
    summary = DiffSummary(
        total_changes=2,
        change_counts=change_counts,
        structural_change_score=0.15,  # 15% structural difference
        risk_level=RiskLevel.LOW,
        breaking_changes_count=0
    )
    
    # Create the diff report
    diff_report = BlueprintDiffReport(
        blueprint1_name=blueprint1_name,
        blueprint2_name=blueprint2_name,
        platform=Platform.MAKE_COM,
        generated_at=datetime.now(),
        summary=summary,
        module_changes=module_changes,
        structural_changes=structural_changes,
        topology_analysis={
            "stub_note": "Real topology analysis will be implemented in Phase 2",
            "modules_blueprint1": 7,
            "modules_blueprint2": 8,
            "connections_blueprint1": 6,
            "connections_blueprint2": 7
        },
        configuration_analysis={
            "stub_note": "Real configuration diff will be implemented in Phase 4",
            "parameters_compared": 23,
            "parameters_changed": 1,
            "data_structure_changes": 1
        }
    )
    
    return create_result(
        blueprint=blueprint1,
        platform=Platform.MAKE_COM,
        function_name="blueprints.diff.make_com",
        data=diff_report
    )


def generate_sample_diff_report() -> ProjectionResult[BlueprintDiffReport]:
    """
    Generate a sample Make.com diff report for demos.
    """
    module_changes = [
        ModuleChange(
            module_id="1",
            module_type="email:TriggerNewEmail",
            module_name="Email Monitor",
            change_type=ChangeType.CONFIGURATION_CHANGED,
            configuration_changes=[
                {"field": "subject", "old_value": "order_", "new_value": "booking_"},
                {"field": "maxResults", "old_value": 1, "new_value": 3}
            ],
            change_severity=ChangeSeverity.MINOR,
            impact_description="Updated email filter criteria and batch size"
        ),
        ModuleChange(
            module_id="6",
            module_type="http:MakeRequest",
            module_name="API Status Update",
            change_type=ChangeType.ADDED,
            change_severity=ChangeSeverity.MODERATE,
            impact_description="New API call added to update external system status"
        ),
        ModuleChange(
            module_id="3",
            module_type="BasicRouter:Route",
            module_name="Priority Router",
            change_type=ChangeType.STRUCTURALLY_MOVED,
            old_position={"flow_order": 3},
            new_position={"flow_order": 2},
            change_severity=ChangeSeverity.MODERATE,
            impact_description="Router moved earlier in flow for faster prioritization"
        )
    ]
    
    structural_changes = [
        StructuralChange(
            change_description="New error handling route added to priority router",
            affected_modules=["3", "7"],
            change_type="error_route_added",
            impact_level=ChangeSeverity.MODERATE
        )
    ]
    
    change_counts = {
        "unchanged": 8,
        "configuration_changed": 1,
        "structurally_moved": 1,
        "added": 1,
        "removed": 0
    }
    
    summary = DiffSummary(
        total_changes=3,
        change_counts=change_counts,
        structural_change_score=0.22,
        risk_level=RiskLevel.LOW,
        breaking_changes_count=0
    )
    
    diff_report = BlueprintDiffReport(
        blueprint1_name="Email Order Processor v1.3",
        blueprint2_name="Email Order Processor v1.4",
        platform=Platform.MAKE_COM,
        generated_at=datetime.now(),
        summary=summary,
        module_changes=module_changes,
        structural_changes=structural_changes,
        topology_analysis={
            "modules_blueprint1": 11,
            "modules_blueprint2": 12,
            "routes_blueprint1": 2,
            "routes_blueprint2": 3,
            "flow_complexity_change": "+8%"
        },
        configuration_analysis={
            "parameters_compared": 34,
            "parameters_changed": 4,
            "filter_changes": 2,
            "mapping_changes": 1,
            "connection_changes": 0
        }
    )
    
    return create_result(
        blueprint={},
        platform=Platform.MAKE_COM,
        function_name="blueprints.diff.make_com.sample",
        data=diff_report
    )