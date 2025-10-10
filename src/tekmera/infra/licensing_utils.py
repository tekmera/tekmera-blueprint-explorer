"""
Centralized licensing utilities to eliminate code duplication and improve DRY compliance.
"""
from typing import Dict, Callable, Optional, Any
from functools import wraps
from ..config.menu_system import menu_system
from ..config.premium_features import PremiumFeatureConfig
from .license import license_manager


class LicenseEnforcer:
    """Centralized license enforcement utility."""
    
    @staticmethod
    def require_license(item_id: str, console=None):
        """Decorator for methods that require license checking."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                # Get the menu item for license requirements
                item = menu_system.get_item(item_id)
                if not item:
                    # If menu item not found, assume it's free
                    return func(self, *args, **kwargs)
                
                # Check license using menu system
                context = getattr(self, 'context', license_manager.get_context())
                if not menu_system.can_execute(item, context):
                    # Use provided console or try to get from self
                    console_obj = console or getattr(self, 'console', None)
                    license_manager.show_premium_prompt(item.label, console_obj)
                    return False
                
                return func(self, *args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def check_feature_access(item_id: str, context: Dict[str, Any], console=None) -> bool:
        """Check if a feature can be accessed with current license."""
        item = menu_system.get_item(item_id)
        if not item:
            return True  # Unknown features are free
        
        if not menu_system.can_execute(item, context):
            if console:
                license_manager.show_premium_prompt(item.label, console)
            return False
        
        return True


class FeatureRegistry:
    """Centralized feature configuration registry."""
    
    # Action to menu item ID mappings - single source of truth
    ACTION_MAPPINGS = {
        # Scenario exploration actions
        "explore_modules": "explore.modules",
        "trace_flow": "explore.walkthrough", 
        "describe_process": "explore.ai_process",
        
        # Analysis actions
        "static_report": "analyze.report",
        "cross_search": "analyze.search",
    }
    
    @classmethod
    def get_menu_item_id(cls, action: str) -> Optional[str]:
        """Get menu item ID for an action."""
        return cls.ACTION_MAPPINGS.get(action)
    
    @classmethod
    def is_premium_action(cls, action: str, context: Dict[str, Any]) -> bool:
        """Check if an action requires premium license."""
        item_id = cls.get_menu_item_id(action)
        if not item_id:
            return False
        
        item = menu_system.get_item(item_id)
        return item and not menu_system.can_execute(item, context)
    
    @classmethod
    def get_all_premium_features(cls) -> Dict[str, str]:
        """Get all premium features with their display names."""
        premium_features = {}
        for action, item_id in cls.ACTION_MAPPINGS.items():
            if PremiumFeatureConfig.is_premium_menu_item(item_id):
                item = menu_system.get_item(item_id)
                premium_features[action] = item.label if item else action
        return premium_features


def execute_with_license_check(action: str, context: Dict[str, Any], 
                              execute_func: Callable, console=None) -> bool:
    """Execute an action with license checking. Returns True if executed, False if blocked."""
    item_id = FeatureRegistry.get_menu_item_id(action)
    
    if item_id and not LicenseEnforcer.check_feature_access(item_id, context, console):
        return False
    
    # Execute the action
    try:
        execute_func()
        return True
    except Exception as e:
        if console:
            console.print(f"[red]Error executing {action}: {e}[/red]")
        return False