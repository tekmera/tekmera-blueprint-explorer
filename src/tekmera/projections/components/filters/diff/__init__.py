"""Filter-specific diff analysis.

Platform-agnostic filter comparison with platform-specific implementations.
"""

from typing import Any, Dict, List
from dataclasses import dataclass

from ....meta.types import Platform


@dataclass
class FilterDifference:
    """Represents a specific difference found in a filter configuration."""
    field_path: str  # e.g., "conditions.0.a", "name"
    old_value: Any
    new_value: Any
    change_type: str  # "added", "removed", "modified"
    significance: str  # "critical", "important", "minor", "cosmetic"
    description: str  # Human-readable description
    logical_impact: str  # "narrows_scope", "broadens_scope", "changes_logic", "cosmetic"


def analyze_filter_differences(old_filter: Dict[str, Any], new_filter: Dict[str, Any], platform: Platform) -> List[FilterDifference]:
    """
    Analyze differences between two filters with platform-specific logic.
    
    Args:
        old_filter: Original filter configuration
        new_filter: Updated filter configuration  
        platform: Platform (Workfront Fusion, Make.com, etc.)
        
    Returns:
        List of FilterDifference objects describing changes
    """
    if platform == Platform.WORKFRONT_FUSION:
        from .workfront_fusion import analyze_workfront_fusion_filter
        return analyze_workfront_fusion_filter(old_filter, new_filter)
    elif platform == Platform.MAKE_COM:
        from .make_com import analyze_make_com_filter
        return analyze_make_com_filter(old_filter, new_filter)
    else:
        raise ValueError(f"Filter diff analysis not implemented for platform: {platform}")


def assess_filter_impact(differences: List[FilterDifference]) -> Dict[str, Any]:
    """
    Assess the overall impact of filter changes on workflow execution.
    
    Returns:
        Dictionary with impact assessment including:
        - scope_change: "narrower", "broader", "different", "unchanged"
        - risk_level: "low", "medium", "high", "critical"
        - execution_impact: Description of how execution will change
    """
    if not differences:
        return {
            "scope_change": "unchanged",
            "risk_level": "low",
            "execution_impact": "No changes to filter logic"
        }
    
    # Analyze logical impact
    logical_impacts = [diff.logical_impact for diff in differences]
    
    if "changes_logic" in logical_impacts:
        scope_change = "different"
        risk_level = "high"
        execution_impact = "Filter logic fundamentally changed"
    elif "narrows_scope" in logical_impacts:
        scope_change = "narrower"
        risk_level = "medium"
        execution_impact = "Filter will allow fewer items through"
    elif "broadens_scope" in logical_impacts:
        scope_change = "broader" 
        risk_level = "medium"
        execution_impact = "Filter will allow more items through"
    else:
        scope_change = "unchanged"
        risk_level = "low"
        execution_impact = "Cosmetic changes only"
    
    return {
        "scope_change": scope_change,
        "risk_level": risk_level,
        "execution_impact": execution_impact
    }