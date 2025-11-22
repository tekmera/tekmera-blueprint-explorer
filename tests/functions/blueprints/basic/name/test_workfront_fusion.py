"""
Tests for Workfront Fusion name extraction.
"""

import pytest

from tekmera.functions.meta.types import Platform
from tekmera.functions.single.basic.name.workfront_fusion import name


class TestWorkfrontFusionName:
    """Test Workfront Fusion name extraction following required test patterns."""

    def test_name_blue_sky(self):
        """Blue sky: Happy path test with typical Workfront Fusion blueprint."""
        blueprint = {
            "name": "My Fusion Scenario",
            "flow": [{"id": 1, "module": "workfront-workfront:searchv3"}],
            "metadata": {"designer": {"orphans": []}},
        }

        result = name(blueprint)

        assert result.platform == Platform.WORKFRONT_FUSION
        assert result.data == "My Fusion Scenario"
        assert result.blueprint_name == "My Fusion Scenario"
        assert result.metadata.function == "single.basic.name"
        assert result.metadata.version == "1.0.0"
        assert result.metadata.input_hash is not None
        assert len(result.metadata.input_hash) == 8

    def test_name_complex_case(self):
        """Complex: Edge case with special characters, unicode, and unusual formatting."""
        blueprint = {
            "name": "🚀 Complex Scenario: Test | With-Special_Characters & Symbols (v2.1) — Updated 2024",
            "flow": [],
            "metadata": {"designer": {"orphans": [[{"id": 99, "module": "orphaned-module"}]]}},
        }

        result = name(blueprint)

        assert (
            result.data
            == "🚀 Complex Scenario: Test | With-Special_Characters & Symbols (v2.1) — Updated 2024"
        )
        assert result.platform == Platform.WORKFRONT_FUSION
        assert result.blueprint_name == result.data

    def test_name_error_missing_name(self):
        """Error handling: Blueprint without name field defaults to 'Unnamed Scenario'."""
        blueprint = {"flow": [], "metadata": {}}

        result = name(blueprint)

        assert result.data == "Unnamed Scenario"
        assert result.blueprint_name == "Unnamed Scenario"
        assert result.platform == Platform.WORKFRONT_FUSION

    def test_name_error_empty_name(self):
        """Error handling: Blueprint with empty name defaults to 'Unnamed Scenario'."""
        blueprint = {"name": "", "flow": [], "metadata": {}}

        result = name(blueprint)

        assert result.data == "Unnamed Scenario"
        assert result.blueprint_name == "Unnamed Scenario"

    def test_name_error_null_name(self):
        """Error handling: Blueprint with null name defaults to 'Unnamed Scenario'."""
        blueprint = {"name": None, "flow": [], "metadata": {}}

        result = name(blueprint)

        assert result.data == "Unnamed Scenario"
        assert result.blueprint_name == "Unnamed Scenario"
