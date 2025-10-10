"""
License management and paywall enforcement for Tekmera Fusion Explorer
"""
import sys
from enum import Enum
from typing import Dict, Any


class LicenseType(Enum):
    FREE = "free"
    PREMIUM = "premium"


class LicenseManager:
    """Manages license validation and feature gating"""
    
    def __init__(self, license_type: LicenseType = LicenseType.FREE):
        self.license_type = license_type
    
    def has_premium(self) -> bool:
        """Check if user has premium license"""
        return self.license_type == LicenseType.PREMIUM
    
    def can_access_feature(self, required_license: LicenseType) -> bool:
        """Check if current license allows access to a feature"""
        if required_license == LicenseType.FREE:
            return True
        return self.has_premium()
    
    def show_premium_prompt(self, feature_name: str, console=None) -> bool:
        """Show upgrade prompt for premium features - non-interactive safe"""
        if console:
            console.print(f"\n[yellow]🔒 Premium Feature Required[/yellow]")
            console.print(f"[bold]{feature_name}[/bold] requires Tekmera Pro.")
            console.print("Upgrade to unlock advanced governance intelligence and AI features.")
            console.print("\n[dim]Press Enter to continue...[/dim]")
            
            # Guard for TTY and handle EOFError gracefully
            if sys.stdin.isatty():
                try:
                    input()
                except EOFError:
                    pass
        return True
    
    def get_context(self, additional_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get license context for feature evaluation"""
        import os
        
        context = {
            "license": self.license_type.value,
            "openai_api_available": bool(os.getenv('OPENAI_API_KEY'))
        }
        
        if additional_context:
            context.update(additional_context)
            
        return context


# Global license manager instance
license_manager = LicenseManager()