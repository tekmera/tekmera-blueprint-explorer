"""Workfront Fusion connection-specific diff analysis."""

from typing import Any, Dict, List
from . import ConnectionDifference


def analyze_workfront_fusion_connection(old_module: Dict[str, Any], new_module: Dict[str, Any]) -> List[ConnectionDifference]:
    """
    Analyze differences between Workfront Fusion connection configurations.
    
    Focuses on __IMTCONN__ parameter changes and related metadata.
    """
    differences = []
    
    # Analyze connection ID changes (critical)
    old_conn_id = old_module.get("parameters", {}).get("__IMTCONN__")
    new_conn_id = new_module.get("parameters", {}).get("__IMTCONN__")
    
    if old_conn_id != new_conn_id:
        # Get connection labels for user-friendly description
        old_restore = old_module.get("metadata", {}).get("restore", {}).get("__IMTCONN__", {})
        new_restore = new_module.get("metadata", {}).get("restore", {}).get("__IMTCONN__", {})
        
        old_label = old_restore.get("label", "")
        new_label = new_restore.get("label", "")
        
        # Format connection display with label and ID
        old_display = _format_connection_display(old_label, old_conn_id)
        new_display = _format_connection_display(new_label, new_conn_id)
        
        differences.append(ConnectionDifference(
            field_path="parameters.__IMTCONN__",
            old_value=old_conn_id,
            new_value=new_conn_id,
            change_type="modified" if old_conn_id and new_conn_id else ("removed" if old_conn_id else "added"),
            significance="critical",
            description=f"Workfront connection changed from {old_display} to {new_display}",
            impact_assessment="breaks_connectivity"
        ))
    
    # Analyze connection label changes (cosmetic but informative)
    old_restore = old_module.get("metadata", {}).get("restore", {}).get("__IMTCONN__", {})
    new_restore = new_module.get("metadata", {}).get("restore", {}).get("__IMTCONN__", {})
    
    old_label = old_restore.get("label", "")
    new_label = new_restore.get("label", "")
    
    if old_label != new_label:
        # Determine if this is just a label change or indicates server/auth changes
        significance, impact = _assess_workfront_label_change(old_label, new_label)
        
        differences.append(ConnectionDifference(
            field_path="metadata.restore.__IMTCONN__.label",
            old_value=old_label,
            new_value=new_label,
            change_type="modified",
            significance=significance,
            description=f"Connection label changed from '{old_label}' to '{new_label}'",
            impact_assessment=impact
        ))
    
    # Analyze module type changes that might affect connection requirements
    old_module_type = old_module.get("module", "")
    new_module_type = new_module.get("module", "")
    
    if old_module_type != new_module_type:
        # Check if this changes connection requirements
        old_category = _get_module_connection_category(old_module_type)
        new_category = _get_module_connection_category(new_module_type)
        
        if old_category != new_category:
            differences.append(ConnectionDifference(
                field_path="module",
                old_value=old_module_type,
                new_value=new_module_type,
                change_type="modified",
                significance="important",
                description=f"Module type changed affecting connection requirements: {old_module_type} → {new_module_type}",
                impact_assessment="changes_auth"
            ))
    
    return differences


def _assess_workfront_label_change(old_label: str, new_label: str) -> tuple[str, str]:
    """
    Assess the significance of a Workfront connection label change.
    
    Returns:
        Tuple of (significance, impact_assessment)
    """
    old_lower = old_label.lower()
    new_lower = new_label.lower()
    
    # Check for server/instance changes
    old_server = _extract_workfront_server(old_label)
    new_server = _extract_workfront_server(new_label)
    
    if old_server != new_server and old_server and new_server:
        return "critical", "breaks_connectivity"
    
    # Check for user/auth context changes
    old_user = _extract_workfront_user(old_label)
    new_user = _extract_workfront_user(new_label)
    
    if old_user != new_user and old_user and new_user:
        return "important", "changes_auth"
    
    # Check for environment changes (prod, test, staging)
    env_keywords = ["prod", "test", "staging", "dev", "sandbox"]
    old_has_env = any(keyword in old_lower for keyword in env_keywords)
    new_has_env = any(keyword in new_lower for keyword in env_keywords)
    
    if old_has_env and new_has_env:
        old_env = [keyword for keyword in env_keywords if keyword in old_lower]
        new_env = [keyword for keyword in env_keywords if keyword in new_lower]
        if old_env != new_env:
            return "important", "changes_auth"
    
    # Otherwise, just a cosmetic label change
    return "cosmetic", "cosmetic_only"


def _extract_workfront_server(label: str) -> str:
    """Extract Workfront server from connection label."""
    import re
    
    # Look for patterns like "server.my.workfront.com"
    server_pattern = r'([^|\s]+\.workfront\.com)'
    match = re.search(server_pattern, label)
    
    return match.group(1) if match else ""


def _extract_workfront_user(label: str) -> str:
    """Extract user context from Workfront connection label."""
    import re
    
    # Look for patterns like "username | server" or "(username)"
    user_patterns = [
        r'([^|]+)\s*\|',  # Before pipe
        r'\(([^)]+)\)',   # In parentheses
    ]
    
    for pattern in user_patterns:
        match = re.search(pattern, label)
        if match:
            user = match.group(1).strip()
            # Filter out obvious non-user strings
            if not any(keyword in user.lower() for keyword in ["connection", "prod", "test", "staging", "sa"]):
                return user
    
    return ""


def _get_module_connection_category(module_type: str) -> str:
    """Get connection category for Workfront Fusion module type."""
    module_lower = module_type.lower()
    
    if "workfront" in module_lower:
        return "workfront_api"
    elif "http" in module_lower:
        return "http_api"
    elif "webhook" in module_lower:
        return "webhook"
    elif "email" in module_lower:
        return "email"
    elif "database" in module_lower or "sql" in module_lower:
        return "database"
    elif "ftp" in module_lower or "sftp" in module_lower:
        return "file_transfer"
    else:
        return "api"


def get_workfront_connection_requirements(module_type: str) -> Dict[str, Any]:
    """
    Get connection requirements for a Workfront Fusion module type.
    
    Returns:
        Dictionary with connection requirements and constraints
    """
    category = _get_module_connection_category(module_type)
    
    requirements = {
        "workfront_api": {
            "required": True,
            "connection_types": ["workfront"],
            "auth_methods": ["api_key", "oauth"],
            "permissions_needed": ["read", "write"]
        },
        "http_api": {
            "required": True,
            "connection_types": ["http", "api"],
            "auth_methods": ["api_key", "oauth", "basic_auth", "bearer_token"],
            "permissions_needed": ["api_access"]
        },
        "webhook": {
            "required": False,
            "connection_types": ["webhook"],
            "auth_methods": ["none", "api_key"],
            "permissions_needed": ["receive_webhooks"]
        },
        "email": {
            "required": True,
            "connection_types": ["email", "smtp", "imap"],
            "auth_methods": ["oauth", "basic_auth"],
            "permissions_needed": ["send_email", "read_email"]
        }
    }
    
    return requirements.get(category, {
        "required": False,
        "connection_types": ["unknown"],
        "auth_methods": ["unknown"],
        "permissions_needed": []
    })


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
    
    # Remove common redundant suffixes
    clean = label.strip()
    if clean.lower().endswith(" connection"):
        clean = clean[:-11]  # Remove " connection"
    
    # Don't limit length - HTML formatter will handle display properly
    return clean