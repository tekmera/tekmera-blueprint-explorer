"""Tests for Workfront Fusion trigger detection."""

import pytest

from tekmera.projections.components.triggers.detection.workfront_fusion import detect_trigger
from tekmera.projections.meta.trigger_types import (
    TriggerExecutionPattern,
    TriggerDataSource,
    TriggerReliability,
    TriggerScaling,
)
from tekmera.projections.meta.types import Platform


class TestWorkfrontFusionTriggerDetection:
    """Test cases for Workfront Fusion trigger detection."""

    def test_workfront_event_watcher(self):
        """Test detection of Workfront event watcher trigger."""
        blueprint = {
            "name": "Test Issue Listener",
            "flow": [
                {
                    "id": 1,
                    "module": "workfront-workfront:watchEvents",
                    "parameters": {
                        "maxResults": 1,
                        "__IMTHOOK__": 6902
                    },
                    "metadata": {
                        "designer": {"name": "Watch Issues"},
                        "restore": {
                            "__IMTHOOK__": {"label": "Test Issue Hook"}
                        }
                    }
                }
            ]
        }
        
        result = detect_trigger(blueprint)
        trigger = result.data
        
        assert trigger.platform == Platform.WORKFRONT_FUSION
        assert trigger.module_id == 1
        assert trigger.module_type == "workfront-workfront:watchEvents"
        assert trigger.execution_pattern == TriggerExecutionPattern.WEBHOOK
        assert trigger.data_source == TriggerDataSource.INTERNAL_PLATFORM
        assert trigger.reliability == TriggerReliability.REAL_TIME
        assert trigger.scaling == TriggerScaling.SINGLE_ITEM
        assert trigger.display_name == "Watch Issues"
        
        # Check connection details
        assert trigger.connection.requires_auth is True
        assert trigger.connection.connection_type == "webhook"
        assert trigger.connection.connection_id == "6902"
        assert trigger.connection.account_reference == "Test Issue Hook"
        
        # Check configuration
        assert trigger.configuration.batch_size == 1

    def test_custom_webhook(self):
        """Test detection of custom webhook trigger."""
        blueprint = {
            "name": "Test Custom Webhook",
            "flow": [
                {
                    "id": 10,
                    "module": "gateway:CustomWebHook",
                    "parameters": {
                        "hook": 2177826,
                        "maxResults": 1
                    },
                    "metadata": {
                        "designer": {"name": "Custom Hook"},
                        "restore": {
                            "parameters": {
                                "hook": {"label": "Test Custom Hook"}
                            }
                        }
                    }
                }
            ]
        }
        
        result = detect_trigger(blueprint)
        trigger = result.data
        
        assert trigger.module_type == "gateway:CustomWebHook"
        assert trigger.execution_pattern == TriggerExecutionPattern.WEBHOOK
        assert trigger.data_source == TriggerDataSource.WEBHOOK_RECEIVER
        assert trigger.connection.connection_type == "custom_webhook"
        assert trigger.connection.connection_id == "2177826"

    def test_workfront_api_scheduled(self):
        """Test detection of scheduled Workfront API trigger."""
        blueprint = {
            "name": "Test API Scheduler",
            "flow": [
                {
                    "id": 2,
                    "module": "workfront-workfront:custom",
                    "parameters": {
                        "__IMTCONN__": 3757,
                        "url": "PRGM/search",
                        "method": "GET",
                        "qs": {
                            "DE:typeOfProject": "Execution"
                        }
                    },
                    "metadata": {
                        "designer": {"name": "Search Programs"}
                    }
                }
            ]
        }
        
        result = detect_trigger(blueprint)
        trigger = result.data
        
        assert trigger.module_type == "workfront-workfront:custom"
        assert trigger.execution_pattern == TriggerExecutionPattern.SCHEDULED
        assert trigger.data_source == TriggerDataSource.EXTERNAL_API
        assert trigger.reliability == TriggerReliability.BATCH
        assert trigger.connection.connection_type == "api"
        assert trigger.connection.connection_id == "3757"
        assert "DE:typeOfProject" in trigger.configuration.filter_conditions

    def test_proof_system_watcher(self):
        """Test detection of proof system watcher trigger."""
        blueprint = {
            "name": "Test Proof Listener",
            "flow": [
                {
                    "id": 1,
                    "module": "workfront-proof:watch",
                    "parameters": {
                        "type": "proofDecision",
                        "limit": 20,
                        "fields": ["decision", "status", "stages"],
                        "decision": "all",
                        "__IMTCONN__": 2848
                    },
                    "metadata": {
                        "designer": {"name": "Watch Proof Decisions"}
                    }
                }
            ]
        }
        
        result = detect_trigger(blueprint)
        trigger = result.data
        
        assert trigger.module_type == "workfront-proof:watch"
        assert trigger.execution_pattern == TriggerExecutionPattern.POLLING
        assert trigger.data_source == TriggerDataSource.EXTERNAL_API
        assert trigger.reliability == TriggerReliability.NEAR_REAL_TIME
        assert trigger.configuration.batch_size == 20
        assert trigger.connection.connection_id == "2848"

    def test_sftp_file_monitor(self):
        """Test detection of SFTP file monitor trigger."""
        blueprint = {
            "name": "Test SFTP Monitor",
            "flow": [
                {
                    "id": 70,
                    "module": "sftp:TriggerNewFile",
                    "parameters": {
                        "path": "/OUTGOING/TEST/",
                        "account": 74381,
                        "maxResults": 2,
                        "highWaterMark": 65536
                    },
                    "metadata": {
                        "designer": {"name": "Watch Files"}
                    }
                }
            ]
        }
        
        result = detect_trigger(blueprint)
        trigger = result.data
        
        assert trigger.module_type == "sftp:TriggerNewFile"
        assert trigger.execution_pattern == TriggerExecutionPattern.POLLING
        assert trigger.data_source == TriggerDataSource.FILE_SYSTEM
        assert trigger.connection.connection_type == "account"
        assert trigger.connection.account_reference == "74381"
        assert trigger.configuration.batch_size == 2
        assert trigger.configuration.timeout_seconds == 64  # highWaterMark / 1024

    def test_email_monitor(self):
        """Test detection of email monitor trigger."""
        blueprint = {
            "name": "Test Email Monitor",
            "flow": [
                {
                    "id": 1,
                    "module": "email:TriggerNewEmail",
                    "parameters": {
                        "folder": "INBOX",
                        "account": 4095630,
                        "subject": "booking_1",
                        "criteria": "ALL",
                        "maxResults": 1
                    },
                    "metadata": {
                        "designer": {"name": "Watch Emails"}
                    }
                }
            ]
        }
        
        result = detect_trigger(blueprint)
        trigger = result.data
        
        assert trigger.module_type == "email:TriggerNewEmail"
        assert trigger.execution_pattern == TriggerExecutionPattern.POLLING
        assert trigger.data_source == TriggerDataSource.EMAIL_SYSTEM
        assert trigger.connection.account_reference == "4095630"
        assert trigger.configuration.batch_size == 1

    def test_variable_initializer(self):
        """Test detection of variable initializer trigger."""
        blueprint = {
            "name": "Test Variable Init",
            "flow": [
                {
                    "id": 20,
                    "module": "util:SetVariables",
                    "parameters": {
                        "scope": "execution"
                    },
                    "metadata": {
                        "designer": {"name": "Set Variables"}
                    }
                }
            ]
        }
        
        result = detect_trigger(blueprint)
        trigger = result.data
        
        assert trigger.module_type == "util:SetVariables"
        assert trigger.execution_pattern == TriggerExecutionPattern.MANUAL
        assert trigger.data_source == TriggerDataSource.USER_INTERFACE
        assert trigger.reliability == TriggerReliability.REAL_TIME
        assert trigger.connection.requires_auth is False

    def test_json_parser(self):
        """Test detection of JSON parser trigger."""
        blueprint = {
            "name": "Test JSON Parser",
            "flow": [
                {
                    "id": 1,
                    "module": "json:ParseJSON",
                    "parameters": {
                        "type": ""
                    },
                    "mapper": {
                        "json": '{"test": "data"}'
                    },
                    "metadata": {
                        "designer": {"name": "Parse JSON"}
                    }
                }
            ]
        }
        
        result = detect_trigger(blueprint)
        trigger = result.data
        
        assert trigger.module_type == "json:ParseJSON"
        assert trigger.execution_pattern == TriggerExecutionPattern.MANUAL
        assert trigger.data_source == TriggerDataSource.USER_INTERFACE

    def test_datastore_query(self):
        """Test detection of datastore query trigger."""
        blueprint = {
            "name": "Test Datastore Query",
            "flow": [
                {
                    "id": 1,
                    "module": "datastore:SearchRecord",
                    "parameters": {
                        "datastore": 1185,
                        "limit": None,
                        "continueWhenNoRes": False,
                        "name": "EYK | IKP"
                    },
                    "metadata": {
                        "designer": {"name": "Search Records"}
                    }
                }
            ]
        }
        
        result = detect_trigger(blueprint)
        trigger = result.data
        
        assert trigger.module_type == "datastore:SearchRecord"
        assert trigger.execution_pattern == TriggerExecutionPattern.SCHEDULED
        assert trigger.data_source == TriggerDataSource.DATABASE
        assert "name" in trigger.configuration.filter_conditions
        assert trigger.configuration.filter_conditions["name"] == "EYK | IKP"

    def test_unknown_trigger_type(self):
        """Test handling of unknown trigger type."""
        blueprint = {
            "name": "Test Unknown Trigger",
            "flow": [
                {
                    "id": 1,
                    "module": "unknown:TriggerType",
                    "parameters": {},
                    "metadata": {
                        "designer": {"name": "Unknown Trigger"}
                    }
                }
            ]
        }
        
        result = detect_trigger(blueprint)
        trigger = result.data
        
        assert trigger.module_type == "unknown:TriggerType"
        assert trigger.execution_pattern == TriggerExecutionPattern.MANUAL
        assert trigger.data_source == TriggerDataSource.USER_INTERFACE
        assert trigger.reliability == TriggerReliability.BEST_EFFORT
        assert trigger.scaling == TriggerScaling.SINGLE_ITEM

    def test_no_flow(self):
        """Test error handling when no flow is present."""
        blueprint = {"name": "No Flow Blueprint"}
        
        with pytest.raises(ValueError, match="No flow found in blueprint"):
            detect_trigger(blueprint)

    def test_empty_flow(self):
        """Test error handling when flow is empty."""
        blueprint = {"name": "Empty Flow", "flow": []}
        
        with pytest.raises(ValueError, match="No trigger module found in flow"):
            detect_trigger(blueprint)

    def test_multiple_modules_lowest_id_selected(self):
        """Test that module with lowest ID is selected as trigger."""
        blueprint = {
            "name": "Multiple Modules",
            "flow": [
                {
                    "id": 5,
                    "module": "workfront-workfront:custom",
                    "parameters": {},
                    "metadata": {"designer": {"name": "Second Module"}}
                },
                {
                    "id": 1,
                    "module": "workfront-workfront:watchEvents",
                    "parameters": {"__IMTHOOK__": 123, "maxResults": 1},
                    "metadata": {"designer": {"name": "First Module"}}
                },
                {
                    "id": 3,
                    "module": "util:SetVariables",
                    "parameters": {},
                    "metadata": {"designer": {"name": "Third Module"}}
                }
            ]
        }
        
        result = detect_trigger(blueprint)
        trigger = result.data
        
        assert trigger.module_id == 1
        assert trigger.module_type == "workfront-workfront:watchEvents"
        assert trigger.display_name == "First Module"