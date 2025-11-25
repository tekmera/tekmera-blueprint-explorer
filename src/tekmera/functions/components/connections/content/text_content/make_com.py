"""Make.com connection text content extraction (strict literal)."""

import json
from typing import Any, Dict, List

from .....meta.types import ModuleComponent, ModuleResult, Platform, create_module_result


def text_content(module_component: ModuleComponent, platform: Platform) -> ModuleResult[str]:
    """
    Literal text extraction for Make.com connection components.
    No inference, no guessing, no classification.
    Only extracts raw text-bearing fields exactly as they appear.
    """
    text_parts: List[str] = []

    # Basic component identifiers
    text_parts.append(f"Module ID: {module_component.id}")
    text_parts.append(f"Module Type: {module_component.module_type}")
    text_parts.append(f"Context: {module_component.extraction_context}")

    raw = module_component.raw_data

    # Extract connection parameters literally
    params = raw.get("parameters", {})
    metadata = raw.get("metadata", {})
    
    # Find and extract connection ID
    connection_param_name, connection_id = _find_connection_parameter(params, metadata.get("parameters", []))
    
    if connection_param_name and connection_id:
        text_parts.append(f"Connection Parameter: {connection_param_name}")
        text_parts.append(f"Connection ID: {connection_id}")

    # Extract raw metadata.restore connection data if present
    restore = metadata.get("restore", {})
    restore_params = restore.get("parameters", {})
    
    if connection_param_name and connection_param_name in restore_params:
        conn_restore = restore_params[connection_param_name]
        if isinstance(conn_restore, dict):
            # Extract label literally
            label = conn_restore.get("label")
            if label:
                text_parts.append(f"Label: {label}")

            # Extract connection data literally
            conn_data = conn_restore.get("data", {})
            if isinstance(conn_data, dict):
                for k, v in conn_data.items():
                    if v:  # Only include non-empty values
                        text_parts.append(f"{k}: {v}")

            # Extract any other literal key/value fields directly
            for k, v in conn_restore.items():
                if k in ["label", "data"]:
                    continue
                if v:
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

            param_type = param_def.get("type")
            if param_type:
                text_parts.append(f"Parameter Type: {param_type}")

            desc = param_def.get("description")
            if desc:
                text_parts.append(f"Parameter Description: {desc}")

            required = param_def.get("required")
            if required is not None:
                text_parts.append(f"Required: {'Yes' if required else 'No'}")

    # Extract module type literally
    module_type = raw.get("module")
    if module_type:
        text_parts.append(f"Module: {module_type}")

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




def _find_connection_parameter(
    parameters: Dict[str, Any], param_definitions: List[Dict[str, Any]]
) -> tuple[str, Any]:
    """Find the connection parameter in Make.com module."""
    # Look for connection parameters using parameter definitions
    for param_def in param_definitions:
        param_name = param_def.get("name", "")
        param_type = param_def.get("type", "")

        if param_type.startswith("account:") and param_name in parameters:
            return param_name, parameters[param_name]

    # Fallback: look for common connection parameters
    common_params = ["account", "connection", "__IMTCONN__"]
    for param_name in common_params:
        if param_name in parameters:
            return param_name, parameters[param_name]

    return None, None
