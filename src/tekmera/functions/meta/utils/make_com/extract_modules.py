"""Module extraction for Make.com blueprints."""

from typing import List

from ...types import Blueprint, Module


def extract_modules(blueprint: Blueprint, include_orphans: bool = True) -> List[Module]:
    """Extract all modules from Make.com blueprint."""
    # Make.com uses flow structure similar to Workfront Fusion
    flow = blueprint.get("flow", [])

    # For now, Make.com structure is simpler (no nested routes/error handlers)
    # include_orphans parameter kept for API consistency but not used yet
    return flow
