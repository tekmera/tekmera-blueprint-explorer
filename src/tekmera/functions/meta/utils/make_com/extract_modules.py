"""Module extraction for Make.com blueprints."""

from typing import List

from ...types import Blueprint, Module


def extract_modules(blueprint: Blueprint, include_orphans: bool = True) -> List[Module]:
    """Extract all modules from Make.com blueprint."""
    # Make.com has a different structure - modules are typically in scenario.modules
    scenario = blueprint.get("scenario", {})
    modules = scenario.get("modules", [])

    # For now, Make.com structure is simpler (no nested routes/error handlers)
    # include_orphans parameter kept for API consistency but not used yet
    return modules
