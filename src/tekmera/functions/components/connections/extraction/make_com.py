"""Make.com connection extraction implementation."""

from typing import Any, Dict, List

from .....meta.types import Platform
from ..types import ConnectionComponent, create_connection_component


def extract_make_com_connections(blueprint: Dict[str, Any]) -> List[ConnectionComponent]:
    """
    Extract all connections from a Make.com blueprint.

    Searches through all modules for connection parameters and creates
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

    Make.com blueprints can have modules in:
    - Main flow
    - Routes within modules (router branches)
    - Error handlers
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
    Extract connection information from a single Make.com module.

    Returns None if module has no connection.
    """
    parameters = module.get("parameters", {})
    metadata = module.get("metadata", {})
    param_definitions = metadata.get("parameters", [])

    # Look for connection parameters using parameter definitions
    connection_param_name = None
    connection_id = None

    for param_def in param_definitions:
        param_name = param_def.get("name", "")
        param_type = param_def.get("type", "")

        # Check if this is a connection parameter
        if param_type.startswith("account:") and param_name in parameters:
            connection_param_name = param_name
            connection_id = parameters[param_name]
            break

    # Fallback: look for common connection parameters
    if not connection_param_name:
        common_params = ["account", "connection", "__IMTCONN__"]
        for param_name in common_params:
            if param_name in parameters:
                connection_param_name = param_name
                connection_id = parameters[param_name]
                break

    # If no connection found, return None
    if not connection_param_name or not connection_id:
        return None

    # Extract module context
    module_id = str(module.get("id", "unknown"))
    extraction_context = module.get("_extraction_context", {})
    context_path = extraction_context.get("path", "main")

    # Prepare connection data for type creation
    connection_data = {"id": connection_id, "parameter_name": connection_param_name}

    # Create the connection component
    connection = create_connection_component(
        module_id=module_id,
        platform=Platform.MAKE_COM,
        extraction_context=f"module{module_id}.{context_path}",
        raw_module_data=module,
        connection_data=connection_data,
    )

    return connection


def get_make_com_connection_summary(connections: List[ConnectionComponent]) -> Dict[str, Any]:
    """
    Get Make.com-specific connection summary.

    Args:
        connections: List of Make.com connections

    Returns:
        Summary with Make.com-specific insights
    """
    if not connections:
        return {
            "email_providers": [],
            "oauth_connections": 0,
            "api_key_connections": 0,
            "service_distribution": {},
            "multi_type_connections": [],
        }

    email_providers = set()
    oauth_connections = 0
    api_key_connections = 0
    service_distribution = {}
    multi_type_connections = []

    for connection in connections:
        # Extract email providers from user context
        if "@" in connection.user_context:
            domain = connection.user_context.split("@")[1] if "@" in connection.user_context else ""
            if domain:
                email_providers.add(domain)

        # Count OAuth vs API key connections (heuristic)
        if "oauth" in connection.connection_label.lower():
            oauth_connections += 1
        else:
            api_key_connections += 1

        # Service distribution
        service = connection.service_name
        service_distribution[service] = service_distribution.get(service, 0) + 1

        # Multi-type connections
        if len(connection.supported_types) > 1:
            multi_type_connections.append(
                {
                    "connection_id": connection.connection_id,
                    "connection_label": connection.connection_label,
                    "supported_types": connection.supported_types,
                }
            )

    return {
        "email_providers": sorted(list(email_providers)),
        "oauth_connections": oauth_connections,
        "api_key_connections": api_key_connections,
        "service_distribution": service_distribution,
        "multi_type_connections": multi_type_connections,
    }
