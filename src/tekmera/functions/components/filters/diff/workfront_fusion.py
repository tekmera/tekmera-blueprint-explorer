"""Workfront Fusion filter-specific diff analysis."""

from typing import Any, Dict, List
from . import FilterDifference


def analyze_workfront_fusion_filter(
    old_filter: Dict[str, Any], new_filter: Dict[str, Any]
) -> List[FilterDifference]:
    """
    Analyze differences between Workfront Fusion filters.
    Focuses on condition logic, operators, and business impact.
    """
    differences = []

    # Filter name (cosmetic)
    old_name = old_filter.get("name", "")
    new_name = new_filter.get("name", "")

    if old_name != new_name:
        differences.append(
            FilterDifference(
                field_path="name",
                old_value=old_name,
                new_value=new_name,
                change_type="modified",
                significance="cosmetic",
                description=f"Filter name changed from '{old_name}' to '{new_name}'",
                logical_impact="cosmetic",
            )
        )

    # Conditions
    old_conditions = old_filter.get("conditions", [])
    new_conditions = new_filter.get("conditions", [])

    differences.extend(_analyze_workfront_conditions(old_conditions, new_conditions))
    return differences


# ---------------------------------------------------------------------
# CONDITION GROUPS
# ---------------------------------------------------------------------

def _analyze_workfront_conditions(
    old_conditions: List, new_conditions: List
) -> List[FilterDifference]:
    differences = []

    old_count = len(old_conditions) if old_conditions else 0
    new_count = len(new_conditions) if new_conditions else 0

    # Structural change to group count
    if old_count != new_count:
        differences.append(
            FilterDifference(
                field_path="conditions",
                old_value=f"{old_count} condition groups",
                new_value=f"{new_count} condition groups",
                change_type="modified",
                significance="critical",
                description=f"Number of condition groups changed from {old_count} to {new_count}",
                logical_impact="changes_logic",
            )
        )

    max_groups = max(old_count, new_count)

    for i in range(max_groups):
        old_group = old_conditions[i] if i < old_count else None
        new_group = new_conditions[i] if i < new_count else None

        if old_group is None and new_group is not None:
            differences.append(
                FilterDifference(
                    field_path=f"conditions.{i}",
                    old_value=None,
                    new_value=f"{len(new_group)} conditions",
                    change_type="added",
                    significance="important",
                    description=f"Condition group {i} added with {len(new_group)} conditions",
                    logical_impact="broadens_scope",
                )
            )
        elif old_group is not None and new_group is None:
            differences.append(
                FilterDifference(
                    field_path=f"conditions.{i}",
                    old_value=f"{len(old_group)} conditions",
                    new_value=None,
                    change_type="removed",
                    significance="important",
                    description=f"Condition group {i} removed (had {len(old_group)} conditions)",
                    logical_impact="narrows_scope",
                )
            )
        else:
            differences.extend(_analyze_condition_group(old_group, new_group, i))

    return differences


# ---------------------------------------------------------------------
# CONDITION GROUP DETAIL
# ---------------------------------------------------------------------

def _analyze_condition_group(
    old_group: List, new_group: List, group_index: int
) -> List[FilterDifference]:
    differences = []

    old_count = len(old_group) if old_group else 0
    new_count = len(new_group) if new_group else 0

    if old_count != new_count:
        differences.append(
            FilterDifference(
                field_path=f"conditions.{group_index}",
                old_value=f"{old_count} conditions",
                new_value=f"{new_count} conditions",
                change_type="modified",
                significance="important",
                description=f"Condition group {group_index}: {old_count} → {new_count} conditions",
                logical_impact="changes_logic",
            )
        )

    # Full condition-level diff (no truncation)
    max_conditions = max(old_count, new_count)

    for i in range(max_conditions):
        old_condition = old_group[i] if i < old_count else None
        new_condition = new_group[i] if i < new_count else None

        if old_condition is None and new_condition is not None:
            differences.append(
                FilterDifference(
                    field_path=f"conditions.{group_index}.{i}",
                    old_value=None,
                    new_value=new_condition,
                    change_type="added",
                    significance="important",
                    description=f"Condition {i} added to group {group_index}",
                    logical_impact="broadens_scope",
                )
            )
        elif old_condition is not None and new_condition is None:
            differences.append(
                FilterDifference(
                    field_path=f"conditions.{group_index}.{i}",
                    old_value=old_condition,
                    new_value=None,
                    change_type="removed",
                    significance="important",
                    description=f"Condition {i} removed from group {group_index}",
                    logical_impact="narrows_scope",
                )
            )
        elif old_condition and new_condition:
            differences.extend(
                _analyze_individual_condition(old_condition, new_condition, group_index, i)
            )

    return differences


# ---------------------------------------------------------------------
# INDIVIDUAL CONDITION LOGIC
# ---------------------------------------------------------------------

def _analyze_individual_condition(
    old_condition: Dict, new_condition: Dict, group_index: int, condition_index: int
) -> List[FilterDifference]:
    differences = []

    # Extract operator first (bug fix)
    old_operator = old_condition.get("o", "")
    new_operator = new_condition.get("o", "")

    # Field (left side)
    old_field = old_condition.get("a", "")
    new_field = new_condition.get("a", "")

    if old_field != new_field:
        differences.append(
            FilterDifference(
                field_path=f"conditions.{group_index}.{condition_index}.a",
                old_value=old_field,
                new_value=new_field,
                change_type="modified",
                significance="important",
                description=_create_field_change_description(old_field, new_field),
                logical_impact="changes_logic",
            )
        )

    # Value (right side)
    old_value = old_condition.get("b", "")
    new_value = new_condition.get("b", "")

    if old_value != new_value:
        significance = (
            "critical"
            if _is_business_critical_value_change(old_value, new_value)
            else "important"
        )

        differences.append(
            FilterDifference(
                field_path=f"conditions.{group_index}.{condition_index}.b",
                old_value=old_value,
                new_value=new_value,
                change_type="modified",
                significance=significance,
                description=_create_filter_value_description(
                    old_field, old_operator, old_value, new_operator, new_value
                ),
                logical_impact=_assess_value_change_impact(old_value, new_value),
            )
        )

    # Operator
    if old_operator != new_operator:
        differences.append(
            FilterDifference(
                field_path=f"conditions.{group_index}.{condition_index}.o",
                old_value=old_operator,
                new_value=new_operator,
                change_type="modified",
                significance="important",
                description=f"Comparison operator changed from '{old_operator}' to '{new_operator}'",
                logical_impact="changes_logic",
            )
        )

    return differences


# ---------------------------------------------------------------------
# HEURISTICS + FIELD LOGIC
# ---------------------------------------------------------------------

def _is_business_critical_value_change(old_value: str, new_value: str) -> bool:
    business_keywords = {
        "queue",
        "project",
        "status",
        "department",
        "team",
        "priority",
        "category",
        "type",
        "support",
        "operations",
    }

    old_lower = str(old_value).lower()
    new_lower = str(new_value).lower()

    return any(
        f" {kw} " in f" {old_lower} " or f" {kw} " in f" {new_lower} "
        for kw in business_keywords
    )


def _assess_value_change_impact(old_value: str, new_value: str) -> str:
    old_str = str(old_value).lower()
    new_str = str(new_value).lower()

    if len(new_str) > len(old_str) and old_str in new_str:
        return "narrows_scope"
    elif len(old_str) > len(new_str) and new_str in old_str:
        return "broadens_scope"
    else:
        return "changes_logic"


def _create_filter_value_description(
    field: str,
    old_operator: str,
    old_value: str,
    new_operator: str,
    new_value: str,
) -> str:
    field_name = _extract_field_name(field)

    if not old_value and new_value:
        return f"Filter now requires {field_name} {new_operator} '{new_value}'"
    if old_value and not new_value:
        return f"Filter no longer requires {field_name} {old_operator} '{old_value}'"
    if old_operator != new_operator:
        return f"Filter logic changed: {field_name} was {old_operator} '{old_value}', now {new_operator} '{new_value}'"
    return f"Filter value changed: {field_name} {new_operator} '{old_value}' → '{new_value}'"


def _create_field_change_description(old_field: str, new_field: str) -> str:
    old_name = _extract_field_name(old_field)
    new_name = _extract_field_name(new_field)

    if old_name != new_name:
        return f"Filter now checks {new_name} instead of {old_name}"
    return f"Filter field reference updated: {old_field} → {new_field}"


def _extract_field_name(field_expression: str) -> str:
    if not field_expression:
        return "unknown field"

    if field_expression.startswith("{{") and field_expression.endswith("}}"):
        inner = field_expression[2:-2]
        parts = inner.split(".")
        return parts[-1].replace("_", " ").title()

    return field_expression.replace("_", " ").title()
