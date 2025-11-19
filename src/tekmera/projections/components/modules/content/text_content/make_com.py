"""Make.com module text content extraction."""

import json
from typing import Any, Dict, List

from .....meta.types import ModuleComponent, ModuleResult, Platform, create_module_result


def text_content(module_component: ModuleComponent, platform: Platform) -> ModuleResult[str]:
    """
    Extract text content from Make.com module component.

    Extracts text from:
    - Module type and parameters
    - Variable names and values
    - Mapper configurations
    - Designer metadata and names
    - Filter conditions
    """
    text_parts = []

    # Use typed component properties
    text_parts.append(f"Module ID: {module_component.id}")
    text_parts.append(f"Module Type: {module_component.module_type}")
    text_parts.append(f"Context: {module_component.extraction_context}")

    # Extract detailed text from raw module data
    raw_module = module_component.raw_data
    module_text = _extract_module_text(raw_module)
    text_parts.extend(module_text)

    # Fallback to JSON if no structured text found
    if len(text_parts) <= 3:  # Only basic component info
        text_parts.append(json.dumps(raw_module, sort_keys=True))

    combined_text = "\n".join(text_parts)

    return create_module_result(
        module=raw_module,
        platform=platform,
        function_name="modules.content.text_content",
        data=combined_text,
    )


def _extract_module_text(module: Dict[str, Any]) -> List[str]:
    """Extract detailed text content from a Make.com module."""
    text_parts = []

    # Module type
    if "module" in module:
        text_parts.append(f"Module: {module['module']}")

    # Extract from mapper (Make.com uses similar structure to Fusion)
    mapper = module.get("mapper", {})
    if isinstance(mapper, dict):
        # Variables
        if "variables" in mapper and isinstance(mapper["variables"], list):
            for var in mapper["variables"]:
                if isinstance(var, dict):
                    name = var.get("name", "")
                    value = var.get("value", "")
                    if name:
                        text_parts.append(f"Variable: {name}")
                    if value and isinstance(value, str):
                        text_parts.append(f"Value: {value}")

        # Filters in mapper
        if "filter" in mapper:
            filter_text = _extract_filter_text(mapper["filter"])
            if filter_text:
                text_parts.append("Module Filter:")
                text_parts.extend(filter_text)

        # Other string fields in mapper
        for key, value in mapper.items():
            if key not in ["variables", "filter"] and isinstance(value, str) and value.strip():
                text_parts.append(f"{key}: {value}")

    # Extract from parameters
    parameters = module.get("parameters", {})
    if isinstance(parameters, dict):
        for key, value in parameters.items():
            if isinstance(value, str) and value.strip():
                text_parts.append(f"Parameter {key}: {value}")

    # Designer metadata for this module
    module_metadata = module.get("metadata", {})
    if isinstance(module_metadata, dict):
        designer = module_metadata.get("designer", {})
        if isinstance(designer, dict) and "name" in designer:
            text_parts.append(f"Designer Name: {designer['name']}")

    return text_parts


def _extract_filter_text(filter_data: Any) -> List[str]:
    """Extract text from Make.com filter conditions."""
    text_parts = []

    if isinstance(filter_data, dict):
        # Named filter with conditions
        if "name" in filter_data:
            text_parts.append(f"Filter: {filter_data['name']}")

        conditions = filter_data.get("conditions", [])
        if isinstance(conditions, list):
            for condition_group in conditions:
                if isinstance(condition_group, list):
                    for condition in condition_group:
                        if isinstance(condition, dict):
                            a = condition.get("a", "")
                            b = condition.get("b", "")
                            o = condition.get("o", "")

                            if a and isinstance(a, str):
                                text_parts.append(f"Condition A: {a}")
                            if b and isinstance(b, str):
                                text_parts.append(f"Condition B: {b}")
                            if o and isinstance(o, str):
                                text_parts.append(f"Operator: {o}")

    elif isinstance(filter_data, list):
        # Direct filter array format
        for condition_group in filter_data:
            if isinstance(condition_group, list):
                for condition in condition_group:
                    if isinstance(condition, dict):
                        a = condition.get("a", "")
                        b = condition.get("b", "")
                        o = condition.get("o", "")

                        if a and isinstance(a, str):
                            text_parts.append(f"Filter A: {a}")
                        if b and isinstance(b, str):
                            text_parts.append(f"Filter B: {b}")
                        if o and isinstance(o, str):
                            text_parts.append(f"Filter Op: {o}")

    return text_parts
