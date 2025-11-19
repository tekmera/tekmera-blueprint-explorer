"""
Platform detection for blueprint JSON files.
"""

from typing import Any, Dict

from .types import Platform, UnsupportedPlatformError


def detect_platform(blueprint: Dict[str, Any]) -> Platform:
    """
    Auto-detect platform from blueprint JSON structure.

    Args:
        blueprint: Blueprint JSON object

    Returns:
        Platform enum value

    Raises:
        UnsupportedPlatformError: If platform cannot be detected
    """
    # First, check for metadata.zone (most reliable)
    metadata = blueprint.get("metadata", {})
    if isinstance(metadata, dict):
        zone = metadata.get("zone", "")
        if "workfrontfusion.com" in zone:
            return Platform.WORKFRONT_FUSION
        elif "make.com" in zone or "make.celonis.com" in zone:
            return Platform.MAKE_COM

    # Fallback to structure-based detection
    # Workfront Fusion: has flow array
    if "flow" in blueprint:
        return Platform.WORKFRONT_FUSION
    # Make.com: has scenario with modules
    elif "scenario" in blueprint and "modules" in blueprint.get("scenario", {}):
        return Platform.MAKE_COM
    else:
        raise UnsupportedPlatformError(
            f"Unable to detect platform from blueprint structure. "
            f"Available keys: {list(blueprint.keys())}"
        )
