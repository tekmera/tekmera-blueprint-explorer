"""Workfront Fusion module-specific diff analysis."""

from typing import Any, Dict, List
from . import ModuleDifference


def analyze_workfront_fusion_module(old_module: Dict[str, Any], new_module: Dict[str, Any]) -> List[ModuleDifference]:
    """
    Analyze differences between Workfront Fusion modules.
    
    Focuses on module-specific configuration patterns and business logic.
    """
    differences = []
    
    # Analyze module type changes (critical)
    old_type = old_module.get("module", "")
    new_type = new_module.get("module", "")
    
    if old_type != new_type:
        differences.append(ModuleDifference(
            field_path="module",
            old_value=old_type,
            new_value=new_type,
            change_type="modified",
            significance="critical",
            description=f"Module type changed from {old_type} to {new_type}",
            platform_specific_context={"workfront_module_change": True}
        ))
    
    # Analyze parameters section (most common changes)
    old_params = old_module.get("parameters", {})
    new_params = new_module.get("parameters", {})
    differences.extend(_analyze_workfront_parameters(old_params, new_params))
    
    # Analyze mapper configuration
    old_mapper = old_module.get("mapper", {})
    new_mapper = new_module.get("mapper", {})
    differences.extend(_analyze_workfront_mapper(old_mapper, new_mapper))
    
    # Analyze Workfront-specific metadata
    old_meta = old_module.get("metadata", {})
    new_meta = new_module.get("metadata", {})
    differences.extend(_analyze_workfront_metadata(old_meta, new_meta))
    
    return differences


def _analyze_workfront_parameters(old_params: Dict[str, Any], new_params: Dict[str, Any]) -> List[ModuleDifference]:
    """Analyze Workfront Fusion parameter changes with business context."""
    differences = []
    
    all_keys = set(old_params.keys()) | set(new_params.keys())
    
    for key in all_keys:
        old_value = old_params.get(key)
        new_value = new_params.get(key)
        
        if old_value != new_value:
            # Determine change type
            if key not in old_params:
                change_type = "added"
            elif key not in new_params:
                change_type = "removed"
            else:
                change_type = "modified"
            
            # Assess business significance
            significance = _assess_workfront_parameter_significance(key, old_value, new_value)
            
            # Generate business-focused description
            description = _generate_workfront_parameter_description(key, old_value, new_value, change_type)
            
            differences.append(ModuleDifference(
                field_path=f"parameters.{key}",
                old_value=old_value,
                new_value=new_value,
                change_type=change_type,
                significance=significance,
                description=description
            ))
    
    return differences


def _analyze_workfront_mapper(old_mapper: Dict[str, Any], new_mapper: Dict[str, Any]) -> List[ModuleDifference]:
    """Analyze Workfront Fusion mapper configuration changes."""
    differences = []
    
    # Mapper changes affect data transformation
    if old_mapper != new_mapper:
        # Count field mappings
        old_fields = len(old_mapper) if old_mapper else 0
        new_fields = len(new_mapper) if new_mapper else 0
        
        if old_fields != new_fields:
            differences.append(ModuleDifference(
                field_path="mapper",
                old_value=f"{old_fields} field mappings",
                new_value=f"{new_fields} field mappings",
                change_type="modified",
                significance="important",
                description=f"Field mappings changed from {old_fields} to {new_fields} fields"
            ))
        else:
            differences.append(ModuleDifference(
                field_path="mapper",
                old_value="field_mappings",
                new_value="field_mappings_modified",
                change_type="modified",
                significance="important",
                description="Field mapping values or expressions modified"
            ))
    
    return differences


def _analyze_workfront_metadata(old_meta: Dict[str, Any], new_meta: Dict[str, Any]) -> List[ModuleDifference]:
    """Analyze Workfront Fusion metadata changes."""
    differences = []
    
    # Check designer metadata (usually cosmetic)
    old_designer = old_meta.get("designer", {})
    new_designer = new_meta.get("designer", {})
    
    # Name changes
    old_name = old_designer.get("name", "")
    new_name = new_designer.get("name", "")
    
    if old_name != new_name:
        differences.append(ModuleDifference(
            field_path="metadata.designer.name",
            old_value=old_name,
            new_value=new_name,
            change_type="modified",
            significance="cosmetic",
            description=f"Module display name changed from '{old_name}' to '{new_name}'"
        ))
    
    # Position changes (cosmetic)
    old_x = old_designer.get("x", 0)
    old_y = old_designer.get("y", 0)
    new_x = new_designer.get("x", 0)
    new_y = new_designer.get("y", 0)
    
    if (old_x, old_y) != (new_x, new_y):
        differences.append(ModuleDifference(
            field_path="metadata.designer.position",
            old_value=f"({old_x}, {old_y})",
            new_value=f"({new_x}, {new_y})",
            change_type="modified",
            significance="cosmetic",
            description="Module position changed in designer"
        ))
    
    return differences


def _assess_workfront_parameter_significance(param_name: str, old_value: Any, new_value: Any) -> str:
    """Assess business significance of Workfront parameter changes."""
    param_lower = param_name.lower()
    
    # Critical parameters that can break integration
    if param_lower in [
        "connection", "url", "endpoint", "method", 
        "objecttype", "recordtype", "action", "operation"
    ]:
        return "critical"
    
    # Important parameters that affect business logic
    elif param_lower in [
        "limit", "offset", "query", "filter", "search", 
        "outputfields", "fields", "conditions", "criteria"
    ]:
        return "important"
    
    # Minor parameters that affect behavior
    elif param_lower in [
        "format", "timezone", "dateformat", "delimiter", 
        "encoding", "timeout", "retries"
    ]:
        return "minor"
    
    # Cosmetic parameters
    elif param_lower in [
        "name", "label", "description", "notes", "comment"
    ]:
        return "cosmetic"
    
    else:
        return "minor"  # Default to minor for unknown parameters


def _generate_workfront_parameter_description(param_name: str, old_value: Any, new_value: Any, change_type: str) -> str:
    """Generate business-focused descriptions for Workfront parameter changes."""
    param_lower = param_name.lower()
    
    # Connection changes
    if param_lower == "connection":
        return f"Workfront connection changed from '{old_value}' to '{new_value}'"
    
    # Object type changes
    elif param_lower in ["objecttype", "recordtype"]:
        return f"Target object type changed from '{old_value}' to '{new_value}'"
    
    # Query/filter changes  
    elif param_lower in ["query", "filter", "search"]:
        return f"Data filtering criteria modified"
    
    # Field selection changes
    elif param_lower in ["outputfields", "fields"]:
        return f"Selected output fields modified"
    
    # Generic parameter changes
    else:
        if change_type == "added":
            return f"Parameter '{param_name}' added with value: {_format_value_display(new_value)}"
        elif change_type == "removed":
            return f"Parameter '{param_name}' removed (was: {_format_value_display(old_value)})"
        else:
            return f"Parameter '{param_name}' changed from {_format_value_display(old_value)} to {_format_value_display(new_value)}"


def _format_value_display(value: Any) -> str:
    """Format value for display in descriptions."""
    if value is None:
        return "None"
    elif isinstance(value, str):
        if len(value) > 30:
            return f"'{value[:27]}...'"
        return f"'{value}'"
    elif isinstance(value, (dict, list)):
        return f"{type(value).__name__} with {len(value)} items"
    else:
        return str(value)


def get_workfront_module_category(module_data: Dict[str, Any]) -> str:
    """Get Workfront Fusion module category for specialized diff analysis."""
    module_type = module_data.get("module", "")
    
    if "workfront" in module_type.lower():
        if "watch" in module_type.lower():
            return "trigger"
        elif "search" in module_type.lower():
            return "search"
        elif "create" in module_type.lower() or "update" in module_type.lower():
            return "crud"
        else:
            return "workfront_api"
    
    elif "http" in module_type.lower() or "webhook" in module_type.lower():
        return "api"
    
    elif "filter" in module_type.lower():
        return "filter"
    
    elif "router" in module_type.lower():
        return "router"
    
    elif "json" in module_type.lower() or "xml" in module_type.lower():
        return "transform"
    
    else:
        return "general"