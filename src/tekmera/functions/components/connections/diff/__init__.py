"""Connection-specific diff analysis.

Platform-agnostic connection comparison with platform-specific implementations.
"""

from typing import Any, Dict, List
from dataclasses import dataclass

from ....meta.types import Platform


@dataclass
class ConnectionDifference:
    """Represents a specific difference found in a connection configuration."""
    field_path: str  # e.g., "connection_id", "connection_label", "service"
    old_value: Any
    new_value: Any
    change_type: str  # "added", "removed", "modified"
    significance: str  # "critical", "important", "minor", "cosmetic"
    description: str  # Human-readable description
    impact_assessment: str  # "breaks_connectivity", "changes_auth", "cosmetic_only"


def analyze_connection_differences(old_connection_data: Dict[str, Any], new_connection_data: Dict[str, Any], platform: Platform) -> List[ConnectionDifference]:
    """
    Analyze differences between two connection configurations with platform-specific logic.
    
    Args:
        old_connection_data: Original connection configuration from module
        new_connection_data: Updated connection configuration from module
        platform: Platform (Workfront Fusion, Make.com, etc.)
        
    Returns:
        List of ConnectionDifference objects describing changes
    """
    if platform == Platform.WORKFRONT_FUSION:
        from .workfront_fusion import analyze_workfront_fusion_connection
        return analyze_workfront_fusion_connection(old_connection_data, new_connection_data)
    elif platform == Platform.MAKE_COM:
        from .make_com import analyze_make_com_connection
        return analyze_make_com_connection(old_connection_data, new_connection_data)
    else:
        raise ValueError(f"Connection diff analysis not implemented for platform: {platform}")


def assess_connection_impact(differences: List[ConnectionDifference]) -> Dict[str, Any]:
    """
    Assess the overall impact of connection changes on module functionality.
    
    Returns:
        Dictionary with impact assessment including:
        - connectivity_risk: "none", "low", "medium", "high", "critical"
        - auth_impact: "unchanged", "credentials_changed", "auth_method_changed" 
        - execution_impact: Description of how execution will change
        - requires_testing: Boolean indicating if testing is recommended
    """
    if not differences:
        return {
            "connectivity_risk": "none",
            "auth_impact": "unchanged",
            "execution_impact": "No changes to connection configuration",
            "requires_testing": False
        }
    
    # Analyze impact types
    impact_types = [diff.impact_assessment for diff in differences]
    significance_levels = [diff.significance for diff in differences]
    
    # Determine connectivity risk
    if "breaks_connectivity" in impact_types or "critical" in significance_levels:
        connectivity_risk = "critical"
        requires_testing = True
    elif "changes_auth" in impact_types or "important" in significance_levels:
        connectivity_risk = "medium"
        requires_testing = True
    elif any(sig in ["minor"] for sig in significance_levels):
        connectivity_risk = "low"
        requires_testing = False
    else:
        connectivity_risk = "none"
        requires_testing = False
    
    # Determine auth impact
    if "changes_auth" in impact_types:
        auth_impact = "auth_method_changed"
    elif "breaks_connectivity" in impact_types:
        auth_impact = "credentials_changed" 
    else:
        auth_impact = "unchanged"
    
    # Generate execution impact description
    if "breaks_connectivity" in impact_types:
        execution_impact = "Connection configuration changed - module may fail to authenticate or connect"
    elif "changes_auth" in impact_types:
        execution_impact = "Authentication method or credentials changed - requires validation"
    else:
        execution_impact = "Minor connection metadata changes - functionality preserved"
    
    return {
        "connectivity_risk": connectivity_risk,
        "auth_impact": auth_impact,
        "execution_impact": execution_impact,
        "requires_testing": requires_testing,
        "change_summary": _generate_change_summary(differences)
    }


def _generate_change_summary(differences: List[ConnectionDifference]) -> str:
    """Generate a concise summary of connection changes."""
    if not differences:
        return "No changes"
    
    change_types = {}
    for diff in differences:
        change_types[diff.change_type] = change_types.get(diff.change_type, 0) + 1
    
    summary_parts = []
    if change_types.get("added", 0) > 0:
        summary_parts.append(f"{change_types['added']} added")
    if change_types.get("modified", 0) > 0:
        summary_parts.append(f"{change_types['modified']} modified")
    if change_types.get("removed", 0) > 0:
        summary_parts.append(f"{change_types['removed']} removed")
    
    return f"{', '.join(summary_parts)} connection field{'s' if len(differences) > 1 else ''}"


def get_connection_change_category(module_data: Dict[str, Any], platform: Platform) -> str:
    """
    Get the connection change category for proper diff analysis routing.
    
    Returns categories like: 'workfront_api', 'email_service', 'http_webhook', etc.
    """
    module_type = module_data.get("module", "")
    
    if platform == Platform.WORKFRONT_FUSION:
        return _get_workfront_connection_category(module_type)
    elif platform == Platform.MAKE_COM:
        return _get_make_com_connection_category(module_type)
    else:
        return "unknown"


def _get_workfront_connection_category(module_type: str) -> str:
    """Get Workfront Fusion connection category."""
    module_lower = module_type.lower()
    
    if "workfront" in module_lower:
        return "workfront_api"
    elif "http" in module_lower or "webhook" in module_lower:
        return "http_webhook"
    elif "email" in module_lower:
        return "email_service"
    elif "database" in module_lower or "sql" in module_lower:
        return "database"
    else:
        return "api_service"


def _get_make_com_connection_category(module_type: str) -> str:
    """Get Make.com connection category."""
    module_lower = module_type.lower()
    
    if "email" in module_lower:
        return "email_service"
    elif "http" in module_lower or "webhook" in module_lower:
        return "http_webhook" 
    elif "google" in module_lower:
        return "google_service"
    elif "microsoft" in module_lower:
        return "microsoft_service"
    elif "database" in module_lower or "sql" in module_lower:
        return "database"
    else:
        return "api_service"