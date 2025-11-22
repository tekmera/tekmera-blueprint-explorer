"""Make.com trigger detection implementation."""

from typing import Any, Dict

from ....meta.trigger_types import (
    MAKE_COM_TRIGGER_PATTERNS,
    TriggerConfiguration,
    TriggerConnection,
    UniversalTrigger,
)
from ....meta.types import Platform, ProjectionResult, create_result


def detect_trigger(blueprint: Dict[str, Any]) -> ProjectionResult[UniversalTrigger]:
    """
    Detect trigger from Make.com blueprint.
    
    Finds the first module (lowest ID) in the scenario and analyzes its
    configuration to create a universal trigger representation.
    """
    # Make.com structure: scenario.modules contains the flow
    scenario = blueprint.get("scenario", {})
    modules = scenario.get("modules", [])
    
    if not modules:
        # Try direct flow structure (some Make.com exports vary)
        modules = blueprint.get("flow", [])
    
    if not modules:
        raise ValueError("No modules found in Make.com blueprint")
    
    # Find the first module (lowest ID) - this is the trigger
    trigger_module = min(modules, key=lambda m: m.get("id", float('inf')))
    
    if not trigger_module:
        raise ValueError("No trigger module found in modules")
    
    module_id = trigger_module.get("id")
    module_type = trigger_module.get("module", "")
    parameters = trigger_module.get("parameters", {})
    metadata = trigger_module.get("metadata", {})
    designer = metadata.get("designer", {})
    restore = metadata.get("restore", {})
    
    # Get universal trigger pattern
    pattern = MAKE_COM_TRIGGER_PATTERNS.get(module_type)
    if not pattern:
        # Default pattern for unknown triggers
        from ....meta.trigger_types import (
            TriggerExecutionPattern,
            TriggerDataSource,
            TriggerReliability,
            TriggerScaling,
        )
        pattern = {
            "execution_pattern": TriggerExecutionPattern.MANUAL,
            "data_source": TriggerDataSource.USER_INTERFACE,
            "reliability": TriggerReliability.BEST_EFFORT,
            "scaling": TriggerScaling.SINGLE_ITEM,
        }
    
    # Extract connection information
    connection = TriggerConnection()
    
    # Custom webhook
    if "hook" in parameters:
        connection.requires_auth = False
        connection.connection_type = "custom_webhook"
        connection.connection_id = str(parameters["hook"])
        # Try to get webhook label from restore metadata
        hook_restore = restore.get("parameters", {}).get("hook", {})
        if isinstance(hook_restore, dict) and "label" in hook_restore:
            connection.account_reference = hook_restore["label"]
    
    # Account-based triggers (email, etc.)
    elif "account" in parameters:
        connection.requires_auth = True
        connection.connection_type = "account"
        connection.account_reference = str(parameters["account"])
    
    # Extract configuration
    configuration = TriggerConfiguration()
    
    # Batch size configuration
    if "maxResults" in parameters:
        configuration.batch_size = parameters["maxResults"]
    elif "limit" in parameters:
        configuration.batch_size = parameters["limit"]
    
    # Email-specific filters
    if module_type == "email:TriggerNewEmail":
        email_filters = {}
        for key in ["subject", "from", "to", "text", "folder", "criteria"]:
            if key in parameters and parameters[key]:
                email_filters[key] = parameters[key]
        configuration.filter_conditions = email_filters
    
    # JSON parser data
    if module_type == "json:ParseJSON" and "json" in trigger_module.get("mapper", {}):
        # Store whether this has sample data
        json_data = trigger_module["mapper"]["json"]
        if json_data:
            configuration.filter_conditions = {"has_sample_data": True, "data_size": len(json_data)}
    
    # Create universal trigger
    trigger = UniversalTrigger(
        platform=Platform.MAKE_COM,
        module_id=module_id,
        module_type=module_type,
        execution_pattern=pattern["execution_pattern"],
        data_source=pattern["data_source"],
        reliability=pattern["reliability"],
        scaling=pattern["scaling"],
        connection=connection,
        configuration=configuration,
        display_name=designer.get("name") or parameters.get("name"),
        raw_parameters=parameters,
        raw_metadata=metadata
    )
    
    return create_result(
        blueprint=blueprint,
        platform=Platform.MAKE_COM,
        function_name="components.triggers.detection",
        data=trigger
    )