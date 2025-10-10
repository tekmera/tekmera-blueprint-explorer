"""
License management and paywall enforcement for Tekmera Fusion Explorer
"""
import json
import os
import sys
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional


class LicenseType(Enum):
    FREE = "free"
    PREMIUM = "premium"


class LicenseData:
    """Represents a license file content"""
    
    def __init__(self, data: Dict[str, Any]):
        self.license_key = data.get("license_key", "")
        self.edition = data.get("edition", "free")
        self.issued_to = data.get("issued_to", "")
        self.issued_at = data.get("issued_at", "")
        self.expiry = data.get("expiry")  # Optional
        self.signature = data.get("signature")  # Optional for future signing
    
    @classmethod
    def from_file(cls, file_path: Path) -> Optional['LicenseData']:
        """Load license data from file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return cls(data)
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return None
    
    def is_valid(self) -> bool:
        """Check if license is valid (not expired)"""
        if not self.license_key or not self.edition:
            return False
        
        if self.expiry:
            try:
                expiry_date = datetime.fromisoformat(self.expiry.replace('Z', '+00:00'))
                return datetime.now() < expiry_date
            except (ValueError, AttributeError):
                return False
        
        return True
    
    def is_premium(self) -> bool:
        """Check if this is a premium license"""
        return self.edition.lower() in ["pro", "premium", "professional"]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "license_key": self.license_key,
            "edition": self.edition,
            "issued_to": self.issued_to,
            "issued_at": self.issued_at,
            "expiry": self.expiry,
            "signature": self.signature
        }


class LicenseManager:
    """Manages license validation and feature gating"""
    
    def __init__(self, license_type: LicenseType = LicenseType.FREE):
        self.license_type = license_type
        self._license_data: Optional[LicenseData] = None
        self._license_dir = Path.home() / ".tekmera"
        self._license_file = self._license_dir / "license.json"
        
        # Auto-load license on initialization
        self._load_license()
    
    def _load_license(self) -> None:
        """Load license from user's home directory"""
        if self._license_file.exists():
            self._license_data = LicenseData.from_file(self._license_file)
            if self._license_data and self._license_data.is_valid():
                if self._license_data.is_premium():
                    self.license_type = LicenseType.PREMIUM
                else:
                    self.license_type = LicenseType.FREE
            else:
                # Invalid or expired license
                self._license_data = None
                self.license_type = LicenseType.FREE
    
    def activate_license(self, license_file_path: Path) -> tuple[bool, str]:
        """Activate a license from file"""
        try:
            # Load and validate the license
            license_data = LicenseData.from_file(license_file_path)
            if not license_data:
                return False, "Invalid license file format"
            
            if not license_data.is_valid():
                return False, "License is invalid or expired"
            
            # Create license directory if it doesn't exist
            self._license_dir.mkdir(exist_ok=True)
            
            # Copy license to user directory
            with open(self._license_file, 'w') as f:
                json.dump(license_data.to_dict(), f, indent=2)
            
            # Update current state
            self._license_data = license_data
            if license_data.is_premium():
                self.license_type = LicenseType.PREMIUM
            else:
                self.license_type = LicenseType.FREE
            
            return True, f"License activated successfully for {license_data.issued_to}"
            
        except Exception as e:
            return False, f"Failed to activate license: {str(e)}"
    
    def deactivate_license(self) -> tuple[bool, str]:
        """Deactivate current license"""
        try:
            if self._license_file.exists():
                self._license_file.unlink()
            
            self._license_data = None
            self.license_type = LicenseType.FREE
            return True, "License deactivated successfully"
            
        except Exception as e:
            return False, f"Failed to deactivate license: {str(e)}"
    
    def get_license_info(self) -> Dict[str, Any]:
        """Get current license information"""
        if self._license_data and self._license_data.is_valid():
            info = {
                "status": "active",
                "edition": self._license_data.edition,
                "license_key": self._license_data.license_key,
                "issued_to": self._license_data.issued_to,
                "issued_at": self._license_data.issued_at,
                "expiry": self._license_data.expiry,
            }
            
            # Add expiry status if applicable
            if self._license_data.expiry:
                try:
                    expiry_date = datetime.fromisoformat(self._license_data.expiry.replace('Z', '+00:00'))
                    days_remaining = (expiry_date - datetime.now()).days
                    info["days_remaining"] = max(0, days_remaining)
                except (ValueError, AttributeError):
                    info["days_remaining"] = 0
            
            return info
        else:
            return {
                "status": "free",
                "edition": "free",
                "license_key": None,
                "issued_to": None,
                "issued_at": None,
                "expiry": None,
            }
    
    def has_premium(self) -> bool:
        """Check if user has premium license"""
        return self.license_type == LicenseType.PREMIUM
    
    def can_access_feature(self, required_license: LicenseType) -> bool:
        """Check if current license allows access to a feature"""
        if required_license == LicenseType.FREE:
            return True
        return self.has_premium()
    
    def show_premium_prompt(self, feature_name: str, console=None) -> bool:
        """Show upgrade prompt for premium features - delegates to UI layer."""
        from .license_ui import LicenseUI
        return LicenseUI.show_premium_prompt(feature_name, console)
    
    def validate_license_on_access(self) -> bool:
        """Validate license when accessing features. Shows warnings if needed."""
        if not self._license_data:
            return True  # Free license is always valid
            
        # Check if license is still valid
        if not self._license_data.is_valid():
            # License became invalid, reset to free
            self._license_data = None
            self.license_type = LicenseType.FREE
            return False
            
        # Check for expiry warnings
        info = self.get_license_info()
        if info['status'] == 'active' and info.get('days_remaining') is not None:
            days_remaining = info['days_remaining']
            if days_remaining <= 30:  # Show warnings for licenses expiring within 30 days
                from .license_ui import LicenseUI
                LicenseUI.show_expiry_warning(days_remaining)
                
        return True
    
    def get_context(self, additional_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get license context for feature evaluation"""
        import os
        
        # Validate license when getting context
        self.validate_license_on_access()
        
        context = {
            "license": self.license_type.value,
            "openai_api_available": bool(os.getenv('OPENAI_API_KEY'))
        }
        
        if additional_context:
            context.update(additional_context)
            
        return context


# Global license manager instance
license_manager = LicenseManager()