"""
Module component description generators.

Generates detailed descriptions for newly added module components,
following the Functions System registry pattern for platform abstraction.
"""

from typing import Dict

from tekmera.functions.meta.types import Platform
from tekmera.functions.components.topology.types import TopologyNode


def generate_module_addition_description(node: TopologyNode) -> str:
    """
    Generate detailed description for a newly added module.

    Platform-agnostic interface following Functions System pattern.

    Args:
        node: Topology node representing the module

    Returns:
        Detailed description of the module's configuration
    """
    platform = _detect_platform(node)

    if platform in MODULE_IMPLEMENTATIONS:
        return MODULE_IMPLEMENTATIONS[platform](node)

    return "New module added to workflow"


def _detect_platform(node: TopologyNode) -> Platform:
    """Detect platform from node characteristics."""
    raw_data = getattr(node, "raw_data", {})

    if isinstance(raw_data, dict):
        module_type = raw_data.get("module", "")
        if isinstance(module_type, str):
            if "workfront" in module_type.lower():
                return Platform.WORKFRONT_FUSION
            elif any(
                prefix in module_type for prefix in ["builtin:", "google:", "slack:", "microsoft:"]
            ):
                return Platform.MAKE_COM

    return Platform.WORKFRONT_FUSION


def _generate_workfront_fusion_module_description(node: TopologyNode) -> str:
    """Generate description for Workfront Fusion modules."""
    raw_data = getattr(node, "raw_data", {})
    if not isinstance(raw_data, dict):
        return "New module added to workflow"

    module_type = raw_data.get("module", "")
    module_name = raw_data.get("metadata", {}).get("designer", {}).get("name", "")

    # Extract meaningful information about the module
    description = _analyze_workfront_module(module_type, module_name, raw_data)

    return description


def _generate_make_com_module_description(node: TopologyNode) -> str:
    """Generate description for Make.com modules."""
    raw_data = getattr(node, "raw_data", {})
    if not isinstance(raw_data, dict):
        return "New module added to workflow"

    module_type = raw_data.get("module", "")
    module_name = raw_data.get("metadata", {}).get("designer", {}).get("name", "")

    # Extract meaningful information about the module
    description = _analyze_make_com_module(module_type, module_name, raw_data)

    return description


def _analyze_workfront_module(module_type: str, module_name: str, raw_data: Dict) -> str:
    """Analyze Workfront Fusion module and generate meaningful description."""
    if not module_type:
        return "New module added to workflow"

    # Parse module type for service and action
    service_info = _parse_module_type(module_type)

    # Get meaningful module name
    display_name = module_name or f"Module {raw_data.get('id', 'Unknown')}"

    # Generate contextual description based on module type
    if service_info["service"] == "workfront":
        action_desc = _describe_workfront_action(service_info["action"])
        return f"New Workfront module added: {display_name} ({action_desc})"
    elif service_info["service"] in ["email", "gmail", "outlook"]:
        action_desc = _describe_email_action(service_info["action"])
        return f"New email module added: {display_name} ({action_desc})"
    elif service_info["service"] in ["http", "webhook"]:
        return f"New HTTP/webhook module added: {display_name}"
    elif service_info["service"] in ["tools", "builtin"]:
        action_desc = _describe_utility_action(service_info["action"])
        return f"New utility module added: {display_name} ({action_desc})"
    else:
        return f"New {service_info['service']} module added: {display_name}"


def _analyze_make_com_module(module_type: str, module_name: str, raw_data: Dict) -> str:
    """Analyze Make.com module and generate meaningful description."""
    if not module_type:
        return "New module added to workflow"

    # Parse module type for service and action
    service_info = _parse_module_type(module_type)

    # Get meaningful module name
    display_name = module_name or f"Module {raw_data.get('id', 'Unknown')}"

    # Generate contextual description based on module type
    if service_info["service"] == "builtin":
        action_desc = _describe_builtin_action(service_info["action"])
        return f"New built-in module added: {display_name} ({action_desc})"
    elif service_info["service"] in ["google", "gmail"]:
        action_desc = _describe_google_action(service_info["action"])
        return f"New Google module added: {display_name} ({action_desc})"
    elif service_info["service"] in ["microsoft", "outlook"]:
        action_desc = _describe_microsoft_action(service_info["action"])
        return f"New Microsoft module added: {display_name} ({action_desc})"
    elif service_info["service"] == "slack":
        action_desc = _describe_slack_action(service_info["action"])
        return f"New Slack module added: {display_name} ({action_desc})"
    else:
        return f"New {service_info['service']} module added: {display_name}"


def _parse_module_type(module_type: str) -> Dict[str, str]:
    """Parse module type string to extract service and action."""
    if ":" in module_type:
        parts = module_type.split(":", 1)
        return {"service": parts[0].lower(), "action": parts[1] if len(parts) > 1 else ""}
    else:
        return {"service": module_type.lower(), "action": ""}


def _describe_workfront_action(action: str) -> str:
    """Describe Workfront action in business terms."""
    action_map = {
        "search": "search records",
        "searchv3": "search records",
        "create": "create record",
        "update": "update record",
        "delete": "delete record",
        "read": "read record",
        "misc": "custom API call",
        "uploadDocument": "upload document",
        "downloadDocument": "download document",
    }
    return action_map.get(action.lower(), action or "perform action")


def _describe_email_action(action: str) -> str:
    """Describe email action in business terms."""
    action_map = {
        "send": "send email",
        "receive": "receive email",
        "watch": "watch for emails",
        "create": "create email",
        "search": "search emails",
    }
    return action_map.get(action.lower(), action or "email action")


def _describe_utility_action(action: str) -> str:
    """Describe utility/tools action in business terms."""
    action_map = {
        "set": "set variables",
        "get": "get variables",
        "increment": "increment counter",
        "sleep": "add delay",
        "json": "parse JSON",
        "text": "process text",
        "math": "calculate values",
    }
    return action_map.get(action.lower(), action or "utility function")


def _describe_builtin_action(action: str) -> str:
    """Describe Make.com built-in action in business terms."""
    action_map = {
        "BasicRouter": "route workflow",
        "BasicAggregator": "aggregate data",
        "BasicIterator": "iterate data",
        "Filter": "filter data",
        "ErrorHandler": "handle errors",
    }
    return action_map.get(action, action or "built-in function")


def _describe_google_action(action: str) -> str:
    """Describe Google service action in business terms."""
    action_map = {
        "send": "send email",
        "watch": "watch emails",
        "search": "search",
        "create": "create item",
        "update": "update item",
        "list": "list items",
    }
    return action_map.get(action.lower(), action or "Google action")


def _describe_microsoft_action(action: str) -> str:
    """Describe Microsoft service action in business terms."""
    action_map = {
        "send": "send email",
        "watch": "watch emails",
        "search": "search",
        "create": "create item",
        "update": "update item",
        "list": "list items",
    }
    return action_map.get(action.lower(), action or "Microsoft action")


def _describe_slack_action(action: str) -> str:
    """Describe Slack action in business terms."""
    action_map = {
        "send": "send message",
        "watch": "watch messages",
        "create": "create channel",
        "update": "update message",
        "search": "search messages",
    }
    return action_map.get(action.lower(), action or "Slack action")


# Registry pattern following Functions System architecture
MODULE_IMPLEMENTATIONS = {
    Platform.WORKFRONT_FUSION: _generate_workfront_fusion_module_description,
    Platform.MAKE_COM: _generate_make_com_module_description,
}
