"""Tests for the main trigger detection function."""

import pytest

from tekmera.functions.components.triggers.detection import detect_trigger
from tekmera.functions.meta.trigger_types import TriggerExecutionPattern
from tekmera.functions.meta.types import Platform


class TestTriggerDetection:
    """Test cases for the main trigger detection function."""

    def test_auto_detect_workfront_fusion_platform(self):
        """Test automatic platform detection for Workfront Fusion blueprints."""
        blueprint = {
            "name": "Auto-detect Fusion",
            "flow": [
                {
                    "id": 1,
                    "module": "workfront-workfront:watchEvents",
                    "parameters": {"__IMTHOOK__": 123, "maxResults": 1},
                    "metadata": {"designer": {"name": "Test"}}
                }
            ],
            "metadata": {"some": "workfront-specific-data"}
        }
        
        result = detect_trigger(blueprint)
        trigger = result.data
        
        assert trigger.platform == Platform.WORKFRONT_FUSION
        assert trigger.module_type == "workfront-workfront:watchEvents"

    def test_auto_detect_make_com_platform(self):
        """Test automatic platform detection for Make.com blueprints."""
        blueprint = {
            "name": "Auto-detect Make.com",
            "scenario": {
                "modules": [
                    {
                        "id": 1,
                        "module": "gateway:CustomWebHook",
                        "parameters": {"hook": 123, "maxResults": 1},
                        "metadata": {"designer": {"name": "Test"}}
                    }
                ]
            }
        }
        
        result = detect_trigger(blueprint)
        trigger = result.data
        
        assert trigger.platform == Platform.MAKE_COM
        assert trigger.module_type == "gateway:CustomWebHook"

    def test_explicit_platform_override(self):
        """Test explicit platform override."""
        blueprint = {
            "name": "Platform Override",
            "flow": [
                {
                    "id": 1,
                    "module": "workfront-workfront:watchEvents",
                    "parameters": {"__IMTHOOK__": 123, "maxResults": 1},
                    "metadata": {"designer": {"name": "Test"}}
                }
            ]
        }
        
        result = detect_trigger(blueprint, platform=Platform.WORKFRONT_FUSION)
        trigger = result.data
        
        assert trigger.platform == Platform.WORKFRONT_FUSION

    def test_unsupported_platform_error(self):
        """Test error handling for unsupported platforms."""
        blueprint = {"name": "Test"}
        
        # Create a fake unsupported platform for testing
        class UnsupportedPlatform:
            value = "unsupported_platform"
        
        unsupported = UnsupportedPlatform()
        
        with pytest.raises(ValueError, match="Platform unsupported_platform not supported"):
            detect_trigger(blueprint, platform=unsupported)

    def test_result_metadata(self):
        """Test that result contains proper metadata."""
        blueprint = {
            "name": "Metadata Test",
            "flow": [
                {
                    "id": 1,
                    "module": "util:SetVariables",
                    "parameters": {"scope": "execution"},
                    "metadata": {"designer": {"name": "Variables"}}
                }
            ]
        }
        
        result = detect_trigger(blueprint)
        
        assert result.platform == Platform.WORKFRONT_FUSION
        assert result.metadata.function == "components.triggers.detection"
        assert hasattr(result.metadata, 'computed_at')

    def test_universal_trigger_abstraction(self):
        """Test that triggers are properly abstracted to universal format."""
        # Test Workfront Fusion webhook
        fusion_blueprint = {
            "name": "Fusion Webhook",
            "flow": [
                {
                    "id": 1,
                    "module": "workfront-workfront:watchEvents",
                    "parameters": {"__IMTHOOK__": 123, "maxResults": 1},
                    "metadata": {"designer": {"name": "Fusion Hook"}}
                }
            ]
        }
        
        # Test Make.com webhook  
        make_blueprint = {
            "name": "Make Webhook",
            "scenario": {
                "modules": [
                    {
                        "id": 1,
                        "module": "gateway:CustomWebHook",
                        "parameters": {"hook": 456, "maxResults": 1},
                        "metadata": {"designer": {"name": "Make Hook"}}
                    }
                ]
            }
        }
        
        fusion_result = detect_trigger(fusion_blueprint)
        make_result = detect_trigger(make_blueprint)
        
        # Both should be webhook triggers despite different platforms
        assert fusion_result.data.execution_pattern == TriggerExecutionPattern.WEBHOOK
        assert make_result.data.execution_pattern == TriggerExecutionPattern.WEBHOOK
        
        # But have different platforms and module types
        assert fusion_result.data.platform == Platform.WORKFRONT_FUSION
        assert make_result.data.platform == Platform.MAKE_COM
        assert fusion_result.data.module_type == "workfront-workfront:watchEvents"
        assert make_result.data.module_type == "gateway:CustomWebHook"