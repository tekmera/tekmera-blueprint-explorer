"""Make.com module types analysis."""

from collections import Counter
from typing import Any, Dict, List

from ....meta.types import Platform, ProjectionResult, create_result
from ....meta.utils.make_com.extract_components import extract_all_components


def analyze_module_types(blueprint: Dict[str, Any]) -> ProjectionResult[Dict[str, Any]]:
    """
    Analyze module types used in a Make.com blueprint.

    Returns comprehensive analysis including type counts, categories,
    and Make.com-specific patterns.
    """
    # Extract all modules
    all_components = extract_all_components(blueprint, include_orphans=True)
    modules = all_components.get("modules", [])

    if not modules:
        return create_result(
            blueprint=blueprint,
            platform=Platform.MAKE_COM,
            function_name="components.modules.types",
            data={
                "total_modules": 0,
                "module_types": {},
                "type_counts": {},
                "categories": {},
                "make_specific": {},
                "trigger_modules": [],
                "action_modules": [],
                "utility_modules": [],
                "unique_types": 0,
                "most_common_type": ("none", 0),
            },
        )

    # Extract module types and analyze them
    module_types = []
    module_details = []

    for module in modules:
        module_type = module.get("module", "unknown")
        module_types.append(module_type)

        module_details.append(
            {
                "id": module.get("id"),
                "module_type": module_type,
                "name": module.get("metadata", {}).get("name", "Unnamed"),
                "platform": Platform.MAKE_COM.value,
            }
        )

    # Count occurrences
    type_counts = dict(Counter(module_types))

    # Categorize modules by function
    categories = _categorize_make_modules(module_types)

    # Make.com-specific analysis
    make_specific = _analyze_make_patterns(module_types)

    # Classify modules by role
    trigger_modules = []
    action_modules = []
    utility_modules = []

    for detail in module_details:
        module_type = detail["module_type"]
        category = _get_make_module_category(module_type)

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
        "make_specific": make_specific,
        "trigger_modules": trigger_modules,
        "action_modules": action_modules,
        "utility_modules": utility_modules,
        "unique_types": len(type_counts),
        "most_common_type": (
            max(type_counts.items(), key=lambda x: x[1]) if type_counts else ("none", 0)
        ),
    }

    return create_result(
        blueprint=blueprint,
        platform=Platform.MAKE_COM,
        function_name="components.modules.types",
        data=analysis_data,
    )


def _categorize_make_modules(module_types: List[str]) -> Dict[str, Dict[str, int]]:
    """Categorize Make.com modules by functional purpose."""
    categories = {
        "triggers_and_sources": {},  # Webhooks, email triggers, file monitors
        "data_processing": {},  # JSON parsers, transformers, aggregators
        "integrations": {},  # Third-party app modules
        "communications": {},  # Email, notifications, messaging
        "flow_control": {},  # Routers, filters, iterators
        "utilities": {},  # Tools, delays, variables
    }

    for module_type in module_types:
        category = _classify_make_module_type(module_type)
        if category in categories:
            categories[category][module_type] = categories[category].get(module_type, 0) + 1
        else:
            categories["utilities"][module_type] = categories["utilities"].get(module_type, 0) + 1

    return categories


def _classify_make_module_type(module_type: str) -> str:
    """Classify a Make.com module type into functional category."""
    module_lower = module_type.lower()

    # Triggers and data sources
    if any(
        keyword in module_lower for keyword in ["trigger", "webhook", "watch", "listen", "monitor"]
    ):
        return "triggers_and_sources"

    # Data processing
    elif any(
        keyword in module_lower
        for keyword in ["parse", "json", "csv", "xml", "aggregate", "iterator", "transform"]
    ):
        return "data_processing"

    # Integrations (app-specific modules)
    elif any(
        keyword in module_lower
        for keyword in ["google", "microsoft", "slack", "notion", "airtable", "shopify", "stripe"]
    ):
        return "integrations"

    # Communications
    elif any(
        keyword in module_lower for keyword in ["email", "sms", "notification", "message", "chat"]
    ):
        return "communications"

    # Flow control
    elif any(keyword in module_lower for keyword in ["router", "filter", "branch", "condition"]):
        return "flow_control"

    # Utilities
    elif any(
        keyword in module_lower for keyword in ["tool", "delay", "variable", "set", "get", "http"]
    ):
        return "utilities"

    # Default to utilities
    else:
        return "utilities"


def _get_make_module_category(module_type: str) -> str:
    """Get the primary role category of a Make.com module."""
    module_lower = module_type.lower()

    # Trigger patterns
    if any(keyword in module_lower for keyword in ["trigger", "webhook", "watch", "listen"]):
        return "trigger"

    # Utility patterns
    elif any(
        keyword in module_lower
        for keyword in ["tool", "router", "filter", "delay", "variable", "set"]
    ):
        return "utility"

    # Everything else is an action
    else:
        return "action"


def _analyze_make_patterns(module_types: List[str]) -> Dict[str, Any]:
    """Analyze Make.com specific module patterns."""
    # Count different types of Make.com functionality
    webhook_modules = [t for t in module_types if "webhook" in t.lower()]
    email_modules = [t for t in module_types if "email" in t.lower()]
    json_modules = [t for t in module_types if "json" in t.lower()]
    http_modules = [t for t in module_types if "http" in t.lower()]
    router_modules = [t for t in module_types if "router" in t.lower()]
    iterator_modules = [t for t in module_types if "iterator" in t.lower()]
    aggregator_modules = [t for t in module_types if "aggregator" in t.lower()]

    # Count third-party integrations
    integration_modules = []
    integration_services = [
        "google",
        "microsoft",
        "slack",
        "notion",
        "airtable",
        "shopify",
        "stripe",
        "trello",
        "asana",
    ]
    for module_type in module_types:
        for service in integration_services:
            if service in module_type.lower():
                integration_modules.append(module_type)
                break

    # Analyze workflow complexity
    has_webhook_triggers = len(webhook_modules) > 0
    has_data_processing = len(json_modules) > 0 or len(iterator_modules) > 0
    has_routing_logic = len(router_modules) > 0
    has_aggregation = len(aggregator_modules) > 0
    has_third_party_integrations = len(integration_modules) > 0

    # Calculate complexity metrics
    data_processing_ratio = (
        (len(json_modules) + len(iterator_modules) + len(aggregator_modules)) / len(module_types)
        if module_types
        else 0
    )
    integration_diversity = len(set([t.split(":")[0] for t in integration_modules if ":" in t]))

    return {
        "webhook_modules_count": len(webhook_modules),
        "email_modules_count": len(email_modules),
        "json_modules_count": len(json_modules),
        "http_modules_count": len(http_modules),
        "router_modules_count": len(router_modules),
        "iterator_modules_count": len(iterator_modules),
        "aggregator_modules_count": len(aggregator_modules),
        "integration_modules_count": len(integration_modules),
        "has_webhook_triggers": has_webhook_triggers,
        "has_data_processing": has_data_processing,
        "has_routing_logic": has_routing_logic,
        "has_aggregation": has_aggregation,
        "has_third_party_integrations": has_third_party_integrations,
        "data_processing_ratio": round(data_processing_ratio, 3),
        "integration_diversity": integration_diversity,
        "complexity_indicators": {
            "high_data_processing": data_processing_ratio > 0.3,
            "multi_service_integration": integration_diversity > 2,
            "complex_routing": len(router_modules) > 2,
            "batch_processing": len(iterator_modules) > 0 and len(aggregator_modules) > 0,
        },
    }
