"""Blueprint diff analysis with platform-specific implementations.

This module provides platform-agnostic blueprint comparison by routing
to platform-specific implementations.
"""

from typing import Any, Dict

from ...meta.platform_detection import detect_platform
from ...meta.types import Platform, ProjectionResult, create_result, UnsupportedPlatformError
from .types import BlueprintDiffReport


def generate_diff_report(blueprint1: Dict[str, Any], blueprint2: Dict[str, Any]) -> ProjectionResult[BlueprintDiffReport]:
    """
    Generate a comprehensive diff report between two blueprints.
    
    Args:
        blueprint1: First blueprint JSON data (baseline)
        blueprint2: Second blueprint JSON data (comparison target)
        
    Returns:
        ProjectionResult containing BlueprintDiffReport
        
    Raises:
        UnsupportedPlatformError: If platform is not supported
    """
    # Detect platforms for both blueprints
    platform1 = detect_platform(blueprint1)
    platform2 = detect_platform(blueprint2)
    
    # Ensure both blueprints are from the same platform
    if platform1 != platform2:
        raise ValueError(f"Platform mismatch: {platform1.value} vs {platform2.value}. Cannot compare blueprints from different platforms.")
    
    platform = platform1
    
    # Route to platform-specific implementation
    if platform == Platform.WORKFRONT_FUSION:
        from .workfront_fusion import generate_diff_report as generate_wf_diff
        return generate_wf_diff(blueprint1, blueprint2)
    elif platform == Platform.MAKE_COM:
        from .make_com import generate_diff_report as generate_make_diff
        return generate_make_diff(blueprint1, blueprint2)
    else:
        raise UnsupportedPlatformError(f"Blueprint diff not implemented for platform: {platform}")


def generate_sample_diff_report(platform: Platform = Platform.WORKFRONT_FUSION) -> ProjectionResult[BlueprintDiffReport]:
    """
    Generate a sample diff report for demos and testing.
    
    Args:
        platform: Target platform for sample report
        
    Returns:
        ProjectionResult containing sample BlueprintDiffReport
    """
    if platform == Platform.WORKFRONT_FUSION:
        from .workfront_fusion import generate_sample_diff_report as generate_wf_sample
        return generate_wf_sample()
    elif platform == Platform.MAKE_COM:
        from .make_com import generate_sample_diff_report as generate_make_sample
        return generate_make_sample()
    else:
        raise UnsupportedPlatformError(f"Sample diff report not implemented for platform: {platform}")