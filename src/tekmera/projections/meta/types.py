"""
Type definitions for projection functions.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, TypeVar, Union


class Platform(Enum):
    """Supported automation platforms."""

    WORKFRONT_FUSION = "workfront_fusion"
    MAKE_COM = "make_com"


T = TypeVar("T")

# Type aliases for projection inputs
Blueprint = Dict[str, Any]
Module = Dict[str, Any]
BlueprintInput = Union[Blueprint, List[Blueprint]]


@dataclass
class ProjectionResult(Generic[T]):
    """Standardized output for all projection functions."""

    blueprint_id: str
    blueprint_name: str
    platform: Platform
    data: T
    metadata: "ProjectionMetadata"


@dataclass
class ModuleResult(Generic[T]):
    """Standardized output for module-level projection functions."""

    module_id: str
    module_type: str
    platform: Platform
    data: T
    metadata: "ProjectionMetadata"


@dataclass
class ProjectionMetadata:
    """Metadata about the projection execution."""

    function: str
    version: str
    computed_at: str
    input_hash: str
    supported_platforms: List[Platform]


@dataclass
class FunctionMetadata:
    """Metadata about a projection function."""

    category: str
    subcategory: str
    name: str
    description: str
    supported_platforms: List[Platform]
    parameters: Dict[str, Any]
    examples: List[Dict[str, Any]]


class UnsupportedPlatformError(Exception):
    """Raised when a platform is not supported."""


def normalize_blueprint_input(blueprints: BlueprintInput) -> List[Blueprint]:
    """Normalize blueprint input to always be a list."""
    if isinstance(blueprints, dict):
        return [blueprints]
    return blueprints


def create_result(
    blueprint: Dict[str, Any],
    platform: Platform,
    function_name: str,
    data: Any,
    version: str = "1.0.0",
    blueprint_name: str | None = None,
) -> ProjectionResult:
    """Create a standardized projection result."""
    import hashlib
    import json

    blueprint_id = blueprint.get("id", hash(json.dumps(blueprint, sort_keys=True)))

    # Use provided blueprint_name, or extract from blueprint, or default
    if blueprint_name is None:
        blueprint_name = blueprint.get("name")
        if not blueprint_name:
            blueprint_name = "Unnamed Blueprint"

    input_hash = hashlib.sha256(json.dumps(blueprint, sort_keys=True).encode()).hexdigest()[:8]

    metadata = ProjectionMetadata(
        function=function_name,
        version=version,
        computed_at=datetime.now().isoformat(),
        input_hash=input_hash,
        supported_platforms=[platform],  # Will be updated by registry
    )

    return ProjectionResult(
        blueprint_id=str(blueprint_id),
        blueprint_name=blueprint_name,
        platform=platform,
        data=data,
        metadata=metadata,
    )


def create_module_result(
    module: Module,
    platform: Platform,
    function_name: str,
    data: Any,
    version: str = "1.0.0",
) -> ModuleResult:
    """Create a standardized module result."""
    import hashlib
    import json

    module_id = str(module.get("id", "unknown"))
    module_type = module.get("module", "unknown")

    input_hash = hashlib.sha256(json.dumps(module, sort_keys=True).encode()).hexdigest()[:8]

    metadata = ProjectionMetadata(
        function=function_name,
        version=version,
        computed_at=datetime.now().isoformat(),
        input_hash=input_hash,
        supported_platforms=[platform],
    )

    return ModuleResult(
        module_id=module_id,
        module_type=module_type,
        platform=platform,
        data=data,
        metadata=metadata,
    )


# Component Type Definitions
# ==========================


class ComponentBase:
    """Base class for all component types."""

    def __init__(
        self,
        id: str,
        component_type: str,
        platform: Platform,
        extraction_context: str,
        raw_data: Dict[str, Any],
        metadata: Dict[str, Any] | None = None,
    ):
        self.id = id
        self.component_type = component_type
        self.platform = platform
        self.extraction_context = extraction_context
        self.raw_data = raw_data
        self.metadata = metadata if metadata is not None else {}


class RouterComponent(ComponentBase):
    """Router component with multiple route flows."""

    def __init__(
        self,
        id: str,
        platform: Platform,
        extraction_context: str,
        raw_data: Dict[str, Any],
        routes_count: int,
        has_filter: bool = False,
        metadata: Dict[str, Any] | None = None,
    ):
        super().__init__(id, "router", platform, extraction_context, raw_data, metadata)
        self.routes_count = routes_count
        self.has_filter = has_filter


class FilterComponent(ComponentBase):
    """Filter component with conditional logic."""

    def __init__(
        self,
        id: str,
        platform: Platform,
        extraction_context: str,
        raw_data: Dict[str, Any],
        filter_name: str,
        conditions_count: int,
        source_router_id: str | None = None,
        metadata: Dict[str, Any] | None = None,
    ):
        super().__init__(id, "filter", platform, extraction_context, raw_data, metadata)
        self.filter_name = filter_name
        self.conditions_count = conditions_count
        self.source_router_id = source_router_id


class ErrorHandlerComponent(ComponentBase):
    """Error handler component with retry/handling logic."""

    def __init__(
        self,
        id: str,
        platform: Platform,
        extraction_context: str,
        raw_data: Dict[str, Any],
        handlers_count: int,
        handler_types: List[str] | None = None,
        metadata: Dict[str, Any] | None = None,
    ):
        super().__init__(id, "error_handler", platform, extraction_context, raw_data, metadata)
        self.handlers_count = handlers_count
        self.handler_types = handler_types if handler_types is not None else []


class ModuleComponent(ComponentBase):
    """Module component with specific functionality."""

    def __init__(
        self,
        id: str,
        platform: Platform,
        extraction_context: str,
        raw_data: Dict[str, Any],
        module_type: str,
        metadata: Dict[str, Any] | None = None,
    ):
        super().__init__(id, "module", platform, extraction_context, raw_data, metadata)
        self.module_type = module_type


# Union type for all components
Component = Union[RouterComponent, FilterComponent, ErrorHandlerComponent, ModuleComponent]
