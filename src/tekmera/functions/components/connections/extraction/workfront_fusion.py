"""Workfront Fusion connection extraction implementation."""

from typing import Any, Dict, List

from .....meta.types import Platform
from ..types import ConnectionComponent, create_connection_component


def extract_workfront_fusion_connections(blueprint: Dict[str, Any]) -> List[ConnectionComponent]:
    """
    Extract all connections from a Workfront Fusion blueprint.

    Searches through all modules for __IMTCONN__ parameters and creates
    ConnectionComponent instances for each.
    """
    connections = []

    # Get all modules from the blueprint flow
    modules = _extract_all_modules_from_flow(blueprint.get("flow", []))

    for module in modules:
        connection = _extract_connection_from_module(module, blueprint)
        if connection:
            connections.append(connection)

    return connections


def _extract_all_modules_from_flow(
    flow: List[Dict[str, Any]], path: str = "main"
) -> List[Dict[str, Any]]:
    """
    Recursively extract all modules from nested flow structure.

    Workfront Fusion blueprints can have modules in:
    - Main flow
    - Routes within modules (router branches)
    - Error handlers (onerror sections)
    """
    modules = []

    for i, module in enumerate(flow):
        # Add extraction context to track where this module came from
        module_with_context = module.copy()
        module_with_context["_extraction_context"] = {"path": path, "position": i}
        modules.append(module_with_context)

        # Recursively extract from routes
        routes = module.get("routes", [])
        if routes:
            for j, route in enumerate(routes):
                route_flow = route.get("flow", [])
                route_path = f"{path}.route{j}"
                modules.extend(_extract_all_modules_from_flow(route_flow, route_path))

        # Recursively extract from error handlers
        error_handlers = module.get("onerror", [])
        if error_handlers:
            error_path = f"{path}.error"
            modules.extend(_extract_all_modules_from_flow(error_handlers, error_path))

    return modules


def _extract_connection_from_module(
    module: Dict[str, Any], blueprint: Dict[str, Any]
) -> ConnectionComponent | None:
    """
    Extract connection information from a single Workfront Fusion module.

    Returns None if module has no connection.
    """
    parameters = module.get("parameters", {})

    # Check if module has a connection parameter
    if "__IMTCONN__" not in parameters:
        return None

    connection_id = parameters["__IMTCONN__"]
    if not connection_id:
        return None

    # Extract module context
    module_id = str(module.get("id", "unknown"))
    extraction_context = module.get("_extraction_context", {})
    context_path = extraction_context.get("path", "main")

    # Prepare connection data for type creation
    connection_data = {"id": connection_id, "parameter_name": "__IMTCONN__"}

    # Create the connection component
    connection = create_connection_component(
        module_id=module_id,
        platform=Platform.WORKFRONT_FUSION,
        extraction_context=f"module{module_id}.{context_path}",
        raw_module_data=module,
        connection_data=connection_data,
    )

    return connection


def get_workfront_connection_summary(connections: List[ConnectionComponent]) -> Dict[str, Any]:
    """
    Get Workfront Fusion-specific connection summary.

    Args:
        connections: List of Workfront Fusion connections

    Returns:
        Summary with WF-specific insights
    """
    if not connections:
        return {
            "workfront_instances": [],
            "api_connections": 0,
            "webhook_connections": 0,
            "connection_distribution": {},
        }

    workfront_instances = set()
    api_connections = 0
    webhook_connections = 0
    connection_distribution = {}

    for connection in connections:
        # Extract Workfront instance from user context
        if "@" in connection.user_context and "workfront.com" in connection.user_context:
            instance = connection.user_context.split("@")[1]
            workfront_instances.add(instance)

        # Count connection types
        if connection.connection_type == "workfront":
            api_connections += 1
        elif connection.connection_type in ["http", "webhook"]:
            webhook_connections += 1

        # Distribution by service
        service = connection.service_name
        connection_distribution[service] = connection_distribution.get(service, 0) + 1

    return {
        "workfront_instances": sorted(list(workfront_instances)),
        "api_connections": api_connections,
        "webhook_connections": webhook_connections,
        "connection_distribution": connection_distribution,
    }
