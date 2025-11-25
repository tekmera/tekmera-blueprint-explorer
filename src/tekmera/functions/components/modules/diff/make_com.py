"""Make.com module-specific diff analysis."""

from typing import Any, Dict, List

from . import ModuleDifference


def analyze_make_com_module(
    old_module: Dict[str, Any], new_module: Dict[str, Any]
) -> List[ModuleDifference]:
    """
    Analyze differences between Make.com modules.

    Focuses on module-specific configuration patterns and business logic.
    """
    differences = []

    # Analyze module type changes
    old_type = old_module.get("module", "")
    new_type = new_module.get("module", "")

    if old_type != new_type:
        differences.append(
            ModuleDifference(
                field_path="module",
                old_value=old_type,
                new_value=new_type,
                change_type="modified",
                significance="critical",
                description=f"Module type changed from {old_type} to {new_type}",
            )
        )

    # Analyze parameters section
    old_params = old_module.get("parameters", {})
    new_params = new_module.get("parameters", {})
    differences.extend(_analyze_make_parameters(old_params, new_params))

    # Analyze Make.com specific settings
    old_settings = old_module.get("settings", {})
    new_settings = new_module.get("settings", {})
    differences.extend(_analyze_make_settings(old_settings, new_settings))

    return differences


def _analyze_make_parameters(
    old_params: Dict[str, Any], new_params: Dict[str, Any]
) -> List[ModuleDifference]:
    """Analyze Make.com parameter changes."""
    differences = []

    all_keys = set(old_params.keys()) | set(new_params.keys())

    for key in all_keys:
        old_value = old_params.get(key)
        new_value = new_params.get(key)

        if old_value != new_value:
            if key not in old_params:
                change_type = "added"
            elif key not in new_params:
                change_type = "removed"
            else:
                change_type = "modified"

            significance = _assess_make_parameter_significance(key, old_value, new_value)
            description = f"Parameter '{key}' {change_type}"

            differences.append(
                ModuleDifference(
                    field_path=f"parameters.{key}",
                    old_value=old_value,
                    new_value=new_value,
                    change_type=change_type,
                    significance=significance,
                    description=description,
                )
            )

    return differences


def _analyze_make_settings(
    old_settings: Dict[str, Any], new_settings: Dict[str, Any]
) -> List[ModuleDifference]:
    """Analyze Make.com settings changes."""
    differences = []

    important_fields = ["enabled", "timeout", "retries"]

    for field in important_fields:
        old_value = old_settings.get(field)
        new_value = new_settings.get(field)

        if old_value != new_value:
            significance = "critical" if field == "enabled" else "minor"

            differences.append(
                ModuleDifference(
                    field_path=f"settings.{field}",
                    old_value=old_value,
                    new_value=new_value,
                    change_type="modified",
                    significance=significance,
                    description=f"Setting '{field}' changed",
                )
            )

    return differences


def _assess_make_parameter_significance(param_name: str, old_value: Any, new_value: Any) -> str:
    """Assess significance of Make.com parameter changes."""
    param_lower = param_name.lower()

    if param_lower in ["url", "endpoint", "method", "connection"]:
        return "critical"
    elif param_lower in ["filter", "limit", "fields", "query"]:
        return "important"
    elif param_lower in ["name", "description"]:
        return "cosmetic"
    else:
        return "minor"


def get_make_module_category(module_data: Dict[str, Any]) -> str:
    """Get Make.com module category."""
    module_type = module_data.get("module", "")

    if "http" in module_type.lower():
        return "api"
    elif "webhook" in module_type.lower():
        return "webhook"
    else:
        return "general"
