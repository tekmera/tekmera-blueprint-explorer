"""Workfront Fusion error handler text content extraction (strict literal)."""

import json
from typing import Any, List

from .....meta.types import ErrorHandlerComponent, ModuleResult, Platform, create_module_result


def text_content(error_handler_component: ErrorHandlerComponent) -> ModuleResult[str]:
    """
    Literal text extraction for Workfront Fusion error-handler components.
    No inference, no headings, no renaming, no labels.
    Only emits:
    - Tekmera component metadata (ID, context)
    - Literal string-bearing values from raw JSON
    - Raw JSON fallback
    """
    text_parts: List[str] = []

    # Tekmera metadata – not blueprint inference
    text_parts.append(f"Error Handler ID: {error_handler_component.id}")
    text_parts.append(f"Context: {error_handler_component.extraction_context}")

    raw = error_handler_component.raw_data

    # Extract literal string values everywhere in the error-handler structure and collect structured entries
    literal_entries: List[tuple] = []
    text_parts.extend(_extract_literal_fields(raw, "", literal_entries))

    # Fallback if nothing but metadata was extracted
    if len(text_parts) <= 2:
        text_parts.append(json.dumps(raw, sort_keys=True))

    return create_module_result(
        module=raw,
        platform=Platform.WORKFRONT_FUSION,
        function_name="error_handlers.content.text_content",
        data="\n".join(text_parts),
        entries=literal_entries,  # Add structured entries for precise search
    )


def _extract_literal_fields(obj: Any, prefix: str = "", entries: List[tuple] = None) -> List[str]:
    """
    Recursively extract literal string-bearing fields.
    Also collects structured entries for precise search.

    STRICT RULES:
    - Do NOT add labels
    - Do NOT infer meaning
    - Do NOT rename fields
    - Do NOT invent headings
    - Only output: "<field_path>: <string value>"
    """
    if entries is None:
        entries = []

    text_parts: List[str] = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else key

            # Emit literal strings
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
