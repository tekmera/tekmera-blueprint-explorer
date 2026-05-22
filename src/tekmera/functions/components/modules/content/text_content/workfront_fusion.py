"""Workfront Fusion module text content extraction (strict literal with structured entries)."""

import json
from typing import Any, List, Tuple

from .....meta.types import ModuleComponent, ModuleResult, Platform, create_module_result


def text_content(
    module_component: ModuleComponent,
    platform: Platform,
) -> ModuleResult[str]:
    """
    Literal text extraction for Workfront Fusion modules with structured entries.
    Produces:
    - Combined literal text (for backward compatibility)
    - Structured (field_path, value) entries (for precise field-level search)
    """
    text_parts: List[str] = []

    # Tekmera metadata (safe and expected)
    text_parts.append(f"Module ID: {module_component.id}")
    text_parts.append(f"Module Type: {module_component.module_type}")
    text_parts.append(f"Context: {module_component.extraction_context}")

    raw = module_component.raw_data

    # Extract structured entries for field-level search
    literal_entries: List[Tuple[str, str]] = []
    _extract_literal_fields(raw, "", literal_entries)

    # Add entries to text output for backward compatibility
    for field_path, value in literal_entries:
        text_parts.append(f"{field_path}: {value}")

    # Fallback if nothing but metadata was found
    if len(literal_entries) == 0:
        text_parts.append(json.dumps(raw, sort_keys=True))

    return create_module_result(
        module=raw,
        platform=platform,
        function_name="modules.content.text_content",
        data="\n".join(text_parts),
        entries=literal_entries,  # Structured entries for precise search
    )


def _extract_literal_fields(
    obj: Any,
    prefix: str,
    out: List[Tuple[str, str]],
) -> None:
    """
    Recursively extract literal string-bearing fields as structured entries.
    STRICT RULES:
    - No inferred labels
    - No renaming keys
    - No headings
    - Only literal (field_path, value) tuples
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            field_path = f"{prefix}.{key}" if prefix else key

            if isinstance(value, str):
                out.append((field_path, value))

            _extract_literal_fields(value, field_path, out)

    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            field_path = f"{prefix}[{idx}]"
            _extract_literal_fields(item, field_path, out)
