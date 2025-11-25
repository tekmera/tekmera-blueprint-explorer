"""Workfront Fusion connection text content extraction (strict literal)."""

import json
from typing import Any, Dict, List

from .....meta.types import ModuleComponent, ModuleResult, Platform, create_module_result


def text_content(
    module_component: ModuleComponent, platform: Platform
) -> ModuleResult[str]:
    """
    Literal text extraction for Workfront Fusion connection components.
    No inference, no guessing, no classification.
    Only extracts raw text-bearing fields exactly as they appear.
    """
    text_parts: List[str] = []

    # Basic component identifiers
    text_parts.append(f"Module ID: {module_component.id}")
    text_parts.append(f"Module Type: {module_component.module_type}")
    text_parts.append(f"Context: {module_component.extraction_context}")

    raw = module_component.raw_data

    # Extract connection ID if present
    params = raw.get("parameters", {})
    conn_id = params.get("__IMTCONN__")
    if conn_id is not None:
        text_parts.append(f"__IMTCONN__: {conn_id}")

    # Extract raw metadata.restore label if present
    metadata = raw.get("metadata", {})
    restore = metadata.get("restore", {})
    conn_restore = restore.get("__IMTCONN__", {})

    if isinstance(conn_restore, dict):
        # Extract label literally
        label = conn_restore.get("label")
        if label:
            text_parts.append(f"Label: {label}")

        # Extract any other literal key/value fields directly
        for k, v in conn_restore.items():
            if k == "label":
                continue
            text_parts.append(f"{k}: {v}")

    # Dump raw metadata.parameters definitions literally
    param_defs = metadata.get("parameters", [])
    if isinstance(param_defs, list):
        for param_def in param_defs:
            # Only extract literal string-bearing fields
            name = param_def.get("name")
            if name:
                text_parts.append(f"Parameter Name: {name}")

            label = param_def.get("label")
            if label:
                text_parts.append(f"Parameter Label: {label}")

            desc = param_def.get("description")
            if desc:
                text_parts.append(f"Parameter Description: {desc}")

    # Fallback to raw JSON to guarantee search coverage
    if len(text_parts) <= 3:  # Only ID/type/context found
        text_parts.append(json.dumps(raw, sort_keys=True))

    combined = "\n".join(text_parts)

    return create_module_result(
        module=raw,
        platform=platform,
        function_name="connections.content.text_content",
        data=combined,
    )
