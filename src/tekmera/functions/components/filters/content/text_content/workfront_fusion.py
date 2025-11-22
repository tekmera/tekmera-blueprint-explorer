"""Workfront Fusion filter text content extraction."""

import json
from typing import Any, Dict, List

from .....meta.types import FilterComponent, ModuleResult, Platform, create_module_result


def text_content(filter_component: FilterComponent) -> ModuleResult[str]:
    """
    Extract text content from Workfront Fusion filter component.

    Extracts text from:
    - Filter names and descriptions
    - Condition variable expressions
    - Comparison values and operators
    - Component metadata
    """
    text_parts = []

    # Use typed component properties
    text_parts.append(f"Filter ID: {filter_component.id}")
    text_parts.append(f"Filter Name: {filter_component.filter_name}")
    text_parts.append(f"Conditions Count: {filter_component.conditions_count}")
    text_parts.append(f"Context: {filter_component.extraction_context}")

    # Extract from the raw filter data
    raw_item = filter_component.raw_data
    filter_data = raw_item.get("filter", {})

    # Extract filter conditions text
    filter_text = _extract_filter_conditions(filter_data)
    if filter_text:
        text_parts.extend(filter_text)

    # Extract from item metadata
    metadata = raw_item.get("metadata", {})
    designer = metadata.get("designer", {})
    if "name" in designer:
        text_parts.append(f"Designer Name: {designer['name']}")

    # Fallback to JSON if no structured text found
    if not text_parts:
        text_parts.append(json.dumps(filter_component.raw_data, sort_keys=True))

    combined_text = "\n".join(text_parts)

    return create_module_result(
        module=filter_component.raw_data,
        platform=Platform.WORKFRONT_FUSION,
        function_name="filters.content.text_content",
        data=combined_text,
    )


def _extract_filter_conditions(filter_data: Dict[str, Any]) -> List[str]:
    """Extract text from filter condition structure."""
    text_parts = []

    # Filter name at top level
    if "name" in filter_data:
        text_parts.append(f"Filter: {filter_data['name']}")

    # Extract from conditions array
    conditions = filter_data.get("conditions", [])
    if isinstance(conditions, list):
        for group_idx, condition_group in enumerate(conditions):
            if isinstance(condition_group, list):
                text_parts.append(f"--- Condition Group {group_idx + 1} ---")
                for condition_idx, condition in enumerate(condition_group):
                    if isinstance(condition, dict):
                        text_parts.append(f"Condition {condition_idx + 1}:")

                        a = condition.get("a", "")
                        if a and isinstance(a, str):
                            text_parts.append(f"  Left Value: {a}")

                        o = condition.get("o", "")
                        if o and isinstance(o, str):
                            text_parts.append(f"  Operator: {o}")

                        b = condition.get("b", "")
                        if b and isinstance(b, str):
                            text_parts.append(f"  Right Value: {b}")

    return text_parts
