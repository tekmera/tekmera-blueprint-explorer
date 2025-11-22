"""
Tests for Workfront Fusion module count extraction.
"""

import pytest

from tekmera.functions.meta.types import Platform
from tekmera.functions.single.basic.module_count.workfront_fusion import module_count


class TestWorkfrontFusionModuleCount:
    """Test Workfront Fusion module count extraction following required test patterns."""

    def test_module_count_blue_sky(self):
        """Blue sky: Happy path test with typical Workfront Fusion blueprint."""
        blueprint = {
            "name": "Test Scenario",
            "flow": [
                {"id": 1, "module": "workfront-workfront:searchv3"},
                {"id": 2, "module": "workfront-workfront:create"},
                {"id": 3, "module": "util:SetVariable2"},
            ],
            "metadata": {"designer": {"orphans": []}},
        }

        result = module_count(blueprint)

        assert result.platform == Platform.WORKFRONT_FUSION
        assert result.data == 3
        assert result.metadata.function == "single.basic.module_count"

    def test_module_count_complex_case(self):
        """Complex: Edge case with nested flows, routes, error handlers, and orphans."""
        blueprint = {
            "name": "Complex Scenario",
            "flow": [
                {
                    "id": 1,
                    "module": "workfront-workfront:searchv3",
                    "routes": [
                        {
                            "flow": [
                                {"id": 4, "module": "nested-module-1"},
                                {"id": 5, "module": "nested-module-2"},
                            ]
                        }
                    ],
                    "onerror": [{"id": 6, "module": "error-handler"}],
                },
                {"id": 2, "module": "workfront-workfront:create"},
                {
                    "id": 3,
                    "module": "util:SetVariable2",
                    "routes": [
                        {
                            "flow": [
                                {
                                    "id": 7,
                                    "module": "deeply-nested",
                                    "onerror": [{"id": 8, "module": "deep-error-handler"}],
                                }
                            ]
                        }
                    ],
                },
            ],
            "metadata": {
                "designer": {
                    "orphans": [
                        [
                            {"id": 99, "module": "orphaned-module-1"},
                            {"id": 100, "module": "orphaned-module-2"},
                        ]
                    ]
                }
            },
        }

        result = module_count(blueprint)

        # Main flow: 3, nested in routes: 3, error handlers: 2, orphans: 2 = 10 total
        assert result.data == 10
        assert result.platform == Platform.WORKFRONT_FUSION

    def test_module_count_error_missing_flow(self):
        """Error handling: Blueprint without flow field returns 0."""
        blueprint = {"name": "No Flow Scenario", "metadata": {}}

        result = module_count(blueprint)

        assert result.data == 0
        assert result.platform == Platform.WORKFRONT_FUSION

    def test_module_count_error_empty_flow(self):
        """Error handling: Blueprint with empty flow returns 0."""
        blueprint = {"name": "Empty Flow Scenario", "flow": [], "metadata": {}}

        result = module_count(blueprint)

        assert result.data == 0

    def test_module_count_error_invalid_flow(self):
        """Error handling: Blueprint with invalid flow type returns 0."""
        blueprint = {"name": "Invalid Flow Scenario", "flow": "not-an-array", "metadata": {}}

        result = module_count(blueprint)

        assert result.data == 0
