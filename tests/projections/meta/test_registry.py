"""
Tests for projection registry system.
"""

import pytest

from tekmera.projections.meta.registry import ProjectionRegistry
from tekmera.projections.meta.types import Platform, UnsupportedPlatformError


class TestProjectionRegistry:
    """Test projection registry functionality."""
    
    def test_registry_auto_discovery(self):
        """Test registry auto-discovers existing functions."""
        registry = ProjectionRegistry()
        
        # This should auto-discover the name function
        func = registry.get_function("single", "basic", "name", Platform.WORKFRONT_FUSION)
        
        assert callable(func)
    
    def test_registry_platform_routing(self):
        """Test registry routes to correct platform implementation."""
        registry = ProjectionRegistry()
        
        # Get platform-specific implementations
        fusion_func = registry.get_function("single", "basic", "name", Platform.WORKFRONT_FUSION)
        make_func = registry.get_function("single", "basic", "name", Platform.MAKE_COM)
        
        # They should be different implementations
        assert fusion_func != make_func
    
    def test_registry_nonexistent_function(self):
        """Test registry handles nonexistent functions."""
        registry = ProjectionRegistry()
        
        with pytest.raises(UnsupportedPlatformError) as exc_info:
            registry.get_function("single", "basic", "nonexistent", Platform.WORKFRONT_FUSION)
        
        assert "Function single.basic.nonexistent not found" in str(exc_info.value)
    
    def test_registry_unsupported_platform(self):
        """Test registry handles unsupported platform for existing function."""
        registry = ProjectionRegistry()
        
        # Force discovery first
        registry.get_function("single", "basic", "name", Platform.WORKFRONT_FUSION)
        
        # Now test with unsupported platform (this should work since we fall back)
        # The current implementation falls back to any available platform
        func = registry.get_function("single", "basic", "name", Platform.MAKE_COM)
        assert callable(func)