"""Workfront Fusion filter text content extraction (strict literal)."""

import json
from typing import Any, Dict, List

from .....meta.types import FilterComponent, ModuleResult, Platform, create_module_result


def text_content(filter_component: FilterComponent) -> ModuleResult[str]:
    """
    Literal text extraction from a Workfront Fusion filter.
    No invented headings, no interpretation.
    Only emits raw strings and raw field values.
    """
    text_parts: List[str] = []

    # Basic Tekmera component metadata (safe, non-inferred)
    text_parts.append(f"Filter ID: {filter_component.id}")
    text_parts.append(f"Filter Name: {filter_component.filter_name}")
    text_parts.append(f"Context: {filter_component.extraction_context}")

    raw = filter_component.raw_data
    filter_data = raw.get("filter", {})

    # Extract literal fields from the filter object
    for key, value in filter_data.items():
        # Conditions handled separately
        if key != "conditions":
            text_parts.append(f"{key}: {value}")

    # Extract literal condition fields
    conditions = filter_data.get("conditions", [])
    if isinstance(conditions, list):
        for group in conditions:
            if isinstance(group, list):
                for condition in group:
                    if isinstance(condition, dict):
                        for cond_key, cond_value in condition.items():
                            # emit literal key/value exactly as-is
                            text_parts.append(f"{cond_key}: {cond_value}")

    # Extract designer metadata literally
    designer = raw.get("metadata", {}).get("designer", {})
    if isinstance(designer, dict):
        for key, value in designer.items():
            text_parts.append(f"{key}: {value}")

    # Fallback to raw JSON if text_parts has very little actual content
    if len(text_parts) <= 3:
        text_parts.append(json.dumps(raw, sort_keys=True))

    combined = "\n".join(text_parts)

    return create_module_result(
        module=raw,
        platform=Platform.WORKFRONT_FUSION,
        function_name="filters.content.text_content",
        data=combined,
    )
