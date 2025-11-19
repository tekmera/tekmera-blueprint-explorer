"""
Tests for Make.com module count extraction.
"""

import pytest

from tekmera.projections.meta.types import Platform
from tekmera.projections.single.basic.module_count.make_com import module_count


class TestMakeComModuleCount:
    """Test Make.com module count extraction following required test patterns."""
    
    def test_module_count_blue_sky(self):
        """Blue sky: Happy path test with typical Make.com blueprint."""
        blueprint = {
            "name": "Test Make Scenario",
            "flow": [
                {"id": 18, "module": "util:SetVariable2"},
                {"id": 19, "module": "workfront:search"},
                {"id": 20, "module": "http:make-request"}
            ],
            "metadata": {
                "zone": "us1.make.com"
            }
        }
        
        result = module_count(blueprint)
        
        assert result.platform == Platform.MAKE_COM
        assert result.data == 3
        assert result.metadata.function == "single.basic.module_count"
    
    def test_module_count_complex_case(self):
        """Complex: Edge case with nested flows, routes, and error handlers."""
        blueprint = {
            "name": "Complex Make Scenario",
            "flow": [
                {"id": 1, "module": "module-1"},
                {
                    "id": 2, 
                    "module": "module-2",
                    "routes": [
                        {
                            "flow": [
                                {"id": 4, "module": "nested-module-1"},
                                {"id": 5, "module": "nested-module-2"}
                            ]
                        }
                    ]
                },
                {
                    "id": 3,
                    "module": "module-3",
                    "onerror": [
                        {"id": 6, "module": "error-handler"}
                    ]
                }
            ],
            "metadata": {
                "zone": "us1.make.com",
                "version": "2.0"
            }
        }
        
        result = module_count(blueprint)
        
        # Main flow: 3, nested in routes: 2, error handler: 1 = 6 total
        assert result.data == 6
        assert result.platform == Platform.MAKE_COM
    
    def test_module_count_error_missing_flow(self):
        """Error handling: Blueprint without flow field returns 0."""
        blueprint = {
            "name": "No Flow",
            "metadata": {
                "zone": "us1.make.com"
            }
        }
        
        result = module_count(blueprint)
        
        assert result.data == 0
        assert result.platform == Platform.MAKE_COM
    
    def test_module_count_error_empty_flow(self):
        """Error handling: Blueprint with empty flow array returns 0."""
        blueprint = {
            "name": "Empty Flow Scenario",
            "flow": [],
            "metadata": {
                "zone": "us1.make.com"
            }
        }
        
        result = module_count(blueprint)
        
        assert result.data == 0
    
    def test_module_count_error_invalid_flow(self):
        """Error handling: Blueprint with invalid flow type returns 0."""
        blueprint = {
            "name": "Invalid Flow Scenario",
            "flow": "not-an-array",
            "metadata": {
                "zone": "us1.make.com"
            }
        }
        
        result = module_count(blueprint)
        
        assert result.data == 0