"""Workfront Fusion connection text content extraction."""

import json
from typing import Any, Dict, List

from .....meta.types import ModuleComponent, ModuleResult, Platform, create_module_result


def text_content(module_component: ModuleComponent, platform: Platform) -> ModuleResult[str]:
    """
    Extract text content from Workfront Fusion connection component.

    Extracts text from:
    - Connection ID and parameter names
    - Connection labels and descriptions
    - Server/instance information
    - User context and authentication details
    """
    text_parts = []

    # Use typed component properties
    text_parts.append(f"Module ID: {module_component.id}")
    text_parts.append(f"Module Type: {module_component.module_type}")
    text_parts.append(f"Context: {module_component.extraction_context}")

    # Extract detailed text from raw module data
    raw_module = module_component.raw_data
    connection_text = _extract_workfront_connection_text(raw_module)
    text_parts.extend(connection_text)

    # Fallback to JSON if no structured text found
    if len(text_parts) <= 3:  # Only basic component info
        text_parts.append(json.dumps(raw_module, sort_keys=True))

    combined_text = "\n".join(text_parts)

    return create_module_result(
        module=raw_module,
        platform=platform,
        function_name="connections.content.text_content",
        data=combined_text,
    )


def _extract_workfront_connection_text(module: Dict[str, Any]) -> List[str]:
    """Extract detailed text content from a Workfront Fusion connection."""
    text_parts = []

    # Extract connection ID
    parameters = module.get("parameters", {})
    connection_id = parameters.get("__IMTCONN__")
    if connection_id:
        text_parts.append(f"Connection ID: {connection_id}")
        text_parts.append("Connection Parameter: __IMTCONN__")

    # Extract connection metadata
    metadata = module.get("metadata", {})
    restore_data = metadata.get("restore", {})
    connection_restore = restore_data.get("__IMTCONN__", {})
    
    if connection_restore:
        # Connection label (contains server and user info)
        label = connection_restore.get("label", "")
        if label:
            text_parts.append(f"Connection Label: {label}")
            
            # Parse and extract structured info from label
            server_info = _extract_server_info(label)
            if server_info:
                text_parts.append(f"Workfront Server: {server_info}")
            
            user_info = _extract_user_info(label)
            if user_info:
                text_parts.append(f"User Context: {user_info}")

    # Extract module type for connection context
    module_type = module.get("module", "")
    if module_type:
        text_parts.append(f"Service Type: {module_type}")
        
        # Add connection category
        category = _get_connection_category(module_type)
        text_parts.append(f"Connection Category: {category}")

    # Extract any additional authentication context
    param_definitions = metadata.get("parameters", [])
    for param_def in param_definitions:
        if param_def.get("name") == "__IMTCONN__":
            param_type = param_def.get("type", "")
            if param_type:
                text_parts.append(f"Auth Type: {param_type}")
            
            required = param_def.get("required", False)
            text_parts.append(f"Required: {'Yes' if required else 'No'}")

    return text_parts


def _extract_server_info(label: str) -> str:
    """Extract Workfront server information from connection label."""
    import re
    
    # Look for Workfront server patterns
    patterns = [
        r'([^|\s]+\.workfront\.com)',  # server.workfront.com
        r'([^|\s]+\.my\.workfront\.com)',  # server.my.workfront.com
    ]
    
    for pattern in patterns:
        match = re.search(pattern, label)
        if match:
            return match.group(1)
    
    return ""


def _extract_user_info(label: str) -> str:
    """Extract user information from Workfront connection label."""
    import re
    
    # Look for user patterns - typically before pipe or in parentheses
    patterns = [
        r'([^|]+)\s*\|\s*[^|]+\.workfront\.com',  # user | server.workfront.com
        r'\(([^)]+)\)',  # (user info)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, label)
        if match:
            user_info = match.group(1).strip()
            # Filter out obvious non-user strings
            if not any(keyword in user_info.lower() for keyword in ["connection", "prod", "test", "staging"]):
                return user_info
    
    return ""


def _get_connection_category(module_type: str) -> str:
    """Get human-readable connection category from module type."""
    module_lower = module_type.lower()
    
    if "workfront" in module_lower:
        if "watch" in module_lower:
            return "Workfront Trigger"
        elif "search" in module_lower:
            return "Workfront Search"
        elif "create" in module_lower or "update" in module_lower:
            return "Workfront CRUD"
        else:
            return "Workfront API"
    elif "http" in module_lower:
        return "HTTP API"
    elif "webhook" in module_lower:
        return "Webhook"
    elif "email" in module_lower:
        return "Email Service"
    elif "database" in module_lower or "sql" in module_lower:
        return "Database"
    elif "ftp" in module_lower or "sftp" in module_lower:
        return "File Transfer"
    else:
        return "API Service"