"""
Filter component description generators.

Generates detailed descriptions for newly added filter components,
following the Functions System registry pattern for platform abstraction.
"""

from typing import List

from tekmera.functions.components.topology.types import TopologyNode
from tekmera.functions.meta.types import Platform


def generate_filter_addition_description(node: TopologyNode) -> str:
    """
    Generate detailed description for a newly added filter.

    Platform-agnostic interface following Functions System pattern.

    Args:
        node: Topology node representing the filter

    Returns:
        Detailed description of the filter's configuration
    """
    platform = _detect_platform(node)

    if platform in FILTER_IMPLEMENTATIONS:
        return FILTER_IMPLEMENTATIONS[platform](node)

    return "New filter added to workflow"


def _detect_platform(node: TopologyNode) -> Platform:
    """Detect platform from node characteristics."""
    raw_data = getattr(node, "raw_data", {})

    if isinstance(raw_data, dict):
        module_type = raw_data.get("module", "")
        if isinstance(module_type, str):
            if "workfront" in module_type.lower():
                return Platform.WORKFRONT_FUSION
            elif any(
                prefix in module_type for prefix in ["builtin:", "google:", "slack:", "microsoft:"]
            ):
                return Platform.MAKE_COM

    return Platform.WORKFRONT_FUSION


def _generate_workfront_fusion_filter_description(node: TopologyNode) -> str:
    """Generate description for Workfront Fusion filters."""
    raw_data = getattr(node, "raw_data", {})
    if not isinstance(raw_data, dict):
        return "New filter added to workflow"

    filter_data = raw_data.get("filter", {})
    if not filter_data:
        return "New filter added to workflow"

    filter_name = filter_data.get("name", "Unnamed Filter")
    conditions = filter_data.get("conditions", [])

    # Generate detailed condition summary
    condition_summary = _analyze_workfront_conditions(conditions)

    if condition_summary:
        return f"New filter added: {filter_name} - {condition_summary}"
    else:
        return f"New filter added: {filter_name} (no conditions configured)"


def _generate_make_com_filter_description(node: TopologyNode) -> str:
    """Generate description for Make.com filters."""
    raw_data = getattr(node, "raw_data", {})
    if not isinstance(raw_data, dict):
        return "New filter added to workflow"

    filter_data = raw_data.get("filter", {})
    if not filter_data:
        return "New filter added to workflow"

    filter_name = filter_data.get("name", "Unnamed Filter")
    conditions = filter_data.get("conditions", [])

    # Make.com uses same condition structure as Workfront Fusion
    condition_summary = _analyze_workfront_conditions(conditions)

    if condition_summary:
        return f"New filter added: {filter_name} - {condition_summary}"
    else:
        return f"New filter added: {filter_name} (no conditions configured)"


def _analyze_workfront_conditions(conditions: List) -> str:
    """
    Analyze filter conditions and generate readable summary.

    Works for both Workfront Fusion and Make.com (same structure).
    No arbitrary limits - shows complete condition information.

    Args:
        conditions: List of condition groups from filter configuration

    Returns:
        Human-readable summary of filter conditions
    """
    if not conditions or not isinstance(conditions, list):
        return ""

    condition_summaries = []

    for group_idx, condition_group in enumerate(conditions):
        if not isinstance(condition_group, list) or not condition_group:
            continue

        group_conditions = []

        for condition in condition_group:
            if not isinstance(condition, dict):
                continue

            field = condition.get("a", "")
            operator = condition.get("o", "")
            value = condition.get("b", "")

            # Create readable condition description
            field_name = _extract_readable_field_name(field)
            operator_text = _format_operator_for_display(operator)

            if value:
                group_conditions.append(f"{field_name} {operator_text} '{value}'")
            else:
                group_conditions.append(f"{field_name} {operator_text}")

        if group_conditions:
            if len(group_conditions) == 1:
                condition_summaries.append(group_conditions[0])
            else:
                condition_summaries.append(f"({' AND '.join(group_conditions)})")

    if condition_summaries:
        if len(condition_summaries) == 1:
            return condition_summaries[0]
        else:
            return " OR ".join(condition_summaries)

    return ""


def _extract_readable_field_name(field_expression: str) -> str:
    """Extract human-readable field name from variable expressions."""
    if not field_expression:
        return "field"

    # Handle variable expressions {{module.field}} or {{field}}
    if field_expression.startswith("{{") and field_expression.endswith("}}"):
        inner = field_expression[2:-2]  # Remove {{ }}
        if "." in inner:
            parts = inner.split(".")
            return parts[-1].replace("_", " ").title()  # Use last part
        return inner.replace("_", " ").title()

    # Handle direct field names
    return field_expression.replace("_", " ").title()


def _format_operator_for_display(operator: str) -> str:
    """
    Format operator code for display.

    Keep simple to avoid over-coupling - use platform values as-is
    with basic mapping for common cases.
    """
    simple_operators = {
        "text:equal": "equals",
        "text:notequal": "does not equal",
        "exist": "exists",
        "notexist": "does not exist",
        "text:contains": "contains",
        "text:notcontains": "does not contain",
    }

    # Return mapped value or original operator
    return simple_operators.get(operator, operator or "matches")


# Registry pattern following Functions System architecture
FILTER_IMPLEMENTATIONS = {
    Platform.WORKFRONT_FUSION: _generate_workfront_fusion_filter_description,
    Platform.MAKE_COM: _generate_make_com_filter_description,
}
