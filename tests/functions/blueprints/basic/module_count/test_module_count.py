"""
Integration tests for module count extraction across platforms.
"""

import pytest

from tekmera.functions import project
from tekmera.functions.meta.types import Platform, UnsupportedPlatformError


class TestModuleCountIntegration:
    """Integration tests for module count projection function across platforms."""

    def test_platform_auto_detection_workfront_fusion(self):
        """Test automatic platform detection for Workfront Fusion."""
        blueprint = {
            "name": "Auto-detected Fusion",
            "flow": [{"id": 1, "module": "test-module"}],
            "metadata": {},
        }

        result = project("blueprints", "basic", "module_count", blueprint)

        assert result.platform == Platform.WORKFRONT_FUSION
        assert result.data == 1

    def test_platform_auto_detection_make_com(self):
        """Test automatic platform detection for Make.com."""
        blueprint = {
            "name": "Auto-detected Make",
            "flow": [{"id": 1, "module": "test-module"}, {"id": 2, "module": "another-module"}],
            "metadata": {"zone": "us1.make.com"},
        }

        result = project("blueprints", "basic", "module_count", blueprint)

        assert result.platform == Platform.MAKE_COM
        assert result.data == 2

    def test_explicit_platform_override(self):
        """Test explicit platform override."""
        blueprint = {
            "name": "Override Test",
            "flow": [{"id": 1, "module": "test-module"}],
            "metadata": {},
        }

        result = project(
            "blueprints", "basic", "module_count", blueprint, platform=Platform.WORKFRONT_FUSION
        )

        assert result.platform == Platform.WORKFRONT_FUSION
        assert result.data == 1

    def test_unsupported_platform_detection(self):
        """Test error for unsupported platform structure."""
        blueprint = {"name": "Unknown Structure", "unknown_field": True}

        with pytest.raises(UnsupportedPlatformError) as exc_info:
            project("blueprints", "basic", "module_count", blueprint)

        assert "Unable to detect platform" in str(exc_info.value)

    def test_consistent_blueprint_id_generation(self):
        """Test that identical blueprints generate identical IDs."""
        blueprint1 = {
            "name": "Test Consistency",
            "flow": [{"id": 1, "module": "test"}],
            "metadata": {},
        }

        blueprint2 = {
            "name": "Test Consistency",
            "flow": [{"id": 1, "module": "test"}],
            "metadata": {},
        }

        result1 = project("blueprints", "basic", "module_count", blueprint1)
        result2 = project("blueprints", "basic", "module_count", blueprint2)

        assert result1.blueprint_id == result2.blueprint_id
        assert result1.metadata.input_hash == result2.metadata.input_hash

    def test_zero_count_scenarios(self):
        """Test various scenarios that should return zero count."""
        # Fusion with empty flow
        fusion_blueprint = {"name": "Empty Fusion", "flow": [], "metadata": {}}

        # Make with empty flow
        make_blueprint = {"name": "Empty Make", "flow": [], "metadata": {"zone": "us1.make.com"}}

        fusion_result = project("blueprints", "basic", "module_count", fusion_blueprint)
        make_result = project("blueprints", "basic", "module_count", make_blueprint)

        assert fusion_result.data == 0
        assert make_result.data == 0
