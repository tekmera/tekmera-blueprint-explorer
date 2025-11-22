"""
Tests for platform detection logic.
"""

import pytest

from tekmera.functions.meta.platform_detection import detect_platform
from tekmera.functions.meta.types import Platform, UnsupportedPlatformError


class TestPlatformDetection:
    """Test platform detection logic."""

    def test_detect_workfront_fusion(self):
        """Test Workfront Fusion platform detection."""
        blueprint = {"name": "Test Scenario", "flow": [], "metadata": {}}
        assert detect_platform(blueprint) == Platform.WORKFRONT_FUSION

    def test_detect_make_com(self):
        """Test Make.com platform detection via zone."""
        blueprint = {"name": "Test Scenario", "flow": [], "metadata": {"zone": "us1.make.com"}}
        assert detect_platform(blueprint) == Platform.MAKE_COM

    def test_detect_unsupported_platform(self):
        """Test unsupported platform detection."""
        blueprint = {"unknown_structure": True}
        with pytest.raises(UnsupportedPlatformError) as exc_info:
            detect_platform(blueprint)

        assert "Unable to detect platform" in str(exc_info.value)
        assert "Available keys: ['unknown_structure']" in str(exc_info.value)

    def test_detect_empty_blueprint(self):
        """Test empty blueprint handling."""
        blueprint = {}
        with pytest.raises(UnsupportedPlatformError):
            detect_platform(blueprint)
