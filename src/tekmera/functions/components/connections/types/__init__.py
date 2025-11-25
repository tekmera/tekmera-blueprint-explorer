"""
Connection component type definitions.

Defines ConnectionComponent class and platform-specific connection typing.
"""

from dataclasses import dataclass
from typing import Any, Dict, List

from ....meta.types import ComponentBase, Platform


@dataclass
class ConnectionComponent(ComponentBase):
    """Connection component with service authentication details."""

    def __init__(
        self,
        id: str,
        platform: Platform,
        extraction_context: str,
        raw_data: Dict[str, Any],
        connection_id: str,
        connection_type: str,
        connection_label: str,
        service_name: str,
        user_context: str = "",
        is_required: bool = True,
        supported_types: List[str] = None,
        metadata: Dict[str, Any] | None = None,
    ):
        super().__init__(id, "connection", platform, extraction_context, raw_data, metadata)
        self.connection_id = connection_id
        self.connection_type = connection_type
        self.connection_label = connection_label
        self.service_name = service_name
        self.user_context = user_context
        self.is_required = is_required
        self.supported_types = supported_types or []


def create_connection_component(
    module_id: str,
    platform: Platform,
    extraction_context: str,
    raw_module_data: Dict[str, Any],
    connection_data: Dict[str, Any],
) -> ConnectionComponent:
    """
    Create a ConnectionComponent from module and connection data.

    Args:
        module_id: ID of the module using this connection
        platform: Platform (Workfront Fusion, Make.com, etc.)
        extraction_context: Context where connection was extracted
        raw_module_data: Full module configuration
        connection_data: Extracted connection information

    Returns:
        ConnectionComponent instance
    """
    if platform == Platform.WORKFRONT_FUSION:
        from .workfront_fusion import create_workfront_fusion_connection

        return create_workfront_fusion_connection(
            module_id, platform, extraction_context, raw_module_data, connection_data
        )
    elif platform == Platform.MAKE_COM:
        from .make_com import create_make_com_connection

        return create_make_com_connection(
            module_id, platform, extraction_context, raw_module_data, connection_data
        )
    else:
        # Generic fallback
        return ConnectionComponent(
            id=f"{module_id}_connection",
            platform=platform,
            extraction_context=extraction_context,
            raw_data=raw_module_data,
            connection_id=connection_data.get("id", "unknown"),
            connection_type=connection_data.get("type", "unknown"),
            connection_label=connection_data.get("label", "Unknown Connection"),
            service_name=connection_data.get("service", "unknown"),
            user_context=connection_data.get("user", ""),
            metadata=connection_data,
        )
