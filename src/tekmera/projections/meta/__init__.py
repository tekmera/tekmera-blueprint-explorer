"""
Projection metadata and infrastructure.
"""

from .platform_detection import detect_platform
from .registry import ProjectionRegistry
from .types import Platform, ProjectionResult

__all__ = ["Platform", "ProjectionResult", "detect_platform", "ProjectionRegistry"]
