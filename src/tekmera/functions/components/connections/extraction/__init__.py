"""
Connection extraction functions.

Platform-agnostic connection extraction with platform-specific implementations.
"""

from typing import Any, Dict, List

from ....meta.types import Platform
from ..types import ConnectionComponent


def extract_all_connections(
    blueprint: Dict[str, Any], platform: Platform
) -> List[ConnectionComponent]:
    """
    Extract all connections used across a blueprint with platform-specific logic.

    Args:
        blueprint: Full blueprint configuration
        platform: Platform (Workfront Fusion, Make.com, etc.)

    Returns:
        List of ConnectionComponent objects for all connections found
    """
    if platform == Platform.WORKFRONT_FUSION:
        from .workfront_fusion import extract_workfront_fusion_connections

        return extract_workfront_fusion_connections(blueprint)
    elif platform == Platform.MAKE_COM:
        from .make_com import extract_make_com_connections

        return extract_make_com_connections(blueprint)
    else:
        raise ValueError(f"Connection extraction not implemented for platform: {platform}")


def get_unique_connections(
    connections: List[ConnectionComponent],
) -> Dict[str, ConnectionComponent]:
    """
    Get unique connections from a list, deduplicating by connection ID.

    Args:
        connections: List of connection components

    Returns:
        Dictionary mapping connection_id -> ConnectionComponent
    """
    unique_connections = {}

    for connection in connections:
        connection_id = connection.connection_id

        # If we haven't seen this connection ID, add it
        if connection_id not in unique_connections:
            unique_connections[connection_id] = connection
        else:
            # If we have seen it, keep the one with more information
            existing = unique_connections[connection_id]
            if len(connection.connection_label) > len(existing.connection_label):
                unique_connections[connection_id] = connection

    return unique_connections


def get_connection_usage_stats(connections: List[ConnectionComponent]) -> Dict[str, Any]:
    """
    Get usage statistics for connections across a blueprint.

    Args:
        connections: List of connection components

    Returns:
        Dictionary with usage statistics
    """
    if not connections:
        return {
            "total_connections": 0,
            "unique_connections": 0,
            "connections_by_type": {},
            "connections_by_service": {},
            "most_used_connection": None,
        }

    unique_connections = get_unique_connections(connections)
    connection_usage = {}
    connections_by_type = {}
    connections_by_service = {}

    # Count usage and categorize
    for connection in connections:
        conn_id = connection.connection_id

        # Count usage
        connection_usage[conn_id] = connection_usage.get(conn_id, 0) + 1

        # Count by type
        conn_type = connection.connection_type
        connections_by_type[conn_type] = connections_by_type.get(conn_type, 0) + 1

        # Count by service
        service = connection.service_name
        connections_by_service[service] = connections_by_service.get(service, 0) + 1

    # Find most used connection
    most_used_connection = None
    if connection_usage:
        most_used_id = max(connection_usage, key=connection_usage.get)
        most_used_connection = {
            "connection_id": most_used_id,
            "usage_count": connection_usage[most_used_id],
            "connection": unique_connections.get(most_used_id),
        }

    return {
        "total_connections": len(connections),
        "unique_connections": len(unique_connections),
        "connections_by_type": connections_by_type,
        "connections_by_service": connections_by_service,
        "most_used_connection": most_used_connection,
        "connection_usage": connection_usage,
    }
