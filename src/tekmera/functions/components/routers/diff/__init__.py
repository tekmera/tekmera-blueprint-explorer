"""Router-specific diff analysis.

Platform-agnostic router comparison with platform-specific implementations.
"""

from dataclasses import dataclass
from typing import Any, Dict, List

from ....meta.types import Platform


@dataclass
class RouterDifference:
    """Represents a specific difference found in a router configuration."""

    field_path: str  # e.g., "routes.0.filter", "routes.count"
    old_value: Any
    new_value: Any
    change_type: str  # "added", "removed", "modified"
    significance: str  # "critical", "important", "minor", "cosmetic"
    description: str  # Human-readable description
    routing_impact: str  # "adds_path", "removes_path", "changes_logic", "cosmetic"


def analyze_router_differences(
    old_router: Dict[str, Any], new_router: Dict[str, Any], platform: Platform
) -> List[RouterDifference]:
    """
    Analyze differences between two routers with platform-specific logic.

    Args:
        old_router: Original router configuration
        new_router: Updated router configuration
        platform: Platform (Workfront Fusion, Make.com, etc.)

    Returns:
        List of RouterDifference objects describing changes
    """
    if platform == Platform.WORKFRONT_FUSION:
        from .workfront_fusion import analyze_workfront_fusion_router

        return analyze_workfront_fusion_router(old_router, new_router)
    elif platform == Platform.MAKE_COM:
        from .make_com import analyze_make_com_router

        return analyze_make_com_router(old_router, new_router)
    else:
        raise ValueError(f"Router diff analysis not implemented for platform: {platform}")


def assess_routing_impact(differences: List[RouterDifference]) -> Dict[str, Any]:
    """
    Assess the overall impact of router changes on workflow execution paths.

    Returns:
        Dictionary with impact assessment including:
        - path_changes: "added", "removed", "modified", "unchanged"
        - risk_level: "low", "medium", "high", "critical"
        - execution_impact: Description of how execution paths will change
    """
    if not differences:
        return {
            "path_changes": "unchanged",
            "risk_level": "low",
            "execution_impact": "No changes to routing logic",
        }

    # Analyze routing impact
    routing_impacts = [diff.routing_impact for diff in differences]

    if "removes_path" in routing_impacts:
        return {
            "path_changes": "removed",
            "risk_level": "critical",
            "execution_impact": "Execution paths removed - some data may no longer be processed",
        }
    elif "adds_path" in routing_impacts:
        return {
            "path_changes": "added",
            "risk_level": "medium",
            "execution_impact": "New execution paths added - additional data processing",
        }
    elif "changes_logic" in routing_impacts:
        return {
            "path_changes": "modified",
            "risk_level": "high",
            "execution_impact": "Routing logic changed - data flow patterns altered",
        }
    else:
        return {
            "path_changes": "unchanged",
            "risk_level": "low",
            "execution_impact": "Cosmetic changes only",
        }
