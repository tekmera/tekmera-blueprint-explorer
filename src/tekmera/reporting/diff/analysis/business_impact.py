"""Business impact assessment for blueprint changes.

Provides meaningful, actionable risk analysis focused on business outcomes
rather than technical metrics.
"""

from typing import Dict, List, Any
from dataclasses import dataclass

from ..diff import ModuleChange, ChangeType, ChangeImpact, ChangeScale


@dataclass
class BusinessImpact:
    """Business-focused impact assessment of blueprint changes."""
    
    # Risk categorization
    deployment_risk: str  # "safe", "caution", "high_risk", "critical"
    testing_requirements: str  # "standard", "extended", "comprehensive", "full_regression"
    
    # Business impact areas
    data_processing_impact: str  # Description of how data flow changes
    user_workflow_impact: str   # Impact on end user workflows
    integration_impact: str     # Impact on external system integrations
    
    # Specific risk factors
    breaking_changes: List[str]  # List of specific breaking changes
    business_logic_changes: List[str]  # Changes to business rules/filters
    connectivity_changes: List[str]    # Changes to external connections
    
    # Recommendations
    recommended_actions: List[str]  # Specific actions to take before deployment
    rollback_considerations: str    # What to consider for rollback planning


def assess_business_impact(module_changes: List[ModuleChange], change_score: float) -> BusinessImpact:
    """
    Assess the business impact of blueprint changes with actionable insights.
    
    Args:
        module_changes: List of all module changes detected
        change_score: Structural change score (0.0-1.0)
        
    Returns:
        BusinessImpact assessment with actionable recommendations
    """
    # Analyze change patterns
    impact_analysis = _analyze_change_patterns(module_changes)
    
    # Determine deployment risk
    deployment_risk = _assess_deployment_risk(impact_analysis, change_score)
    
    # Assess testing requirements
    testing_requirements = _assess_testing_requirements(impact_analysis)
    
    # Analyze business impact areas
    data_impact = _assess_data_processing_impact(impact_analysis)
    user_impact = _assess_user_workflow_impact(impact_analysis)
    integration_impact = _assess_integration_impact(impact_analysis)
    
    # Generate recommendations
    recommendations = _generate_recommendations(impact_analysis, deployment_risk)
    rollback_plan = _assess_rollback_considerations(impact_analysis)
    
    return BusinessImpact(
        deployment_risk=deployment_risk,
        testing_requirements=testing_requirements,
        data_processing_impact=data_impact,
        user_workflow_impact=user_impact,
        integration_impact=integration_impact,
        breaking_changes=impact_analysis["breaking_changes"],
        business_logic_changes=impact_analysis["business_logic_changes"],
        connectivity_changes=impact_analysis["connectivity_changes"],
        recommended_actions=recommendations,
        rollback_considerations=rollback_plan
    )


def _analyze_change_patterns(module_changes: List[ModuleChange]) -> Dict[str, Any]:
    """Analyze patterns in the changes to understand business impact."""
    analysis = {
        "total_changes": len(module_changes),
        "removed_modules": [],
        "added_modules": [],
        "filter_changes": [],
        "connection_changes": [],
        "trigger_changes": [],
        "router_changes": [],
        "breaking_changes": [],
        "business_logic_changes": [],
        "connectivity_changes": [],
        "data_transformation_changes": []
    }
    
    for change in module_changes:
        # Categorize by change type
        if change.change_type == ChangeType.REMOVED:
            analysis["removed_modules"].append(change.module_name)
            analysis["breaking_changes"].append(f"Removed {change.module_type}: {change.module_name}")
            
        elif change.change_type == ChangeType.ADDED:
            analysis["added_modules"].append(change.module_name)
            
        elif change.change_type == ChangeType.CONFIGURATION_CHANGED:
            # Analyze what kind of configuration changed
            _categorize_configuration_change(change, analysis)
    
    return analysis


def _categorize_configuration_change(change: ModuleChange, analysis: Dict[str, Any]) -> None:
    """Categorize a configuration change by its business impact."""
    module_type_lower = change.module_type.lower()
    
    # Filter changes affect business logic
    if "filter" in module_type_lower or change.module_type == "filters":
        analysis["filter_changes"].append(change.module_name)
        
        # Check for queue/department/team changes (common business logic)
        if change.configuration_changes:
            for config_change in change.configuration_changes:
                field = config_change.get("field", "")
                old_val = str(config_change.get("old_value", "")).lower()
                new_val = str(config_change.get("new_value", "")).lower()
                
                if any(keyword in old_val or keyword in new_val for keyword in 
                      ["queue", "department", "team", "support", "operations"]):
                    analysis["business_logic_changes"].append(
                        f"Queue/team assignment changed in {change.module_name}"
                    )
    
    # Router changes affect execution paths
    elif "router" in module_type_lower:
        analysis["router_changes"].append(change.module_name)
        analysis["business_logic_changes"].append(f"Execution path logic changed in {change.module_name}")
    
    # Trigger changes affect when workflows run
    elif "trigger" in module_type_lower or "watch" in module_type_lower:
        analysis["trigger_changes"].append(change.module_name)
        analysis["breaking_changes"].append(f"Trigger configuration changed: {change.module_name}")
    
    # Connection/API changes affect integrations
    elif any(keyword in module_type_lower for keyword in ["connection", "api", "http", "webhook"]):
        analysis["connection_changes"].append(change.module_name)
        analysis["connectivity_changes"].append(f"External connection modified: {change.module_name}")
    
    # Workfront-specific changes
    elif "workfront" in module_type_lower:
        if "create" in module_type_lower or "update" in module_type_lower:
            analysis["data_transformation_changes"].append(change.module_name)
        elif "search" in module_type_lower:
            analysis["business_logic_changes"].append(f"Data retrieval criteria changed: {change.module_name}")


def _assess_deployment_risk(analysis: Dict[str, Any], change_score: float) -> str:
    """Assess deployment risk with business context."""
    removed_count = len(analysis["removed_modules"])
    breaking_count = len(analysis["breaking_changes"])
    trigger_changes = len(analysis["trigger_changes"])
    
    # Critical risk - workflow may break or stop working
    if (removed_count > 0 or 
        trigger_changes > 0 or 
        breaking_count > 2):
        return "critical"
    
    # High risk - significant business logic changes
    elif (len(analysis["business_logic_changes"]) > 1 or 
          len(analysis["connectivity_changes"]) > 0 or
          change_score > 0.3):
        return "high_risk"
    
    # Caution - some business logic changes
    elif (len(analysis["business_logic_changes"]) > 0 or 
          len(analysis["filter_changes"]) > 0 or
          len(analysis["router_changes"]) > 0):
        return "caution"
    
    # Safe - cosmetic or minor changes
    else:
        return "safe"


def _assess_testing_requirements(analysis: Dict[str, Any]) -> str:
    """Determine testing requirements based on change patterns."""
    if analysis["breaking_changes"] or analysis["trigger_changes"]:
        return "full_regression"
    elif analysis["connectivity_changes"] or len(analysis["business_logic_changes"]) > 1:
        return "comprehensive"
    elif analysis["business_logic_changes"] or analysis["filter_changes"]:
        return "extended"
    else:
        return "standard"


def _assess_data_processing_impact(analysis: Dict[str, Any]) -> str:
    """Assess how changes affect data processing."""
    if analysis["removed_modules"]:
        return f"Data processing steps removed - some data may no longer be processed"
    elif analysis["filter_changes"]:
        return f"Data filtering logic changed - different records may be processed"
    elif analysis["business_logic_changes"]:
        return f"Business rules modified - data processing behavior altered"
    elif analysis["added_modules"]:
        return f"New data processing steps added - additional data handling"
    else:
        return "No significant impact on data processing"


def _assess_user_workflow_impact(analysis: Dict[str, Any]) -> str:
    """Assess impact on end user workflows."""
    if analysis["trigger_changes"]:
        return "Workflow triggers changed - automation timing may be affected"
    elif any("queue" in change for change in analysis["business_logic_changes"]):
        return "Queue assignments changed - work may route to different teams"
    elif analysis["connectivity_changes"]:
        return "External integrations changed - user data sync may be affected"
    elif analysis["business_logic_changes"]:
        return "Business logic updated - user experience may change"
    else:
        return "Minimal impact on user workflows"


def _assess_integration_impact(analysis: Dict[str, Any]) -> str:
    """Assess impact on external system integrations."""
    if analysis["connectivity_changes"]:
        return "External connections modified - integration behavior will change"
    elif analysis["removed_modules"]:
        return "Modules removed - some integrations may be disconnected"
    elif analysis["data_transformation_changes"]:
        return "Data transformation logic changed - external systems may receive different data"
    else:
        return "No significant integration impact"


def _generate_recommendations(analysis: Dict[str, Any], deployment_risk: str) -> List[str]:
    """Generate specific, actionable recommendations."""
    recommendations = []
    
    if deployment_risk == "critical":
        recommendations.extend([
            "Conduct full workflow testing in staging environment",
            "Notify stakeholders of potential service disruption",
            "Prepare detailed rollback plan with specific steps",
            "Schedule deployment during low-activity period"
        ])
    elif deployment_risk == "high_risk":
        recommendations.extend([
            "Test all affected business scenarios thoroughly", 
            "Verify external integrations still function correctly",
            "Coordinate with affected business teams"
        ])
    elif deployment_risk == "caution":
        recommendations.extend([
            "Test the specific changed business logic",
            "Verify data flows to expected destinations"
        ])
    
    # Specific recommendations based on change types
    if analysis["filter_changes"]:
        recommendations.append("Verify that filters still capture the intended data sets")
    
    if analysis["connectivity_changes"]:
        recommendations.append("Test all external API connections and authentication")
    
    if analysis["business_logic_changes"]:
        recommendations.append("Validate business rule changes with stakeholders")
    
    return recommendations


def _assess_rollback_considerations(analysis: Dict[str, Any]) -> str:
    """Assess rollback complexity and considerations."""
    if analysis["removed_modules"]:
        return "Complex rollback - removed modules need to be restored with previous configuration"
    elif analysis["connectivity_changes"]:
        return "Moderate rollback complexity - external connections need reconfiguration"
    elif analysis["business_logic_changes"]:
        return "Standard rollback - business logic changes can be reverted easily"
    else:
        return "Simple rollback - changes can be reverted without data loss risk"