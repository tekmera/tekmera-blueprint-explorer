"""
Centralized premium feature configuration.
Single source of truth for which features require premium licenses.
"""
from typing import Set, Dict, Any
from ..infra.license import LicenseType


class PremiumFeatureConfig:
    """Centralized configuration for premium features."""
    
    # Core premium features defined in menu system
    PREMIUM_MENU_ITEMS: Set[str] = {
        "explore.walkthrough",      # Live Scenario Walkthrough
        "explore.ai_process",       # Describe Business Process
        "analyze.search",           # Search across all blueprints
        # Premium governance checks
        "governance.check_6",       # Flow Complexity Index
        "governance.check_7",       # Functional Density Index
        "governance.check_8",       # Router Density Analysis
        "governance.check_9",       # Route Fan-Out Profile
        "governance.check_10",      # Flow Depth Estimate
        "governance.check_11",      # Field Mapping Complexity
    }
    
    
    # Feature requirements beyond just premium license
    FEATURE_REQUIREMENTS: Dict[str, Dict[str, Any]] = {
        "explore.ai_process": {
            "premium": True,
            "requires_openai": True,
            "description": "AI-powered business process analysis requires OpenAI API key"
        },
        "explore.walkthrough": {
            "premium": True,
            "requires_openai": False,
            "description": "Interactive step-by-step execution flow"
        },
        "analyze.search": {
            "premium": True,
            "requires_openai": False,
            "description": "Advanced cross-blueprint search capabilities"
        }
    }
    
    @classmethod
    def is_premium_menu_item(cls, item_id: str) -> bool:
        """Check if a menu item requires premium license."""
        return item_id in cls.PREMIUM_MENU_ITEMS
    
    
    @classmethod
    def get_feature_requirements(cls, item_id: str) -> Dict[str, Any]:
        """Get all requirements for a feature."""
        return cls.FEATURE_REQUIREMENTS.get(item_id, {
            "premium": cls.is_premium_menu_item(item_id),
            "requires_openai": False,
            "description": ""
        })
    
    @classmethod
    def requires_openai(cls, item_id: str) -> bool:
        """Check if a feature requires OpenAI API key."""
        return cls.FEATURE_REQUIREMENTS.get(item_id, {}).get("requires_openai", False)
    
    @classmethod
    def get_all_premium_features(cls) -> Dict[str, Dict[str, Any]]:
        """Get all premium features with their requirements."""
        premium_features = {}
        
        # Add all premium menu items (includes governance checks)
        for item_id in cls.PREMIUM_MENU_ITEMS:
            premium_features[item_id] = cls.get_feature_requirements(item_id)
        
        return premium_features
    
    @classmethod
    def validate_configuration(cls) -> bool:
        """Validate that the premium feature configuration is consistent."""
        # Check that all premium menu items have requirements defined
        missing_requirements = cls.PREMIUM_MENU_ITEMS - set(cls.FEATURE_REQUIREMENTS.keys())
        if missing_requirements:
            print(f"Warning: Premium menu items missing requirements: {missing_requirements}")
            return False
        
        # Check that all features marked as premium in requirements are in premium set
        for item_id, requirements in cls.FEATURE_REQUIREMENTS.items():
            if requirements.get("premium", False) and item_id not in cls.PREMIUM_MENU_ITEMS:
                print(f"Warning: Feature {item_id} marked premium in requirements but not in PREMIUM_MENU_ITEMS")
                return False
        
        return True