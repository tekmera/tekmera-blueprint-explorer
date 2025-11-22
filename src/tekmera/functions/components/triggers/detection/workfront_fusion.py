"""Workfront Fusion trigger detection implementation."""

from typing import Any, Dict

from ....meta.trigger_types import (
    WORKFRONT_FUSION_TRIGGER_PATTERNS,
    TriggerConfiguration,
    TriggerConnection,
    UniversalTrigger,
)
from ....meta.types import Platform, ProjectionResult, create_result


def detect_trigger(blueprint: Dict[str, Any]) -> ProjectionResult[UniversalTrigger]:
    """
    Detect trigger from Workfront Fusion blueprint.
    
    Finds the first module (lowest ID) in the flow and analyzes its
    configuration to create a universal trigger representation.
    """
    # Get the flow array
    flow = blueprint.get("flow")
    if flow is None:
        raise ValueError("No flow found in blueprint")
    if not flow:
        raise ValueError("No trigger module found in flow")
    
    # Find the first module (lowest ID) - this is the trigger
    trigger_module = min(flow, key=lambda m: m.get("id", float('inf')))
    
    if not trigger_module:
        raise ValueError("No trigger module found in flow")
    
    module_id = trigger_module.get("id")
    module_type = trigger_module.get("module", "")
    parameters = trigger_module.get("parameters", {})
    metadata = trigger_module.get("metadata", {})
    designer = metadata.get("designer", {})
    restore = metadata.get("restore", {})
    
    # Get universal trigger pattern
    pattern = WORKFRONT_FUSION_TRIGGER_PATTERNS.get(module_type)
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
    
    # Webhook-based triggers
    if "__IMTHOOK__" in parameters:
        connection.requires_auth = True
        connection.connection_type = "webhook"
        connection.connection_id = str(parameters["__IMTHOOK__"])
        # Try to get webhook label from restore metadata
        hook_restore = restore.get("__IMTHOOK__", {})
        if isinstance(hook_restore, dict) and "label" in hook_restore:
            connection.account_reference = hook_restore["label"]
    
    # API-based triggers  
    elif "__IMTCONN__" in parameters:
        connection.requires_auth = True
        connection.connection_type = "api"
        connection.connection_id = str(parameters["__IMTCONN__"])
    
    # Account-based triggers (SFTP, email, etc.)
    elif "account" in parameters:
        connection.requires_auth = True
        connection.connection_type = "account"
        connection.account_reference = str(parameters["account"])
    
    # Custom webhook
    elif "hook" in parameters:
        connection.requires_auth = False
        connection.connection_type = "custom_webhook"
        connection.connection_id = str(parameters["hook"])
    
    # Extract configuration
    configuration = TriggerConfiguration()
    
    # Batch size configuration
    if "maxResults" in parameters:
        configuration.batch_size = parameters["maxResults"]
    elif "limit" in parameters:
        configuration.batch_size = parameters["limit"]
    
    # Filter conditions (for search-based triggers)
    if "qs" in parameters:
        configuration.filter_conditions = parameters["qs"]
    elif module_type == "datastore:SearchRecord":
        # Datastore search filters are often in the parameters directly
        configuration.filter_conditions = {k: v for k, v in parameters.items() 
                                         if k not in ["datastore", "limit", "continueWhenNoRes"]}
    
    # Timeout handling
    if "highWaterMark" in parameters:
        configuration.timeout_seconds = parameters["highWaterMark"] // 1024  # Convert bytes to approx seconds
    
    # Create universal trigger
    trigger = UniversalTrigger(
        platform=Platform.WORKFRONT_FUSION,
        module_id=module_id,
        module_type=module_type,
        execution_pattern=pattern["execution_pattern"],
        data_source=pattern["data_source"],
        reliability=pattern["reliability"],
        scaling=pattern["scaling"],
        connection=connection,
        configuration=configuration,
        display_name=designer.get("name"),
        raw_parameters=parameters,
        raw_metadata=metadata
    )
    
    return create_result(
        blueprint=blueprint,
        platform=Platform.WORKFRONT_FUSION,
        function_name="components.triggers.detection",
        data=trigger
    )