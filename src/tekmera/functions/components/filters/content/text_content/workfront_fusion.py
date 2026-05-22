"""Workfront Fusion filter text content extraction (strict literal)."""

import json
from typing import List, Tuple

from .....meta.types import FilterComponent, ModuleResult, Platform, create_module_result


def text_content(filter_component: FilterComponent) -> ModuleResult[str]:
    """
    Literal text extraction from a Workfront Fusion filter.
    No headings, no interpretation, no operator mapping.
    Only emits literal strings and raw field values.
    """
    text_parts: List[str] = []
    literal_entries: List[Tuple[str, str]] = []

    # Tekmera metadata
    text_parts.append(f"Filter ID: {filter_component.id}")
    text_parts.append(f"Filter Name: {filter_component.filter_name}")
    text_parts.append(f"Context: {filter_component.extraction_context}")

    raw = filter_component.raw_data
    filter_data = raw.get("filter", {})

    # Literal root-level filter fields (not conditions)
    for key, value in filter_data.items():
        if key != "conditions" and isinstance(value, str):
            field_path = f"filter.{key}"
            literal_entries.append((field_path, value))
            text_parts.append(f"{field_path}: {value}")

    # Literal conditions extraction only
    conditions = filter_data.get("conditions", [])
    if isinstance(conditions, list):
        for group_idx, group in enumerate(conditions):
            if isinstance(group, list):
                for cond_idx, condition in enumerate(group):
                    if isinstance(condition, dict):
                        for cond_key, cond_value in condition.items():
                            if isinstance(cond_value, str):
                                field_path = (
                                    f"filter.conditions[{group_idx}][{cond_idx}].{cond_key}"
                                )
                                literal_entries.append((field_path, cond_value))
                                text_parts.append(f"{field_path}: {cond_value}")

    # Designer metadata
    designer = raw.get("metadata", {}).get("designer", {})
    if isinstance(designer, dict):
        for key, value in designer.items():
            if isinstance(value, str):
                field_path = f"metadata.designer.{key}"
                literal_entries.append((field_path, value))
                text_parts.append(f"{field_path}: {value}")

    # Fallback
    if len(text_parts) <= 3:
        text_parts.append(json.dumps(raw, sort_keys=True))

    combined = "\n".join(text_parts)

    return create_module_result(
        module=raw,
        platform=Platform.WORKFRONT_FUSION,
        function_name="filters.content.text_content",
        data=combined,
        entries=literal_entries,
    )
