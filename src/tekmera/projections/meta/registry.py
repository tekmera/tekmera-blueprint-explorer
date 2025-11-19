"""
Function registry and discovery system.
"""

import importlib
from typing import Callable, Dict, List, Set

from .types import FunctionMetadata, Platform, UnsupportedPlatformError


class ProjectionRegistry:
    """Central registry for function discovery and routing."""

    def __init__(self):
        self._functions: Dict[str, Dict[Platform, Callable]] = {}
        self._metadata: Dict[str, FunctionMetadata] = {}

    def register_function(
        self,
        category: str,
        subcategory: str,
        name: str,
        platform: Platform,
        func: Callable,
        metadata: FunctionMetadata = None,
    ):
        """Register a projection function."""
        key = f"{category}.{subcategory}.{name}"

        if key not in self._functions:
            self._functions[key] = {}

        self._functions[key][platform] = func

        if metadata:
            self._metadata[key] = metadata

    def get_function(
        self, category: str, subcategory: str, name: str, platform: Platform
    ) -> Callable:
        """Get platform-specific function implementation."""
        key = f"{category}.{subcategory}.{name}"

        if key not in self._functions:
            # Try to auto-discover
            self._discover_function(category, subcategory, name)

        if key not in self._functions:
            raise UnsupportedPlatformError(f"Function {key} not found")

        platform_funcs = self._functions[key]

        if platform in platform_funcs:
            return platform_funcs[platform]

        # Try common implementation
        if Platform.WORKFRONT_FUSION in platform_funcs:
            return platform_funcs[Platform.WORKFRONT_FUSION]

        raise UnsupportedPlatformError(
            f"Function {key} not supported for platform {platform.value}"
        )

    def _discover_function(self, category: str, subcategory: str, name: str):
        """Auto-discover function by importing its module and registering implementations."""
        try:
            # Try new structure first: components/blueprints
            if category in ["components", "blueprints"]:
                module_path = f"tekmera.projections.{category}.{subcategory}.{name}"
            else:
                # Fallback for any legacy paths
                module_path = f"tekmera.projections.{category}.{subcategory}.{name}"

            module = importlib.import_module(module_path)

            # Get the main function and its implementations
            getattr(module, name)
            implementations = getattr(module, "IMPLEMENTATIONS", {})

            # Register all platform implementations
            key = f"{category}.{subcategory}.{name}"
            self._functions[key] = implementations.copy()

        except (ImportError, AttributeError):
            pass  # Function doesn't exist or has no implementations

    def list_functions(self, platform: Platform = None) -> List[FunctionMetadata]:
        """List available functions, optionally filtered by platform."""
        result = []
        for key, metadata in self._metadata.items():
            if platform is None or platform in metadata.supported_platforms:
                result.append(metadata)
        return result

    def get_supported_platforms(self) -> Set[Platform]:
        """Get all supported platforms."""
        platforms = set()
        for func_platforms in self._functions.values():
            platforms.update(func_platforms.keys())
        return platforms
