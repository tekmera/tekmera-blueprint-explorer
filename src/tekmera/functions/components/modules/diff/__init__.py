"""Module-specific diff analysis.

Platform-agnostic module comparison with platform-specific implementations.
"""

from typing import Any, Dict, List
from dataclasses import dataclass

from ....meta.types import Platform


@dataclass
class ModuleDifference:
    """Represents a specific difference found in a module configuration."""
    field_path: str  # e.g., "parameters.url", "metadata.name"
    old_value: Any
    new_value: Any
    change_type: str  # "added", "removed", "modified"
    significance: str  # "critical", "important", "minor", "cosmetic"
    description: str  # Human-readable description
    platform_specific_context: Dict[str, Any] = None  # Platform-specific metadata


def analyze_module_differences(old_module: Dict[str, Any], new_module: Dict[str, Any], platform: Platform) -> List[ModuleDifference]:
    """
    Analyze differences between two modules with platform-specific logic.
    
    Args:
        old_module: Original module configuration
        new_module: Updated module configuration  
        platform: Platform (Workfront Fusion, Make.com, etc.)
        
    Returns:
        List of ModuleDifference objects describing changes
    """
    if platform == Platform.WORKFRONT_FUSION:
        from .workfront_fusion import analyze_workfront_fusion_module
        return analyze_workfront_fusion_module(old_module, new_module)
    elif platform == Platform.MAKE_COM:
        from .make_com import analyze_make_com_module
        return analyze_make_com_module(old_module, new_module)
    else:
        raise ValueError(f"Module diff analysis not implemented for platform: {platform}")


def get_module_type_category(module_data: Dict[str, Any], platform: Platform) -> str:
    """
    Get the module type category for proper diff analysis routing.
    
    Returns categories like: 'api', 'database', 'transform', 'webhook', etc.
    """
    if platform == Platform.WORKFRONT_FUSION:
        from .workfront_fusion import get_workfront_module_category
        return get_workfront_module_category(module_data)
    elif platform == Platform.MAKE_COM:
        from .make_com import get_make_module_category
        return get_make_module_category(module_data)
    else:
        return "unknown"