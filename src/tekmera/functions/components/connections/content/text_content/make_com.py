"""Make.com connection text content extraction."""

import json
from typing import Any, Dict, List

from .....meta.types import ModuleComponent, ModuleResult, Platform, create_module_result


def text_content(module_component: ModuleComponent, platform: Platform) -> ModuleResult[str]:
    """
    Extract text content from Make.com connection component.

    Extracts text from:
    - Connection ID and parameter names
    - Connection labels and service information
    - Email addresses and user context
    - Service providers and authentication types
    """
    text_parts = []

    # Use typed component properties
    text_parts.append(f"Module ID: {module_component.id}")
    text_parts.append(f"Module Type: {module_component.module_type}")
    text_parts.append(f"Context: {module_component.extraction_context}")

    # Extract detailed text from raw module data
    raw_module = module_component.raw_data
    connection_text = _extract_make_com_connection_text(raw_module)
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


def _extract_make_com_connection_text(module: Dict[str, Any]) -> List[str]:
    """Extract detailed text content from a Make.com connection."""
    text_parts = []

    # Find connection parameter
    parameters = module.get("parameters", {})
    metadata = module.get("metadata", {})
    param_definitions = metadata.get("parameters", [])
    
    connection_param_name, connection_id = _find_connection_parameter(parameters, param_definitions)
    
    if connection_param_name and connection_id:
        text_parts.append(f"Connection ID: {connection_id}")
        text_parts.append(f"Connection Parameter: {connection_param_name}")

        # Extract connection metadata
        restore_data = metadata.get("restore", {}).get("parameters", {})
        connection_restore = restore_data.get(connection_param_name, {})
        
        if connection_restore:
            # Connection label
            label = connection_restore.get("label", "")
            if label:
                text_parts.append(f"Connection Label: {label}")
                
                # Extract structured info from label
                email = _extract_email(label)
                if email:
                    text_parts.append(f"User Email: {email}")
                    
                    # Extract domain for provider context
                    domain = email.split("@")[1] if "@" in email else ""
                    if domain:
                        text_parts.append(f"Email Domain: {domain}")
                
                provider = _extract_service_provider(label)
                if provider:
                    text_parts.append(f"Service Provider: {provider}")
                
                auth_method = _extract_auth_method(label)
                if auth_method:
                    text_parts.append(f"Authentication: {auth_method}")

            # Connection type information
            conn_data = connection_restore.get("data", {})
            if conn_data:
                connection_type = conn_data.get("connection", "")
                if connection_type:
                    text_parts.append(f"Connection Type: {connection_type}")
                
                scoped = conn_data.get("scoped", "")
                if scoped:
                    text_parts.append(f"Scoped Access: {scoped}")

        # Extract supported connection types from parameter definition
        for param_def in param_definitions:
            if param_def.get("name") == connection_param_name:
                param_type = param_def.get("type", "")
                if param_type.startswith("account:"):
                    supported_types = param_type[8:]  # Remove "account:" prefix
                    text_parts.append(f"Supported Types: {supported_types}")
                
                required = param_def.get("required", False)
                text_parts.append(f"Required: {'Yes' if required else 'No'}")
                
                param_label = param_def.get("label", "")
                if param_label and param_label != "Connection":
                    text_parts.append(f"Parameter Label: {param_label}")

    # Extract module type for connection context
    module_type = module.get("module", "")
    if module_type:
        text_parts.append(f"Service Type: {module_type}")
        
        # Add connection category
        category = _get_connection_category(module_type)
        text_parts.append(f"Connection Category: {category}")

    return text_parts


def _find_connection_parameter(parameters: Dict[str, Any], param_definitions: List[Dict[str, Any]]) -> tuple[str, Any]:
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


def _extract_email(label: str) -> str:
    """Extract email address from Make.com connection label."""
    import re
    
    # Look for email pattern
    email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    match = re.search(email_pattern, label)
    
    return match.group(1) if match else ""


def _extract_service_provider(label: str) -> str:
    """Extract service provider from Make.com connection label."""
    label_lower = label.lower()
    
    # Common service providers with their detection keywords
    providers = {
        "Google": ["google", "gmail"],
        "Microsoft": ["microsoft", "outlook", "office365", "office 365"],
        "Apple": ["apple", "icloud"],
        "Yahoo": ["yahoo"],
        "Amazon": ["aws", "amazon"],
        "Azure": ["azure"],
        "Salesforce": ["salesforce"],
        "Slack": ["slack"],
        "Discord": ["discord"],
        "Telegram": ["telegram"],
        "SMTP": ["smtp"],
        "IMAP": ["imap"],
        "HTTP": ["http"],
        "FTP": ["ftp", "sftp"]
    }
    
    for provider, keywords in providers.items():
        if any(keyword in label_lower for keyword in keywords):
            return provider
    
    return ""


def _extract_auth_method(label: str) -> str:
    """Extract authentication method from Make.com connection label."""
    label_lower = label.lower()
    
    if "oauth" in label_lower:
        return "OAuth"
    elif "api key" in label_lower:
        return "API Key"
    elif "basic" in label_lower:
        return "Basic Auth"
    elif "token" in label_lower:
        return "Token"
    else:
        return ""


def _get_connection_category(module_type: str) -> str:
    """Get human-readable connection category from module type."""
    module_lower = module_type.lower()
    
    if "email" in module_lower:
        if "trigger" in module_lower or "watch" in module_lower:
            return "Email Trigger"
        else:
            return "Email Service"
    elif "google" in module_lower:
        return "Google Service"
    elif "microsoft" in module_lower:
        return "Microsoft Service"
    elif "http" in module_lower:
        return "HTTP API"
    elif "webhook" in module_lower:
        return "Webhook"
    elif "database" in module_lower or "sql" in module_lower:
        return "Database"
    elif "ftp" in module_lower or "sftp" in module_lower:
        return "File Transfer"
    elif "builtin" in module_lower:
        return "Built-in Function"
    else:
        return "API Service"