"""Workfront Fusion router text content extraction (strict literal)."""

import json
from typing import Any, Dict, List

from .....meta.types import RouterComponent, ModuleResult, Platform, create_module_result


def text_content(router: RouterComponent) -> ModuleResult[str]:
    """
    Literal text extraction for Workfront Fusion router components.
    No inference, no headings, no labels, no interpretation.
    Only emits:
    - Tekmera component metadata (ID, context)
    - Raw string-bearing values from router JSON
    - Raw JSON fallback
    """
    text_parts: List[str] = []

    # Tekmera router metadata (safe to include)
    text_parts.append(f"Router ID: {router.id}")
    text_parts.append(f"Context: {router.extraction_context}")

    raw = router.raw_data

    # Extract literal string values from entire router structure and collect structured entries
    literal_entries: List[tuple] = []
    text_parts.extend(_extract_literal_fields(raw, "", literal_entries))

    # Fallback if nothing but metadata was produced
    if len(text_parts) <= 2:
        text_parts.append(json.dumps(raw, sort_keys=True))

    return create_module_result(
        module=raw,
        platform=Platform.WORKFRONT_FUSION,
        function_name="routers.content.text_content",
        data="\n".join(text_parts),
        entries=literal_entries,  # Add structured entries for precise search
    )


def _extract_literal_fields(obj: Any, prefix: str = "", entries: List[tuple] = None) -> List[str]:
    """
    Recursively extract literal string-bearing fields.
    Does not invent labels, headings, or structure.
    Also collects structured entries for precise search.
    """
    if entries is None:
        entries = []
    
    text_parts: List[str] = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else key

            # Emit literal string values
            if isinstance(value, str):
                text_parts.append(f"{path}: {value}")
                # Add to structured entries for precise search
                entries.append((path, value))

            # Recurse
            text_parts.extend(_extract_literal_fields(value, path, entries))

    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            path = f"{prefix}[{idx}]"
            text_parts.extend(_extract_literal_fields(item, path, entries))

    return text_parts
