"""Workfront Fusion filter-specific diff analysis."""

from typing import Any, Dict, List
from . import FilterDifference


def analyze_workfront_fusion_filter(old_filter: Dict[str, Any], new_filter: Dict[str, Any]) -> List[FilterDifference]:
    """
    Analyze differences between Workfront Fusion filters.
    
    Focuses on condition logic, operators, and business impact.
    """
    differences = []
    
    # Filter name changes (usually cosmetic)
    old_name = old_filter.get("name", "")
    new_name = new_filter.get("name", "")
    
    if old_name != new_name:
        differences.append(FilterDifference(
            field_path="name",
            old_value=old_name,
            new_value=new_name,
            change_type="modified",
            significance="cosmetic",
            description=f"Filter name changed from '{old_name}' to '{new_name}'",
            logical_impact="cosmetic"
        ))
    
    # Condition logic changes (critical for execution)
    old_conditions = old_filter.get("conditions", [])
    new_conditions = new_filter.get("conditions", [])
    
    differences.extend(_analyze_workfront_conditions(old_conditions, new_conditions))
    
    return differences


def _analyze_workfront_conditions(old_conditions: List, new_conditions: List) -> List[FilterDifference]:
    """Analyze Workfront Fusion filter condition changes."""
    differences = []
    
    # Check if conditions structure changed
    old_count = len(old_conditions) if old_conditions else 0
    new_count = len(new_conditions) if new_conditions else 0
    
    if old_count != new_count:
        differences.append(FilterDifference(
            field_path="conditions",
            old_value=f"{old_count} condition groups",
            new_value=f"{new_count} condition groups",
            change_type="modified",
            significance="critical",
            description=f"Number of condition groups changed from {old_count} to {new_count}",
            logical_impact="changes_logic"
        ))
    
    # Analyze individual condition groups
    max_groups = max(old_count, new_count)
    for i in range(max_groups):
        old_group = old_conditions[i] if i < old_count else None
        new_group = new_conditions[i] if i < new_count else None
        
        if old_group is None and new_group is not None:
            differences.append(FilterDifference(
                field_path=f"conditions.{i}",
                old_value=None,
                new_value=f"{len(new_group)} conditions",
                change_type="added",
                significance="important",
                description=f"New condition group {i} added with {len(new_group)} conditions",
                logical_impact="broadens_scope"  # More conditions usually broaden scope
            ))
        elif old_group is not None and new_group is None:
            differences.append(FilterDifference(
                field_path=f"conditions.{i}",
                old_value=f"{len(old_group)} conditions",
                new_value=None,
                change_type="removed",
                significance="important",
                description=f"Condition group {i} removed (had {len(old_group)} conditions)",
                logical_impact="narrows_scope"  # Fewer conditions usually narrow scope
            ))
        elif old_group and new_group:
            # Analyze individual conditions within the group
            differences.extend(_analyze_condition_group(old_group, new_group, i))
    
    return differences


def _analyze_condition_group(old_group: List, new_group: List, group_index: int) -> List[FilterDifference]:
    """Analyze changes within a specific condition group."""
    differences = []
    
    old_count = len(old_group) if old_group else 0
    new_count = len(new_group) if new_group else 0
    
    if old_count != new_count:
        differences.append(FilterDifference(
            field_path=f"conditions.{group_index}",
            old_value=f"{old_count} conditions",
            new_value=f"{new_count} conditions",
            change_type="modified",
            significance="important",
            description=f"Condition group {group_index}: {old_count} → {new_count} conditions",
            logical_impact="changes_logic"
        ))
    
    # Analyze individual conditions for meaningful changes
    max_conditions = max(old_count, new_count)
    for i in range(min(3, max_conditions)):  # Analyze first 3 conditions in detail
        old_condition = old_group[i] if i < old_count else None
        new_condition = new_group[i] if i < new_count else None
        
        if old_condition and new_condition:
            differences.extend(_analyze_individual_condition(old_condition, new_condition, group_index, i))
    
    return differences


def _analyze_individual_condition(old_condition: Dict, new_condition: Dict, group_index: int, condition_index: int) -> List[FilterDifference]:
    """Analyze changes in individual condition parameters."""
    differences = []
    
    # Analyze field being compared (left side)
    old_field = old_condition.get("a", "")
    new_field = new_condition.get("a", "")
    
    if old_field != new_field:
        differences.append(FilterDifference(
            field_path=f"conditions.{group_index}.{condition_index}.a",
            old_value=old_field,
            new_value=new_field,
            change_type="modified",
            significance="important",
            description=f"Condition field changed from '{old_field}' to '{new_field}'",
            logical_impact="changes_logic"
        ))
    
    # Analyze comparison value (right side) - this is often the business-critical change
    old_value = old_condition.get("b", "")
    new_value = new_condition.get("b", "")
    
    if old_value != new_value:
        # This is the key change we want to highlight prominently
        significance = "critical" if _is_business_critical_value_change(old_value, new_value) else "important"
        
        differences.append(FilterDifference(
            field_path=f"conditions.{group_index}.{condition_index}.b",
            old_value=old_value,
            new_value=new_value,
            change_type="modified",
            significance=significance,
            description=f"Filter value changed from '{old_value}' to '{new_value}'",
            logical_impact=_assess_value_change_impact(old_value, new_value)
        ))
    
    # Analyze operator changes
    old_operator = old_condition.get("o", "")
    new_operator = new_condition.get("o", "")
    
    if old_operator != new_operator:
        differences.append(FilterDifference(
            field_path=f"conditions.{group_index}.{condition_index}.o",
            old_value=old_operator,
            new_value=new_operator,
            change_type="modified",
            significance="important",
            description=f"Comparison operator changed from '{old_operator}' to '{new_operator}'",
            logical_impact="changes_logic"
        ))
    
    return differences


def _is_business_critical_value_change(old_value: str, new_value: str) -> bool:
    """Determine if a filter value change is business-critical."""
    # Changes in queue names, project names, status values are usually business-critical
    business_keywords = [
        "queue", "project", "status", "department", "team", 
        "priority", "category", "type", "support", "operations"
    ]
    
    old_lower = str(old_value).lower()
    new_lower = str(new_value).lower()
    
    # If either value contains business keywords, it's likely critical
    for keyword in business_keywords:
        if keyword in old_lower or keyword in new_lower:
            return True
    
    return False


def _assess_value_change_impact(old_value: str, new_value: str) -> str:
    """Assess how a filter value change impacts execution scope."""
    old_str = str(old_value).lower()
    new_str = str(new_value).lower()
    
    # Simple heuristics for scope assessment
    if len(new_str) > len(old_str) and old_str in new_str:
        return "narrows_scope"  # More specific value
    elif len(old_str) > len(new_str) and new_str in old_str:
        return "broadens_scope"  # Less specific value
    else:
        return "changes_logic"  # Different logic entirely