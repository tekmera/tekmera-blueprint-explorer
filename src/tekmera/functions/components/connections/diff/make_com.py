"""Make.com connection-specific diff analysis."""

from typing import Any, Dict, List
from . import ConnectionDifference


def analyze_make_com_connection(old_module: Dict[str, Any], new_module: Dict[str, Any]) -> List[ConnectionDifference]:
    """
    Analyze differences between Make.com connection configurations.
    
    Focuses on service-specific connection parameter changes and metadata.
    """
    differences = []
    
    # Find connection parameters in both modules
    old_conn_param, old_conn_id = _find_connection_parameter(old_module)
    new_conn_param, new_conn_id = _find_connection_parameter(new_module)
    
    # Analyze connection ID changes
    if old_conn_id != new_conn_id:
        # Get connection labels for user-friendly description
        old_label = _get_connection_label(old_module, old_conn_param)
        new_label = _get_connection_label(new_module, new_conn_param)
        
        # Format connection display with label and ID
        old_display = _format_connection_display(old_label, old_conn_id)
        new_display = _format_connection_display(new_label, new_conn_id)
        
        # Determine field path
        field_path = f"parameters.{new_conn_param or old_conn_param or 'connection'}"
        
        differences.append(ConnectionDifference(
            field_path=field_path,
            old_value=old_conn_id,
            new_value=new_conn_id,
            change_type="modified" if old_conn_id and new_conn_id else ("removed" if old_conn_id else "added"),
            significance="critical",
            description=f"Make.com connection changed from {old_display} to {new_display}",
            impact_assessment="breaks_connectivity"
        ))
    
    # Analyze connection parameter name changes (indicates service type change)
    if old_conn_param != new_conn_param and old_conn_param and new_conn_param:
        differences.append(ConnectionDifference(
            field_path="connection_parameter",
            old_value=old_conn_param,
            new_value=new_conn_param,
            change_type="modified",
            significance="critical",
            description=f"Connection parameter changed from '{old_conn_param}' to '{new_conn_param}' (service type change)",
            impact_assessment="breaks_connectivity"
        ))
    
    # Analyze connection label/metadata changes
    old_label = _get_connection_label(old_module, old_conn_param)
    new_label = _get_connection_label(new_module, new_conn_param)
    
    if old_label != new_label and old_label and new_label:
        significance, impact = _assess_make_label_change(old_label, new_label)
        
        differences.append(ConnectionDifference(
            field_path=f"metadata.restore.parameters.{new_conn_param or old_conn_param}.label",
            old_value=old_label,
            new_value=new_label,
            change_type="modified",
            significance=significance,
            description=f"Connection label changed from '{old_label}' to '{new_label}'",
            impact_assessment=impact
        ))
    
    # Analyze connection type/service changes
    old_conn_types = _get_connection_types(old_module, old_conn_param)
    new_conn_types = _get_connection_types(new_module, new_conn_param)
    
    if old_conn_types != new_conn_types and old_conn_types and new_conn_types:
        differences.append(ConnectionDifference(
            field_path=f"metadata.restore.parameters.{new_conn_param or old_conn_param}.data.connection",
            old_value=old_conn_types,
            new_value=new_conn_types,
            change_type="modified",
            significance="critical",
            description=f"Connection service type changed from '{old_conn_types}' to '{new_conn_types}'",
            impact_assessment="breaks_connectivity"
        ))
    
    return differences


def _find_connection_parameter(module: Dict[str, Any]) -> tuple[str, Any]:
    """
    Find the connection parameter in a Make.com module.
    
    Returns:
        Tuple of (parameter_name, connection_id) or (None, None) if no connection
    """
    parameters = module.get("parameters", {})
    metadata = module.get("metadata", {})
    param_definitions = metadata.get("parameters", [])
    
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


def _get_connection_label(module: Dict[str, Any], conn_param: str) -> str:
    """Get connection label from Make.com module metadata."""
    if not conn_param:
        return ""
    
    restore_data = module.get("metadata", {}).get("restore", {}).get("parameters", {})
    conn_restore = restore_data.get(conn_param, {})
    
    return conn_restore.get("label", "")


def _get_connection_types(module: Dict[str, Any], conn_param: str) -> str:
    """Get connection types from Make.com module metadata."""
    if not conn_param:
        return ""
    
    # Try restore data first
    restore_data = module.get("metadata", {}).get("restore", {}).get("parameters", {})
    conn_restore = restore_data.get(conn_param, {})
    conn_types = conn_restore.get("data", {}).get("connection", "")
    
    if conn_types:
        return conn_types
    
    # Try parameter definition
    param_definitions = module.get("metadata", {}).get("parameters", [])
    for param_def in param_definitions:
        if param_def.get("name") == conn_param:
            param_type = param_def.get("type", "")
            if ":" in param_type:
                return param_type.split(":", 1)[1]
    
    return ""


def _assess_make_label_change(old_label: str, new_label: str) -> tuple[str, str]:
    """
    Assess the significance of a Make.com connection label change.
    
    Returns:
        Tuple of (significance, impact_assessment)
    """
    old_lower = old_label.lower()
    new_lower = new_label.lower()
    
    # Extract email addresses for user context comparison
    old_email = _extract_email_from_label(old_label)
    new_email = _extract_email_from_label(new_label)
    
    if old_email != new_email and old_email and new_email:
        return "important", "changes_auth"
    
    # Check for service provider changes
    old_provider = _extract_service_provider(old_label)
    new_provider = _extract_service_provider(new_label)
    
    if old_provider != new_provider and old_provider and new_provider:
        return "critical", "breaks_connectivity"
    
    # Check for OAuth vs other auth method changes
    old_has_oauth = "oauth" in old_lower
    new_has_oauth = "oauth" in new_lower
    
    if old_has_oauth != new_has_oauth:
        return "important", "changes_auth"
    
    # Otherwise, cosmetic change
    return "cosmetic", "cosmetic_only"


def _extract_email_from_label(label: str) -> str:
    """Extract email address from Make.com connection label."""
    import re
    
    # Look for email pattern in parentheses or elsewhere
    email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    match = re.search(email_pattern, label)
    
    return match.group(1) if match else ""


def _extract_service_provider(label: str) -> str:
    """Extract service provider from Make.com connection label."""
    label_lower = label.lower()
    
    # Common service providers
    providers = {
        "google": ["google", "gmail"],
        "microsoft": ["microsoft", "outlook", "office365"],
        "apple": ["apple", "icloud"],
        "yahoo": ["yahoo"],
        "aws": ["aws", "amazon"],
        "azure": ["azure"],
        "salesforce": ["salesforce"],
        "slack": ["slack"],
        "discord": ["discord"],
        "telegram": ["telegram"]
    }
    
    for provider, keywords in providers.items():
        if any(keyword in label_lower for keyword in keywords):
            return provider
    
    return ""


def get_make_com_connection_requirements(module_type: str) -> Dict[str, Any]:
    """
    Get connection requirements for a Make.com module type.
    
    Returns:
        Dictionary with connection requirements and constraints
    """
    module_lower = module_type.lower()
    
    if "email" in module_lower:
        return {
            "required": True,
            "connection_types": ["imap", "smtp", "google", "microsoft"],
            "auth_methods": ["oauth", "app_password"],
            "permissions_needed": ["read_email", "send_email"]
        }
    elif "google" in module_lower:
        return {
            "required": True,
            "connection_types": ["google", "google-restricted"],
            "auth_methods": ["oauth"],
            "permissions_needed": ["google_api_access"]
        }
    elif "microsoft" in module_lower:
        return {
            "required": True,
            "connection_types": ["microsoft", "office365"],
            "auth_methods": ["oauth"],
            "permissions_needed": ["microsoft_graph_access"]
        }
    elif "http" in module_lower:
        return {
            "required": False,
            "connection_types": ["http", "api"],
            "auth_methods": ["api_key", "oauth", "basic_auth", "none"],
            "permissions_needed": ["api_access"]
        }
    else:
        return {
            "required": False,
            "connection_types": ["unknown"],
            "auth_methods": ["unknown"],
            "permissions_needed": []
        }


def _format_connection_display(label: str, connection_id: Any) -> str:
    """Format connection for user-friendly display with label and ID."""
    if not label or label == "":
        # No label available, just show ID
        return str(connection_id) if connection_id else "Unknown"
    
    # Extract meaningful part of label (remove redundant text)
    clean_label = _clean_connection_label(label)
    
    if connection_id:
        return f"'{clean_label}' ({connection_id})"
    else:
        return f"'{clean_label}'"


def _clean_connection_label(label: str) -> str:
    """Clean up connection label for display."""
    if not label:
        return "Unknown Connection"
    
    # Remove common redundant prefixes/suffixes
    clean = label.strip()
    
    # Remove "My " prefix
    if clean.lower().startswith("my "):
        clean = clean[3:]
    
    # Remove " connection" suffix
    if clean.lower().endswith(" connection"):
        clean = clean[:-11]
    
    # Remove " OAuth connection" suffix
    if clean.lower().endswith(" oauth connection"):
        clean = clean[:-17]
    
    # Don't limit length - HTML formatter will handle display properly
    return clean