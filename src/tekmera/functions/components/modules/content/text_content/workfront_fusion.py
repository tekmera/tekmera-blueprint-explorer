"""Workfront Fusion module text content extraction (strict literal)."""

import json
from typing import Any, Dict, List

from .....meta.types import ModuleComponent, ModuleResult, Platform, create_module_result


def text_content(
    module_component: ModuleComponent,
    platform: Platform,
) -> ModuleResult[str]:
    """
    Literal text extraction for Workfront Fusion modules.
    No inference, no headings, no labels, no interpretation.
    Only emits:
    - Tekmera component metadata (ID, type, context)
    - Raw string-bearing field values from the module
    - Raw JSON fallback
    """
    text_parts: List[str] = []

    # Always allowed — Tekmera metadata, not blueprint inference
    text_parts.append(f"Module ID: {module_component.id}")
    text_parts.append(f"Module Type: {module_component.module_type}")
    text_parts.append(f"Context: {module_component.extraction_context}")

    raw = module_component.raw_data

    # Extract literal string values from the module object
    text_parts.extend(_extract_literal_fields(raw))

    # Fallback to raw JSON if nothing beyond ID/type/context was found
    if len(text_parts) <= 3:
        text_parts.append(json.dumps(raw, sort_keys=True))

    return create_module_result(
        module=raw,
        platform=platform,
        function_name="modules.content.text_content",
        data="\n".join(text_parts),
    )


def _extract_literal_fields(obj: Any, prefix: str = "") -> List[str]:
    """
    Recursively extract literal string-bearing fields from the module JSON.
    Does not:
    - rename fields
    - add headings
    - interpret meaning
    - special-case any keys
    - format values beyond str()
    """
    text_parts: List[str] = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            field_path = f"{prefix}.{key}" if prefix else key

            # Emit literal string values
            if isinstance(value, str):
                text_parts.append(f"{field_path}: {value}")

            # Recurse
            text_parts.extend(_extract_literal_fields(value, field_path))

    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            field_path = f"{prefix}[{idx}]"
            text_parts.extend(_extract_literal_fields(item, field_path))

    return text_parts
