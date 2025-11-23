"""Types and data structures for platform-specific analysis."""

from typing import Any
from dataclasses import dataclass


@dataclass
class FieldChange:
    """Represents a specific field change within a module configuration."""
    field_path: str  # e.g., "parameters.url" or "metadata.notes"
    old_value: Any
    new_value: Any
    change_type: str  # "added", "removed", "modified"
    significance: str  # "critical", "important", "minor", "cosmetic"
    human_description: str  # Human-readable description of the change


def convert_field_changes_to_module_change_format(field_changes: list[FieldChange]) -> list[dict[str, Any]]:
    """Convert FieldChange objects to the format expected by ModuleChange.configuration_changes."""
    return [
        {
            "field": change.field_path,
            "old_value": change.old_value,
            "new_value": change.new_value,
            "change_type": change.change_type,
            "significance": change.significance,
            "description": change.human_description
        }
        for change in field_changes
    ]