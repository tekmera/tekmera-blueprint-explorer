"""
Platform-specific utilities for projection functions.
"""

from typing import Any, Dict, List

from ..types import Blueprint, Module, Platform
from . import make_com, workfront_fusion

MODULE_IMPLEMENTATIONS = {
    Platform.WORKFRONT_FUSION: workfront_fusion.extract_modules,
    Platform.MAKE_COM: make_com.extract_modules,
}

COMPONENT_IMPLEMENTATIONS = {
    Platform.WORKFRONT_FUSION: workfront_fusion.extract_components,
    Platform.MAKE_COM: make_com.extract_components,
}


def extract_modules(
    blueprint: Blueprint, platform: Platform, include_orphans: bool = True
) -> List[Module]:
    """Extract all modules from blueprint based on platform."""
    if platform in MODULE_IMPLEMENTATIONS:
        return MODULE_IMPLEMENTATIONS[platform](blueprint, include_orphans)

    raise ValueError(f"Platform {platform.value} not supported for module extraction")


def extract_all_components(
    blueprint: Blueprint, platform: Platform, include_orphans: bool = True
) -> Dict[str, List[Dict[str, Any]]]:
    """Extract all components (modules, routers, filters, error handlers) from blueprint."""
    if platform in COMPONENT_IMPLEMENTATIONS:
        return COMPONENT_IMPLEMENTATIONS[platform].extract_all_components(
            blueprint, include_orphans
        )

    raise ValueError(f"Platform {platform.value} not supported for component extraction")


def extract_routers(
    blueprint: Blueprint, platform: Platform, include_orphans: bool = True
) -> List[Dict[str, Any]]:
    """Extract routers from blueprint."""
    if platform in COMPONENT_IMPLEMENTATIONS:
        return COMPONENT_IMPLEMENTATIONS[platform].extract_routers(blueprint, include_orphans)

    raise ValueError(f"Platform {platform.value} not supported for router extraction")


def extract_filters(
    blueprint: Blueprint, platform: Platform, include_orphans: bool = True
) -> List[Dict[str, Any]]:
    """Extract filters from blueprint."""
    if platform in COMPONENT_IMPLEMENTATIONS:
        return COMPONENT_IMPLEMENTATIONS[platform].extract_filters(blueprint, include_orphans)

    raise ValueError(f"Platform {platform.value} not supported for filter extraction")


def extract_error_handlers(
    blueprint: Blueprint, platform: Platform, include_orphans: bool = True
) -> List[Dict[str, Any]]:
    """Extract error handlers from blueprint."""
    if platform in COMPONENT_IMPLEMENTATIONS:
        return COMPONENT_IMPLEMENTATIONS[platform].extract_error_handlers(
            blueprint, include_orphans
        )

    raise ValueError(f"Platform {platform.value} not supported for error handler extraction")
