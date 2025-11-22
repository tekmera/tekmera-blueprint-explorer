"""Workfront Fusion module types analysis."""

from collections import Counter
from typing import Any, Dict, List

from ....meta.types import Platform, ProjectionResult, create_result
from ....meta.utils.workfront_fusion.extract_components import extract_all_components


def analyze_module_types(blueprint: Dict[str, Any]) -> ProjectionResult[Dict[str, Any]]:
    """
    Analyze module types used in a Workfront Fusion blueprint.
    
    Returns comprehensive analysis including type counts, categories,
    and Workfront-specific patterns.
    """
    # Extract all modules
    all_components = extract_all_components(blueprint, include_orphans=True)
    modules = all_components.get("modules", [])
    
    if not modules:
        return create_result(
            blueprint=blueprint,
            platform=Platform.WORKFRONT_FUSION,
            function_name="components.modules.types",
            data={
                "total_modules": 0,
                "module_types": {},
                "type_counts": {},
                "categories": {},
                "workfront_specific": {},
                "trigger_modules": [],
                "action_modules": [],
                "utility_modules": [],
                "unique_types": 0,
                "most_common_type": ("none", 0)
            }
        )
    
    # Extract module types and analyze them
    module_types = []
    module_details = []
    
    for module in modules:
        module_type = module.get("module", "unknown")
        module_types.append(module_type)
        
        module_details.append({
            "id": module.get("id"),
            "module_type": module_type,
            "name": module.get("metadata", {}).get("designer", {}).get("name", "Unnamed"),
            "platform": Platform.WORKFRONT_FUSION.value
        })
    
    # Count occurrences
    type_counts = dict(Counter(module_types))
    
    # Categorize modules by function
    categories = _categorize_workfront_modules(module_types)
    
    # Workfront-specific analysis
    workfront_specific = _analyze_workfront_patterns(module_types)
    
    # Classify modules by role
    trigger_modules = []
    action_modules = []
    utility_modules = []
    
    for detail in module_details:
        module_type = detail["module_type"]
        category = _get_workfront_module_category(module_type)
        
        if category == "trigger":
            trigger_modules.append(detail)
        elif category == "utility":
            utility_modules.append(detail)
        else:
            action_modules.append(detail)
    
    analysis_data = {
        "total_modules": len(modules),
        "module_types": type_counts,
        "type_counts": type_counts,  # Keep both for backward compatibility
        "categories": categories,
        "workfront_specific": workfront_specific,
        "trigger_modules": trigger_modules,
        "action_modules": action_modules,
        "utility_modules": utility_modules,
        "unique_types": len(type_counts),
        "most_common_type": max(type_counts.items(), key=lambda x: x[1]) if type_counts else ("none", 0)
    }
    
    return create_result(
        blueprint=blueprint,
        platform=Platform.WORKFRONT_FUSION,
        function_name="components.modules.types",
        data=analysis_data
    )


def _categorize_workfront_modules(module_types: List[str]) -> Dict[str, Dict[str, int]]:
    """Categorize Workfront Fusion modules by functional purpose."""
    categories = {
        "workfront_integration": {},  # Native Workfront modules
        "external_triggers": {},  # Webhooks, watchers, external triggers
        "data_transformation": {},  # Parsers, converters, mappers
        "external_actions": {},  # API calls, file operations, notifications
        "flow_control": {},  # Routers, filters, iterators
        "utilities": {}  # Tools, variables, delays
    }
    
    for module_type in module_types:
        category = _classify_workfront_module_type(module_type)
        if category in categories:
            categories[category][module_type] = categories[category].get(module_type, 0) + 1
        else:
            categories["utilities"][module_type] = categories["utilities"].get(module_type, 0) + 1
    
    return categories


def _classify_workfront_module_type(module_type: str) -> str:
    """Classify a Workfront Fusion module type into functional category."""
    module_lower = module_type.lower()
    
    # Native Workfront integration
    if "workfront" in module_lower:
        return "workfront_integration"
    
    # External triggers and watchers
    elif any(keyword in module_lower for keyword in ["watch", "trigger", "webhook", "listen", "monitor"]):
        return "external_triggers"
    
    # Data transformation
    elif any(keyword in module_lower for keyword in ["parse", "json", "csv", "xml", "convert", "transform"]):
        return "data_transformation"
    
    # External actions
    elif any(keyword in module_lower for keyword in ["http", "email", "slack", "teams", "adobe", "sftp", "ftp"]):
        return "external_actions"
    
    # Flow control
    elif any(keyword in module_lower for keyword in ["router", "filter", "iterator", "aggregator", "branch"]):
        return "flow_control"
    
    # Utilities
    elif any(keyword in module_lower for keyword in ["util", "tool", "variable", "set", "delay", "datastore"]):
        return "utilities"
    
    # Default to utilities
    else:
        return "utilities"


def _get_workfront_module_category(module_type: str) -> str:
    """Get the primary role category of a Workfront module."""
    module_lower = module_type.lower()
    
    # Trigger patterns
    if any(keyword in module_lower for keyword in ["watch", "trigger", "webhook", "listen"]):
        return "trigger"
    
    # Utility patterns
    elif any(keyword in module_lower for keyword in ["util", "tool", "variable", "set", "router", "filter", "delay"]):
        return "utility"
    
    # Everything else is an action
    else:
        return "action"


def _analyze_workfront_patterns(module_types: List[str]) -> Dict[str, Any]:
    """Analyze Workfront Fusion specific module patterns."""
    # Count different types of Workfront integration
    workfront_modules = [t for t in module_types if "workfront" in t.lower()]
    proof_modules = [t for t in module_types if "proof" in t.lower()]
    webhook_modules = [t for t in module_types if "webhook" in t.lower() or "customwebhook" in t.lower()]
    api_modules = [t for t in module_types if "custom" in t.lower()]
    email_modules = [t for t in module_types if "email" in t.lower()]
    sftp_modules = [t for t in module_types if "sftp" in t.lower()]
    datastore_modules = [t for t in module_types if "datastore" in t.lower()]
    
    # Analyze integration complexity
    has_workfront_core = any("workfront:search" in t.lower() or "workfront:custom" in t.lower() or "workfront:watch" in t.lower() for t in module_types)
    has_proof_workflow = len(proof_modules) > 0
    has_external_webhooks = len(webhook_modules) > 0
    has_file_operations = len(sftp_modules) > 0
    has_data_storage = len(datastore_modules) > 0
    
    # Calculate complexity metrics
    integration_density = len(workfront_modules) / len(module_types) if module_types else 0
    external_dependency_ratio = (len(webhook_modules) + len(email_modules) + len(sftp_modules)) / len(module_types) if module_types else 0
    
    return {
        "workfront_modules_count": len(workfront_modules),
        "proof_modules_count": len(proof_modules),
        "webhook_modules_count": len(webhook_modules),
        "custom_api_modules_count": len(api_modules),
        "email_modules_count": len(email_modules),
        "sftp_modules_count": len(sftp_modules),
        "datastore_modules_count": len(datastore_modules),
        "has_workfront_core_integration": has_workfront_core,
        "has_proof_workflow": has_proof_workflow,
        "has_external_webhooks": has_external_webhooks,
        "has_file_operations": has_file_operations,
        "has_data_storage": has_data_storage,
        "integration_density": round(integration_density, 3),
        "external_dependency_ratio": round(external_dependency_ratio, 3),
        "complexity_indicators": {
            "high_workfront_integration": integration_density > 0.5,
            "high_external_dependencies": external_dependency_ratio > 0.3,
            "multi_system_integration": len(set([t.split(":")[0] for t in module_types if ":" in t])) > 3,
            "proof_workflow_complexity": len(proof_modules) > 2
        }
    }