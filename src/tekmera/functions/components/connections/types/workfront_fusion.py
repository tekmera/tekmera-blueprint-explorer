"""Workfront Fusion connection type implementation."""

import re
from typing import Any, Dict

from .....meta.types import Platform
from . import ConnectionComponent


def create_workfront_fusion_connection(
    module_id: str,
    platform: Platform,
    extraction_context: str,
    raw_module_data: Dict[str, Any],
    connection_data: Dict[str, Any],
) -> ConnectionComponent:
    """
    Create a ConnectionComponent for Workfront Fusion.

    Workfront Fusion connections use __IMTCONN__ parameter with metadata in restore section.
    """
    parameters = raw_module_data.get("parameters", {})
    metadata = raw_module_data.get("metadata", {})
    restore_data = metadata.get("restore", {})

    # Extract connection ID from parameters
    connection_id = str(parameters.get("__IMTCONN__", "unknown"))

    # Extract connection label from restore metadata
    connection_restore = restore_data.get("__IMTCONN__", {})
    connection_label = connection_restore.get("label", "Unknown Workfront Connection")

    # Parse service and user info from label
    service_name, user_context = _parse_workfront_connection_label(connection_label)

    # Determine connection type from module type
    module_type = raw_module_data.get("module", "")
    connection_type = _get_workfront_connection_type(module_type)

    return ConnectionComponent(
        id=f"{module_id}_connection",
        platform=platform,
        extraction_context=extraction_context,
        raw_data={
            "module_data": raw_module_data,
            "connection_id": connection_id,
            "connection_label": connection_label,
        },
        connection_id=connection_id,
        connection_type=connection_type,
        connection_label=connection_label,
        service_name=service_name,
        user_context=user_context,
        is_required=True,
        supported_types=["account"],
        metadata={"parameter_name": "__IMTCONN__", "restore_data": connection_restore},
    )


def _parse_workfront_connection_label(label: str) -> tuple[str, str]:
    """
    Parse Workfront connection label to extract service and user info.

    Example: "EYET PROD SA Connection (P.eygfusion.1 P.eygfusion.1 | eyet.my.workfront.com)"
    Returns: ("Workfront", "P.eygfusion.1@eyet.my.workfront.com")
    """
    service_name = "Workfront"
    user_context = ""

    # Look for patterns like "username | server.workfront.com"
    server_pattern = r"([^|]+)\s*\|\s*([^)]+\.workfront\.com)"
    server_match = re.search(server_pattern, label)

    if server_match:
        username = server_match.group(1).strip()
        server = server_match.group(2).strip()
        user_context = f"{username}@{server}"
    else:
        # Look for just server pattern
        server_pattern = r"([^)]+\.workfront\.com)"
        server_match = re.search(server_pattern, label)
        if server_match:
            user_context = server_match.group(1).strip()

    return service_name, user_context


def _get_workfront_connection_type(module_type: str) -> str:
    """
    Determine connection type from Workfront Fusion module type.

    Args:
        module_type: Module type string (e.g., "workfront-workfront:custom")

    Returns:
        Connection type classification
    """
    if not module_type:
        return "unknown"

    module_lower = module_type.lower()

    if "workfront" in module_lower:
        return "workfront"
    elif "http" in module_lower or "webhook" in module_lower:
        return "http"
    elif "email" in module_lower:
        return "email"
    elif "database" in module_lower or "sql" in module_lower:
        return "database"
    elif "ftp" in module_lower or "sftp" in module_lower:
        return "ftp"
    else:
        return "api"
