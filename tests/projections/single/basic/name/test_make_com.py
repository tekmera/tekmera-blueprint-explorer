"""
Tests for Make.com name extraction.
"""

import pytest

from tekmera.projections.meta.types import Platform
from tekmera.projections.single.basic.name.make_com import name


class TestMakeComName:
    """Test Make.com name extraction following required test patterns."""
    
    def test_name_blue_sky(self):
        """Blue sky: Happy path test with typical Make.com blueprint."""
        blueprint = {
            "name": "My Make Scenario",
            "scenario": {
                "modules": [
                    {
                        "id": 18,
                        "module": "util:SetVariable2"
                    }
                ]
            }
        }
        
        result = name(blueprint)
        
        assert result.platform == Platform.MAKE_COM
        assert result.data == "My Make Scenario"
        assert result.blueprint_name == "My Make Scenario"
        assert result.metadata.function == "single.basic.name"
        assert result.metadata.version == "1.0.0"
        assert result.metadata.input_hash is not None
        assert len(result.metadata.input_hash) == 8
    
    def test_name_complex_case(self):
        """Complex: Edge case with special characters, unicode, and unusual formatting."""
        blueprint = {
            "name": "⚡ Advanced Automation: Data Processing & API Integration (2024) — Version 3.5",
            "scenario": {
                "modules": [],
                "metadata": {
                    "version": "3.5",
                    "tags": ["production", "critical"]
                }
            }
        }
        
        result = name(blueprint)
        
        assert result.data == "⚡ Advanced Automation: Data Processing & API Integration (2024) — Version 3.5"
        assert result.platform == Platform.MAKE_COM
        assert result.blueprint_name == result.data
    
    def test_name_error_missing_name(self):
        """Error handling: Blueprint without name field defaults to 'Unnamed Scenario'."""
        blueprint = {
            "scenario": {
                "modules": []
            }
        }
        
        result = name(blueprint)
        
        assert result.data == "Unnamed Scenario"
        assert result.blueprint_name == "Unnamed Scenario"
        assert result.platform == Platform.MAKE_COM
    
    def test_name_error_empty_name(self):
        """Error handling: Blueprint with empty name defaults to 'Unnamed Scenario'."""
        blueprint = {
            "name": "",
            "scenario": {
                "modules": []
            }
        }
        
        result = name(blueprint)
        
        assert result.data == "Unnamed Scenario"
        assert result.blueprint_name == "Unnamed Scenario"
    
    def test_name_error_null_name(self):
        """Error handling: Blueprint with null name defaults to 'Unnamed Scenario'."""
        blueprint = {
            "name": None,
            "scenario": {
                "modules": []
            }
        }
        
        result = name(blueprint)
        
        assert result.data == "Unnamed Scenario"
        assert result.blueprint_name == "Unnamed Scenario"