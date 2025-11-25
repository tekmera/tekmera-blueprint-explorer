"""Tests for Make.com trigger detection."""

import pytest

from tekmera.functions.components.triggers.detection.make_com import detect_trigger
from tekmera.functions.meta.trigger_types import (
    TriggerDataSource,
    TriggerExecutionPattern,
    TriggerReliability,
    TriggerScaling,
)
from tekmera.functions.meta.types import Platform


class TestMakeComTriggerDetection:
    """Test cases for Make.com trigger detection."""

    def test_custom_webhook(self):
        """Test detection of custom webhook trigger."""
        blueprint = {
            "name": "GAC MA C05 U03 Child 2",
            "scenario": {
                "modules": [
                    {
                        "id": 10,
                        "module": "gateway:CustomWebHook",
                        "parameters": {"hook": 2177826, "maxResults": 1},
                        "metadata": {
                            "designer": {"name": "Custom Webhook"},
                            "restore": {
                                "parameters": {
                                    "hook": {
                                        "data": {"editable": "true"},
                                        "label": "GAC MA C05 U03 CWH2",
                                    }
                                }
                            },
                        },
                    }
                ]
            },
        }

        result = detect_trigger(blueprint)
        trigger = result.data

        assert trigger.platform == Platform.MAKE_COM
        assert trigger.module_id == 10
        assert trigger.module_type == "gateway:CustomWebHook"
        assert trigger.execution_pattern == TriggerExecutionPattern.WEBHOOK
        assert trigger.data_source == TriggerDataSource.WEBHOOK_RECEIVER
        assert trigger.reliability == TriggerReliability.REAL_TIME
        assert trigger.scaling == TriggerScaling.SINGLE_ITEM
        assert trigger.display_name == "Custom Webhook"

        # Check connection details
        assert trigger.connection.requires_auth is False
        assert trigger.connection.connection_type == "custom_webhook"
        assert trigger.connection.connection_id == "2177826"
        assert trigger.connection.account_reference == "GAC MA C05 U03 CWH2"

        # Check configuration
        assert trigger.configuration.batch_size == 1

    def test_email_trigger(self):
        """Test detection of email trigger."""
        blueprint = {
            "name": "GAC Make Advanced C04_U03.1",
            "scenario": {
                "modules": [
                    {
                        "id": 1,
                        "module": "email:TriggerNewEmail",
                        "parameters": {
                            "to": "",
                            "from": "",
                            "text": "",
                            "folder": "INBOX",
                            "account": 4095630,
                            "subject": "booking_1",
                            "criteria": "ALL",
                            "markSeen": False,
                            "maxResults": 1,
                        },
                        "metadata": {"designer": {"name": "Watch Emails"}},
                    }
                ]
            },
        }

        result = detect_trigger(blueprint)
        trigger = result.data

        assert trigger.module_type == "email:TriggerNewEmail"
        assert trigger.execution_pattern == TriggerExecutionPattern.POLLING
        assert trigger.data_source == TriggerDataSource.EMAIL_SYSTEM
        assert trigger.reliability == TriggerReliability.NEAR_REAL_TIME
        assert trigger.scaling == TriggerScaling.BATCH_LIMITED

        # Check connection details
        assert trigger.connection.requires_auth is True
        assert trigger.connection.connection_type == "account"
        assert trigger.connection.account_reference == "4095630"

        # Check configuration
        assert trigger.configuration.batch_size == 1
        # Check email filters
        expected_filters = {"subject": "booking_1", "folder": "INBOX", "criteria": "ALL"}
        for key, value in expected_filters.items():
            assert trigger.configuration.filter_conditions[key] == value

    def test_json_parser_with_data(self):
        """Test detection of JSON parser trigger with sample data."""
        blueprint = {
            "name": "GAC Make Intermediate 2",
            "scenario": {
                "modules": [
                    {
                        "id": 1,
                        "module": "json:ParseJSON",
                        "parameters": {"type": ""},
                        "mapper": {
                            "json": '{"shopping_basket": {"date": "2023-06-07T10:45:26.894Z", "items": []}}'
                        },
                        "metadata": {"designer": {"name": "Parse Shopping Data"}},
                    }
                ]
            },
        }

        result = detect_trigger(blueprint)
        trigger = result.data

        assert trigger.module_type == "json:ParseJSON"
        assert trigger.execution_pattern == TriggerExecutionPattern.MANUAL
        assert trigger.data_source == TriggerDataSource.USER_INTERFACE
        assert trigger.reliability == TriggerReliability.REAL_TIME
        assert trigger.scaling == TriggerScaling.SINGLE_ITEM
        assert trigger.display_name == "Parse Shopping Data"

        # Check configuration for sample data
        assert trigger.configuration.filter_conditions["has_sample_data"] is True
        assert "data_size" in trigger.configuration.filter_conditions

    def test_json_parser_no_data(self):
        """Test detection of JSON parser trigger without sample data."""
        blueprint = {
            "name": "Empty JSON Parser",
            "scenario": {
                "modules": [
                    {
                        "id": 1,
                        "module": "json:ParseJSON",
                        "parameters": {"type": ""},
                        "mapper": {},
                        "metadata": {"designer": {"name": "Parse JSON"}},
                    }
                ]
            },
        }

        result = detect_trigger(blueprint)
        trigger = result.data

        assert trigger.module_type == "json:ParseJSON"
        assert trigger.execution_pattern == TriggerExecutionPattern.MANUAL
        assert len(trigger.configuration.filter_conditions) == 0

    def test_unknown_trigger_type(self):
        """Test handling of unknown Make.com trigger type."""
        blueprint = {
            "name": "Unknown Trigger Test",
            "scenario": {
                "modules": [
                    {
                        "id": 1,
                        "module": "unknown:MakeComTrigger",
                        "parameters": {},
                        "metadata": {"designer": {"name": "Unknown Trigger"}},
                    }
                ]
            },
        }

        result = detect_trigger(blueprint)
        trigger = result.data

        assert trigger.module_type == "unknown:MakeComTrigger"
        assert trigger.execution_pattern == TriggerExecutionPattern.MANUAL
        assert trigger.data_source == TriggerDataSource.USER_INTERFACE
        assert trigger.reliability == TriggerReliability.BEST_EFFORT
        assert trigger.scaling == TriggerScaling.SINGLE_ITEM

    def test_fallback_flow_structure(self):
        """Test fallback to direct flow structure when scenario.modules not found."""
        blueprint = {
            "name": "Direct Flow Structure",
            "flow": [
                {
                    "id": 1,
                    "module": "gateway:CustomWebHook",
                    "parameters": {"hook": 123456, "maxResults": 1},
                    "metadata": {"designer": {"name": "Webhook"}},
                }
            ],
        }

        result = detect_trigger(blueprint)
        trigger = result.data

        assert trigger.module_type == "gateway:CustomWebHook"
        assert trigger.module_id == 1
        assert trigger.connection.connection_id == "123456"

    def test_no_modules_error(self):
        """Test error handling when no modules found."""
        blueprint = {"name": "No Modules", "scenario": {}}

        with pytest.raises(ValueError, match="No modules found in Make.com blueprint"):
            detect_trigger(blueprint)

    def test_empty_modules_error(self):
        """Test error handling when modules array is empty."""
        blueprint = {"name": "Empty Modules", "scenario": {"modules": []}}

        with pytest.raises(ValueError, match="No modules found in Make.com blueprint"):
            detect_trigger(blueprint)

    def test_multiple_modules_lowest_id_selected(self):
        """Test that module with lowest ID is selected as trigger."""
        blueprint = {
            "name": "Multiple Modules",
            "scenario": {
                "modules": [
                    {
                        "id": 15,
                        "module": "json:ParseJSON",
                        "parameters": {},
                        "metadata": {"designer": {"name": "Second Module"}},
                    },
                    {
                        "id": 5,
                        "module": "gateway:CustomWebHook",
                        "parameters": {"hook": 123, "maxResults": 1},
                        "metadata": {"designer": {"name": "First Module"}},
                    },
                    {
                        "id": 10,
                        "module": "email:TriggerNewEmail",
                        "parameters": {"account": 456, "maxResults": 1},
                        "metadata": {"designer": {"name": "Third Module"}},
                    },
                ]
            },
        }

        result = detect_trigger(blueprint)
        trigger = result.data

        assert trigger.module_id == 5
        assert trigger.module_type == "gateway:CustomWebHook"
        assert trigger.display_name == "First Module"

    def test_module_name_fallback(self):
        """Test fallback to parameters.name when designer.name not available."""
        blueprint = {
            "name": "Name Fallback Test",
            "scenario": {
                "modules": [
                    {
                        "id": 1,
                        "module": "gateway:CustomWebHook",
                        "parameters": {
                            "hook": 123,
                            "maxResults": 1,
                            "name": "Webhook from parameters",
                        },
                        "metadata": {},
                    }
                ]
            },
        }

        result = detect_trigger(blueprint)
        trigger = result.data

        assert trigger.display_name == "Webhook from parameters"
