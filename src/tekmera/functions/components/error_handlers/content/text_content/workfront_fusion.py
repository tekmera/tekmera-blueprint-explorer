"""Workfront Fusion error handler text content extraction."""

import json
from typing import Any, Dict, List

from .....meta.types import ErrorHandlerComponent, ModuleResult, Platform, create_module_result


def text_content(error_handler_component: ErrorHandlerComponent) -> ModuleResult[str]:
    """
    Extract text content from Workfront Fusion error handler component.

    Extracts text from:
    - Error handler module types and configurations
    - Retry settings (count, interval, retry flags)
    - Error handling parameters and conditions
    - Component metadata and designer names
    """
    text_parts = []

    # Use typed component properties
    text_parts.append(f"Error Handler ID: {error_handler_component.id}")
    text_parts.append(f"Handlers Count: {error_handler_component.handlers_count}")
    text_parts.append(f"Handler Types: {', '.join(error_handler_component.handler_types)}")
    text_parts.append(f"Context: {error_handler_component.extraction_context}")

    # Extract from the raw error handler data
    raw_item = error_handler_component.raw_data

    # Extract from the onerror array
    onerror_handlers = raw_item.get("onerror", [])
    for handler_idx, handler in enumerate(onerror_handlers):
        if isinstance(handler, dict):
            handler_text = _extract_error_handler_text(handler, handler_idx + 1)
            if handler_text:
                text_parts.extend(handler_text)

    # Extract from item metadata
    metadata = raw_item.get("metadata", {})
    designer = metadata.get("designer", {})
    if "name" in designer:
        text_parts.append(f"Parent Module Designer Name: {designer['name']}")

    # Fallback to JSON if no structured text found
    if not text_parts:
        text_parts.append(json.dumps(error_handler_component.raw_data, sort_keys=True))

    combined_text = "\n".join(text_parts)

    return create_module_result(
        module=error_handler_component.raw_data,
        platform=Platform.WORKFRONT_FUSION,
        function_name="error_handlers.content.text_content",
        data=combined_text,
    )


def _extract_error_handler_text(handler: Dict[str, Any], handler_number: int) -> List[str]:
    """Extract text from individual error handler module."""
    text_parts = [f"--- Error Handler {handler_number} ---"]

    # Handler module type
    if "module" in handler:
        text_parts.append(f"Module: {handler['module']}")

    # Extract from mapper (retry configurations, etc.)
    mapper = handler.get("mapper", {})
    if isinstance(mapper, dict):
        # Retry configuration
        if "retry" in mapper:
            retry_value = mapper["retry"]
            text_parts.append(f"Retry: {retry_value}")

        if "count" in mapper:
            count_value = mapper["count"]
            text_parts.append(f"Retry Count: {count_value}")

        if "interval" in mapper:
            interval_value = mapper["interval"]
            text_parts.append(f"Retry Interval: {interval_value}")

        # Other mapper fields
        for key, value in mapper.items():
            if key not in ["retry", "count", "interval"]:
                if isinstance(value, str) and value.strip():
                    text_parts.append(f"{key}: {value}")
                elif isinstance(value, (bool, int, float)):
                    text_parts.append(f"{key}: {str(value)}")

    # Extract from parameters
    parameters = handler.get("parameters", {})
    if isinstance(parameters, dict):
        for key, value in parameters.items():
            if isinstance(value, str) and value.strip():
                text_parts.append(f"Parameter {key}: {value}")
            elif isinstance(value, (bool, int, float)):
                text_parts.append(f"Parameter {key}: {str(value)}")

    # Handler-specific metadata
    handler_metadata = handler.get("metadata", {})
    if isinstance(handler_metadata, dict):
        designer = handler_metadata.get("designer", {})
        if isinstance(designer, dict) and "name" in designer:
            text_parts.append(f"Handler Designer Name: {designer['name']}")

    return text_parts
