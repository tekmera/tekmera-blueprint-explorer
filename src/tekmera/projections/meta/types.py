"""
Type definitions for projection functions.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, TypeVar


class Platform(Enum):
    """Supported automation platforms."""

    WORKFRONT_FUSION = "workfront_fusion"
    MAKE_COM = "make_com"


T = TypeVar("T")


@dataclass
class ProjectionResult(Generic[T]):
    """Standardized output for all projection functions."""

    blueprint_id: str
    blueprint_name: str
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


def create_result(
    blueprint: Dict[str, Any],
    platform: Platform,
    function_name: str,
    data: Any,
    version: str = "1.0.0",
    blueprint_name: str = None,
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
