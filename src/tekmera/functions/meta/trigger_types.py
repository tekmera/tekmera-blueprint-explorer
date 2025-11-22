"""
Universal trigger type definitions for automation platforms.

This module defines platform-agnostic trigger concepts that apply across
automation platforms like Workfront Fusion, Make.com, n8n, Power Platform, etc.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

from .types import Platform


class TriggerExecutionPattern(Enum):
    """How the trigger executes - fundamental pattern across all platforms."""
    WEBHOOK = "webhook"          # Real-time HTTP callbacks
    POLLING = "polling"          # Periodic checking for changes  
    SCHEDULED = "scheduled"      # Time-based execution
    MANUAL = "manual"            # User or system initiated
    EVENT_DRIVEN = "event_driven"  # Platform-specific event subscriptions


class TriggerDataSource(Enum):
    """What type of system/data the trigger monitors."""
    INTERNAL_PLATFORM = "internal_platform"    # Platform's own events (Workfront events)
    EXTERNAL_API = "external_api"              # Third-party API calls
    FILE_SYSTEM = "file_system"                # File/folder monitoring
    EMAIL_SYSTEM = "email_system"              # Email inbox monitoring
    DATABASE = "database"                      # Database queries
    WEBHOOK_RECEIVER = "webhook_receiver"      # Generic webhook endpoint
    MESSAGE_QUEUE = "message_queue"            # Queue-based triggers
    USER_INTERFACE = "user_interface"          # Manual UI triggers


class TriggerReliability(Enum):
    """Reliability characteristics of the trigger."""
    REAL_TIME = "real_time"         # Immediate execution
    NEAR_REAL_TIME = "near_real_time"  # Within seconds/minutes
    BATCH = "batch"                 # Periodic bulk processing
    BEST_EFFORT = "best_effort"     # No delivery guarantees


class TriggerScaling(Enum):
    """How the trigger handles load/volume."""
    SINGLE_ITEM = "single_item"     # Processes one item at a time
    BATCH_LIMITED = "batch_limited" # Fixed batch size
    BATCH_UNLIMITED = "batch_unlimited"  # No batch limits
    STREAMING = "streaming"         # Continuous processing


@dataclass
class TriggerConnection:
    """Universal connection/authentication information."""
    requires_auth: bool = False
    connection_type: Optional[str] = None  # oauth, api_key, basic, etc.
    connection_id: Optional[str] = None
    account_reference: Optional[str] = None


@dataclass
class TriggerConfiguration:
    """Universal trigger configuration."""
    batch_size: Optional[int] = None
    timeout_seconds: Optional[int] = None
    retry_policy: Optional[str] = None
    error_handling: Optional[str] = None
    filter_conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UniversalTrigger:
    """
    Platform-agnostic trigger representation.
    
    This captures the universal concepts that apply across automation platforms,
    allowing for cross-platform analysis and comparison.
    """
    # Core identification
    platform: Platform
    module_id: int
    module_type: str  # Platform-specific module type
    
    # Universal trigger characteristics
    execution_pattern: TriggerExecutionPattern
    data_source: TriggerDataSource
    reliability: TriggerReliability
    scaling: TriggerScaling
    
    # Universal configuration
    connection: TriggerConnection = field(default_factory=TriggerConnection)
    configuration: TriggerConfiguration = field(default_factory=TriggerConfiguration)
    
    # Metadata
    display_name: Optional[str] = None
    description: Optional[str] = None
    
    # Platform-specific raw data (preserved for detailed analysis)
    raw_parameters: Dict[str, Any] = field(default_factory=dict)
    raw_metadata: Dict[str, Any] = field(default_factory=dict)


# Universal trigger pattern mappings
# These map platform-specific modules to universal patterns

WORKFRONT_FUSION_TRIGGER_PATTERNS = {
    "workfront-workfront:watchEvents": {
        "execution_pattern": TriggerExecutionPattern.WEBHOOK,
        "data_source": TriggerDataSource.INTERNAL_PLATFORM,
        "reliability": TriggerReliability.REAL_TIME,
        "scaling": TriggerScaling.SINGLE_ITEM,
    },
    "gateway:CustomWebHook": {
        "execution_pattern": TriggerExecutionPattern.WEBHOOK,
        "data_source": TriggerDataSource.WEBHOOK_RECEIVER,
        "reliability": TriggerReliability.REAL_TIME,
        "scaling": TriggerScaling.SINGLE_ITEM,
    },
    "workfront-workfront:custom": {
        "execution_pattern": TriggerExecutionPattern.SCHEDULED,
        "data_source": TriggerDataSource.EXTERNAL_API,
        "reliability": TriggerReliability.BATCH,
        "scaling": TriggerScaling.BATCH_LIMITED,
    },
    "workfront-workfront:searchv3": {
        "execution_pattern": TriggerExecutionPattern.SCHEDULED,
        "data_source": TriggerDataSource.EXTERNAL_API,
        "reliability": TriggerReliability.BATCH,
        "scaling": TriggerScaling.BATCH_LIMITED,
    },
    "workfront-proof:watch": {
        "execution_pattern": TriggerExecutionPattern.POLLING,
        "data_source": TriggerDataSource.EXTERNAL_API,
        "reliability": TriggerReliability.NEAR_REAL_TIME,
        "scaling": TriggerScaling.BATCH_LIMITED,
    },
    "sftp:TriggerNewFile": {
        "execution_pattern": TriggerExecutionPattern.POLLING,
        "data_source": TriggerDataSource.FILE_SYSTEM,
        "reliability": TriggerReliability.NEAR_REAL_TIME,
        "scaling": TriggerScaling.BATCH_LIMITED,
    },
    "email:TriggerNewEmail": {
        "execution_pattern": TriggerExecutionPattern.POLLING,
        "data_source": TriggerDataSource.EMAIL_SYSTEM,
        "reliability": TriggerReliability.NEAR_REAL_TIME,
        "scaling": TriggerScaling.BATCH_LIMITED,
    },
    "util:SetVariables": {
        "execution_pattern": TriggerExecutionPattern.MANUAL,
        "data_source": TriggerDataSource.USER_INTERFACE,
        "reliability": TriggerReliability.REAL_TIME,
        "scaling": TriggerScaling.SINGLE_ITEM,
    },
    "json:ParseJSON": {
        "execution_pattern": TriggerExecutionPattern.MANUAL,
        "data_source": TriggerDataSource.USER_INTERFACE,
        "reliability": TriggerReliability.REAL_TIME,
        "scaling": TriggerScaling.SINGLE_ITEM,
    },
    "datastore:SearchRecord": {
        "execution_pattern": TriggerExecutionPattern.SCHEDULED,
        "data_source": TriggerDataSource.DATABASE,
        "reliability": TriggerReliability.BATCH,
        "scaling": TriggerScaling.BATCH_LIMITED,
    },
}

# Make.com patterns (expandable as we analyze more Make.com blueprints)
MAKE_COM_TRIGGER_PATTERNS = {
    "gateway:CustomWebHook": {
        "execution_pattern": TriggerExecutionPattern.WEBHOOK,
        "data_source": TriggerDataSource.WEBHOOK_RECEIVER,
        "reliability": TriggerReliability.REAL_TIME,
        "scaling": TriggerScaling.SINGLE_ITEM,
    },
    "email:TriggerNewEmail": {
        "execution_pattern": TriggerExecutionPattern.POLLING,
        "data_source": TriggerDataSource.EMAIL_SYSTEM,
        "reliability": TriggerReliability.NEAR_REAL_TIME,
        "scaling": TriggerScaling.BATCH_LIMITED,
    },
    "json:ParseJSON": {
        "execution_pattern": TriggerExecutionPattern.MANUAL,
        "data_source": TriggerDataSource.USER_INTERFACE,
        "reliability": TriggerReliability.REAL_TIME,
        "scaling": TriggerScaling.SINGLE_ITEM,
    },
}

# Future platform patterns can be added here:
# N8N_TRIGGER_PATTERNS = {...}
# POWER_PLATFORM_TRIGGER_PATTERNS = {...}
# ZAPIER_TRIGGER_PATTERNS = {...}