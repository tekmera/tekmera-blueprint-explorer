"""Make.com connection type implementation."""

import re
from typing import Any, Dict, List

from tekmera.functions.meta.types import Platform
from . import ConnectionComponent


def create_make_com_connection(
    module_id: str,
    platform: Platform,
    extraction_context: str,
    raw_module_data: Dict[str, Any],
) -> ConnectionComponent:
    """
    Create a ConnectionComponent for Make.com.

    Make.com connections use service-specific parameter names with metadata in restore section.
    """
    parameters = raw_module_data.get("parameters", {})
    metadata = raw_module_data.get("metadata", {})
    restore_data = metadata.get("restore", {}).get("parameters", {})
    param_definitions = metadata.get("parameters", [])

    # Find connection parameter
    connection_param_name, connection_id = _find_make_connection_parameter(
        parameters, param_definitions
    )

    if not connection_param_name:
        # Fallback - no connection found
        return ConnectionComponent(
            id=f"{module_id}_connection",
            platform=platform,
            extraction_context=extraction_context,
            raw_data=raw_module_data,
            connection_id="none",
            connection_type="none",
            connection_label="No Connection Required",
            service_name="builtin",
            user_context="",
            is_required=False,
        )

    # Extract connection details from restore data
    connection_restore = restore_data.get(connection_param_name, {})
    connection_label = connection_restore.get("label", "Unknown Make.com Connection")

    # Extract connection type from restore data or parameter definition
    connection_types = connection_restore.get("data", {}).get("connection", "")
    if not connection_types:
        # Try to get from parameter definition
        for param_def in param_definitions:
            if param_def.get("name") == connection_param_name:
                param_type = param_def.get("type", "")
                if ":" in param_type:
                    connection_types = param_type.split(":", 1)[1]
                break

    # Parse service and user info from label
    service_name, user_context = _parse_make_connection_label(connection_label, connection_types)

    # Get supported connection types
    supported_types = _parse_supported_types(connection_types)

    return ConnectionComponent(
        id=f"{module_id}_connection",
        platform=platform,
        extraction_context=extraction_context,
        raw_data={
            "module_data": raw_module_data,
            "connection_id": connection_id,
            "connection_label": connection_label,
            "connection_param_name": connection_param_name,
        },
        connection_id=str(connection_id),
        connection_type=supported_types[0] if supported_types else "unknown",
        connection_label=connection_label,
        service_name=service_name,
        user_context=user_context,
        is_required=True,
        supported_types=supported_types,
        metadata={
            "parameter_name": connection_param_name,
            "restore_data": connection_restore,
            "connection_types": connection_types,
        },
    )


def _find_make_connection_parameter(
    parameters: Dict[str, Any], param_definitions: List[Dict[str, Any]]
) -> tuple[str, Any]:
    """
    Find the connection parameter in Make.com module.

    Returns:
        Tuple of (parameter_name, connection_id) or (None, None) if no connection found
    """
    # Look for parameters with account/connection types
    for param_def in param_definitions:
        param_name = param_def.get("name", "")
        param_type = param_def.get("type", "")

        if param_type.startswith("account:") and param_name in parameters:
            return param_name, parameters[param_name]

    # Fallback: look for common connection parameter names
    common_connection_params = ["account", "connection", "__IMTCONN__"]
    for param_name in common_connection_params:
        if param_name in parameters:
            return param_name, parameters[param_name]

    return None, None


def _parse_make_connection_label(label: str, connection_types: str) -> tuple[str, str]:
    """
    Parse Make.com connection label to extract service and user info.

    Example: "My Microsoft SMTP/IMAP OAuth connection (glenn.coward@capabilitysource.com)"
    Returns: ("Microsoft SMTP/IMAP", "glenn.coward@capabilitysource.com")
    """
    service_name = "Unknown Service"
    user_context = ""

    # Extract email from parentheses
    email_pattern = r"\(([^)]*@[^)]*)\)"
    email_match = re.search(email_pattern, label)
    if email_match:
        user_context = email_match.group(1).strip()

    # Extract service name from label (before "connection" keyword)
    # Remove "My " prefix and " connection" suffix
    clean_label = label.lower()
    if "connection" in clean_label:
        service_part = label.split("connection")[0].strip()
        if service_part.lower().startswith("my "):
            service_part = service_part[3:]
        service_name = service_part.strip()

    # If service name is still generic, use connection types
    if service_name in ["Unknown Service", ""] and connection_types:
        service_name = _format_service_name_from_types(connection_types)

    return service_name, user_context


def _format_service_name_from_types(connection_types: str) -> str:
    """
    Format a readable service name from connection types.

    Example: "imap,google-restricted,microsoft-smtp-imap" -> "Microsoft SMTP/IMAP"
    """
    if not connection_types:
        return "Unknown Service"

    types = [t.strip() for t in connection_types.split(",")]

    # Service name mapping
    service_mapping = {
        "microsoft-smtp-imap": "Microsoft SMTP/IMAP",
        "google": "Google",
        "google-restricted": "Google",
        "imap": "IMAP Email",
        "smtp": "SMTP Email",
        "http": "HTTP API",
        "webhook": "Webhook",
        "ftp": "FTP",
        "sftp": "SFTP",
    }

    # Find the most specific service type
    for type_name in types:
        if type_name in service_mapping:
            return service_mapping[type_name]

    # Fallback to first type, capitalized
    if types:
        return types[0].replace("-", " ").title()

    return "Unknown Service"


def _parse_supported_types(connection_types: str) -> List[str]:
    """
    Parse supported connection types from Make.com type string.

    Example: "account:imap,google-restricted,microsoft-smtp-imap" -> ["imap", "google-restricted", "microsoft-smtp-imap"]
    """
    if not connection_types:
        return []

    # Remove "account:" prefix if present
    if connection_types.startswith("account:"):
        connection_types = connection_types[8:]

    # Split by comma and clean
    return [t.strip() for t in connection_types.split(",") if t.strip()]
