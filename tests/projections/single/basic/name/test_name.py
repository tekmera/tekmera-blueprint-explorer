"""
Integration tests for name extraction across platforms.
"""

import pytest

from tekmera.projections.meta.types import Platform, UnsupportedPlatformError
from tekmera.projections.single.basic.name import name


class TestNameIntegration:
    """Integration tests for name projection function across platforms."""
    
    def test_platform_auto_detection_workfront_fusion(self):
        """Test automatic platform detection for Workfront Fusion."""
        blueprint = {
            "name": "Auto-detected Fusion",
            "flow": [],
            "metadata": {}
        }
        
        result = name(blueprint)
        
        assert result.platform == Platform.WORKFRONT_FUSION
        assert result.data == "Auto-detected Fusion"
    
    def test_platform_auto_detection_make_com(self):
        """Test automatic platform detection for Make.com."""
        blueprint = {
            "name": "Auto-detected Make",
            "scenario": {
                "modules": []
            }
        }
        
        result = name(blueprint)
        
        assert result.platform == Platform.MAKE_COM
        assert result.data == "Auto-detected Make"
    
    def test_explicit_platform_override(self):
        """Test explicit platform override."""
        blueprint = {
            "name": "Override Test",
            "flow": [],
            "metadata": {}
        }
        
        result = name(blueprint, platform=Platform.WORKFRONT_FUSION)
        
        assert result.platform == Platform.WORKFRONT_FUSION
        assert result.data == "Override Test"
    
    def test_unsupported_platform_detection(self):
        """Test error for unsupported platform structure."""
        blueprint = {
            "name": "Unknown Structure",
            "unknown_field": True
        }
        
        with pytest.raises(UnsupportedPlatformError) as exc_info:
            name(blueprint)
        
        assert "Unable to detect platform" in str(exc_info.value)
    
    def test_consistent_blueprint_id_generation(self):
        """Test that identical blueprints generate identical IDs."""
        blueprint1 = {
            "name": "Test Consistency",
            "flow": [],
            "metadata": {}
        }
        
        blueprint2 = {
            "name": "Test Consistency",
            "flow": [],
            "metadata": {}
        }
        
        result1 = name(blueprint1)
        result2 = name(blueprint2)
        
        assert result1.blueprint_id == result2.blueprint_id
        assert result1.metadata.input_hash == result2.metadata.input_hash
    
    def test_input_immutability(self):
        """Test that input blueprints are never modified."""
        original_blueprint = {
            "name": "Immutability Test",
            "flow": [{"id": 1, "module": "test"}],
            "metadata": {"test": "data"}
        }
        
        blueprint_copy = original_blueprint.copy()
        name(blueprint_copy)
        
        assert blueprint_copy == original_blueprint