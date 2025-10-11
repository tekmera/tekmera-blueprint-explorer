"""
License management for Tekmera Fusion Explorer with Lemon Squeezy integration
"""

import os
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from .lemon_squeezy import LemonSqueezyLicenseManager


class LicenseType(Enum):
    FREE = "free"
    PREMIUM = "premium"


class LicenseManager:
    """Manages license validation and feature gating with Lemon Squeezy"""

    def __init__(self, license_type: LicenseType = LicenseType.FREE):
        self.license_type = license_type
        self._license_key: Optional[str] = None
        self._license_data: Optional[Dict[str, Any]] = None
        self._instance_id: Optional[str] = None
        self._lemon_squeezy = LemonSqueezyLicenseManager()
        self._last_validation: Optional[datetime] = None

        # Check for license key in environment variable for persistence
        self._load_from_environment()

    def _load_from_environment(self) -> None:
        """Load license from environment variable if available"""
        license_key = os.getenv("TEKMERA_LICENSE_KEY")
        instance_id = os.getenv("TEKMERA_INSTANCE_ID")

        if license_key and instance_id:
            self._license_key = license_key
            self._instance_id = instance_id

            # Try to validate if online
            if self._lemon_squeezy.is_online_validation_available():
                success, message = self._lemon_squeezy.validate_online(license_key, instance_id)
                if success:
                    self.license_type = LicenseType.PREMIUM
                    self._license_data = {
                        "license_key": license_key,
                        "edition": "pro",
                        "status": "active",
                        "instance_id": instance_id,
                    }
                    self._last_validation = datetime.now()

    def activate_license_key(self, license_key: str) -> tuple[bool, str]:
        """Activate a license using a license key with Lemon Squeezy"""
        try:
            # Try online activation
            if not self._lemon_squeezy.is_online_validation_available():
                return False, "No internet connection available for license activation"

            success, message, license_data = self._lemon_squeezy.activate_online(license_key)

            if success and license_data:
                # Store license data in memory and environment
                self._license_key = license_key
                self._license_data = license_data
                self._instance_id = license_data.get("instance_id")
                self._last_validation = datetime.now()

                # Persist in environment variables (user can add to shell profile)
                os.environ["TEKMERA_LICENSE_KEY"] = license_key
                if self._instance_id:
                    os.environ["TEKMERA_INSTANCE_ID"] = self._instance_id

                # Update license type
                if license_data.get("edition", "").lower() in ["pro", "premium", "professional"]:
                    self.license_type = LicenseType.PREMIUM
                else:
                    self.license_type = LicenseType.FREE

                return (
                    True,
                    f"{message}\n\nTo persist this license, add these to your shell profile:\nexport TEKMERA_LICENSE_KEY={license_key}\nexport TEKMERA_INSTANCE_ID={self._instance_id}",
                )
            else:
                return False, message

        except Exception as e:
            return False, f"Failed to activate license key: {str(e)}"

    def deactivate_license(self) -> tuple[bool, str]:
        """Deactivate current license with Lemon Squeezy"""
        try:
            # Try to deactivate online
            if (
                self._license_key
                and self._instance_id
                and self._lemon_squeezy.is_online_validation_available()
            ):

                success, message = self._lemon_squeezy.deactivate_online(
                    self._license_key, self._instance_id
                )

                if not success:
                    return False, f"Failed to deactivate online: {message}"

            # Clear in-memory license data
            self._license_key = None
            self._license_data = None
            self._instance_id = None
            self._last_validation = None
            self.license_type = LicenseType.FREE

            # Clear environment variables
            if "TEKMERA_LICENSE_KEY" in os.environ:
                del os.environ["TEKMERA_LICENSE_KEY"]
            if "TEKMERA_INSTANCE_ID" in os.environ:
                del os.environ["TEKMERA_INSTANCE_ID"]

            return (
                True,
                "License deactivated successfully.\n\nRemove these from your shell profile:\nTEKMERA_LICENSE_KEY\nTEKMERA_INSTANCE_ID",
            )

        except Exception as e:
            return False, f"Failed to deactivate license: {str(e)}"

    def get_license_info(self) -> Dict[str, Any]:
        """Get current license information"""
        if self._license_data and self._is_license_valid():
            info = {
                "status": "active",
                "edition": self._license_data.get("edition", "pro"),
                "license_key": self._license_key,
                "issued_to": self._license_data.get("issued_to", ""),
                "issued_at": self._license_data.get("issued_at", ""),
                "expiry": self._license_data.get("expiry"),
                "instance_id": self._instance_id,
            }

            # Add expiry status if applicable
            expiry = self._license_data.get("expiry")
            if expiry:
                try:
                    expiry_date = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
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
                "instance_id": None,
            }

    def _is_license_valid(self) -> bool:
        """Check if current license data is valid"""
        if not self._license_data or not self._license_key:
            return False

        # Check expiry
        expiry = self._license_data.get("expiry")
        if expiry:
            try:
                expiry_date = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
                if datetime.now() >= expiry_date:
                    return False
            except (ValueError, AttributeError):
                return False

        # Check status
        status = self._license_data.get("status", "active")
        return status == "active"

    def has_premium(self) -> bool:
        """Check if user has premium license"""
        return self.license_type == LicenseType.PREMIUM

    def can_access_feature(self, required_license: LicenseType) -> bool:
        """Check if current license allows access to a feature"""
        if required_license == LicenseType.FREE:
            return True
        return self.has_premium()

    def show_premium_prompt(self, feature_name: str, console=None) -> bool:
        """Show upgrade prompt for premium features"""
        from .license_ui import LicenseUI

        return LicenseUI.show_premium_prompt(feature_name, console)

    def validate_license_on_access(self) -> bool:
        """Validate license when accessing features"""
        if not self._license_key or not self._instance_id:
            return True  # Free license is always valid

        # Check if we should validate online (hourly rate limiting)
        if self._should_validate_online():
            success, message = self._lemon_squeezy.validate_online(
                self._license_key, self._instance_id
            )

            if not success:
                print(f"Warning: License validation failed: {message}")
                if "expired" in message.lower() or "disabled" in message.lower():
                    self._license_key = None
                    self._license_data = None
                    self._instance_id = None
                    self.license_type = LicenseType.FREE
                    return False
            else:
                self._last_validation = datetime.now()

        # Check if license is still valid locally
        if not self._is_license_valid():
            self._license_key = None
            self._license_data = None
            self._instance_id = None
            self.license_type = LicenseType.FREE
            return False

        # Check for expiry warnings
        info = self.get_license_info()
        if info["status"] == "active" and info.get("days_remaining") is not None:
            days_remaining = info["days_remaining"]
            if days_remaining <= 30:  # Show warnings for licenses expiring within 30 days
                from .license_ui import LicenseUI

                LicenseUI.show_expiry_warning(days_remaining)

        return True

    def _should_validate_online(self) -> bool:
        """Determine if we should validate online (rate limiting)"""
        if not self._last_validation:
            return self._lemon_squeezy.is_online_validation_available()

        # Check if an hour has passed since last validation
        hours_since_validation = (datetime.now() - self._last_validation).total_seconds() / 3600

        return (
            hours_since_validation >= 1.0 and self._lemon_squeezy.is_online_validation_available()
        )

    def get_context(self, additional_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get license context for feature evaluation"""
        # Validate license when getting context
        self.validate_license_on_access()

        context = {
            "license": self.license_type.value,
            "openai_api_available": bool(os.getenv("OPENAI_API_KEY")),
        }

        if additional_context:
            context.update(additional_context)

        return context


# Global license manager instance
license_manager = LicenseManager()
