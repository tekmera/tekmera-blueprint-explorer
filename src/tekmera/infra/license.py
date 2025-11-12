"""
License management for Tekmera Fusion Explorer with simple licensing framework
"""

import hashlib
import json
import os
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict


class LicenseType(Enum):
    FREE = "free"
    PREMIUM = "premium"


class SimpleLicenseManager:
    """Simple license manager without external dependencies"""

    def __init__(self):
        self.license_dir = Path.home() / ".tekmera"
        self.license_file = self.license_dir / "license.json"
        self._ensure_license_dir()

    def _ensure_license_dir(self):
        """Ensure license directory exists"""
        self.license_dir.mkdir(exist_ok=True)

    def _generate_machine_fingerprint(self) -> str:
        """Generate a simple machine fingerprint"""
        import platform
        import socket

        try:
            hostname = socket.gethostname()
            system = platform.system()
            machine = platform.machine()
            fingerprint = f"{hostname}-{system}-{machine}"
            return hashlib.md5(fingerprint.encode()).hexdigest()[:16]
        except Exception:
            # Fallback to a random ID stored in license dir
            fingerprint_file = self.license_dir / ".machine_id"
            if fingerprint_file.exists():
                return fingerprint_file.read_text().strip()
            else:
                machine_id = str(uuid.uuid4())[:16]
                fingerprint_file.write_text(machine_id)
                return machine_id

    def _validate_license_key(self, license_key: str) -> tuple[bool, str, Dict[str, Any]]:
        """Validate a license key format and extract data"""
        try:
            # Simple format: TEKMERA-PRO-{edition}-{hash}
            if not license_key.startswith("TEKMERA-PRO-"):
                return False, "Invalid license key format", {}

            parts = license_key.split("-")
            if len(parts) < 4:
                return False, "Invalid license key format", {}

            edition = parts[2]
            # key_hash = "-".join(parts[3:])  # Reserved for future validation

            # For now, accept any properly formatted key
            # In production, you'd validate against a signing secret
            license_data = {
                "edition": edition.lower(),
                "status": "active",
                "issued_at": datetime.now().isoformat(),
                "machine_fingerprint": self._generate_machine_fingerprint(),
            }

            return True, "License key is valid", license_data

        except Exception as e:
            return False, f"License validation error: {str(e)}", {}

    def activate_license_key(self, license_key: str) -> tuple[bool, str]:
        """Activate a license key"""
        try:
            success, message, license_data = self._validate_license_key(license_key)

            if not success:
                return False, message

            # Store license data
            license_data.update(
                {
                    "license_key": license_key,
                    "activated_at": datetime.now().isoformat(),
                    "instance_id": str(uuid.uuid4())[:8],
                }
            )

            self.license_file.write_text(json.dumps(license_data, indent=2))

            return (
                True,
                f"License activated successfully!\n\nEdition: {license_data['edition']}\nInstance ID: {license_data['instance_id']}",
            )

        except Exception as e:
            return False, f"Failed to activate license: {str(e)}"

    def deactivate_license(self) -> tuple[bool, str]:
        """Deactivate current license"""
        try:
            if self.license_file.exists():
                self.license_file.unlink()
            return True, "License deactivated successfully"
        except Exception as e:
            return False, f"Failed to deactivate license: {str(e)}"

    def get_license_info(self) -> Dict[str, Any]:
        """Get current license information"""
        # Check for local pro mode environment variable
        if os.getenv("TEKMERA_LOCAL_PRO", "").lower() in ["true", "1", "yes", "on"]:
            return {
                "status": "active",
                "edition": "pro",
                "license_key": "local-dev-mode",
                "instance_id": "local",
                "local_mode": True,
                "issued_to": "Local Development",
                "issued_at": datetime.now().isoformat(),
                "expiry": None,
            }

        # Check for license file
        if not self.license_file.exists():
            return {
                "status": "free",
                "edition": "free",
                "license_key": None,
                "instance_id": None,
                "local_mode": False,
                "issued_to": None,
                "issued_at": None,
                "expiry": None,
            }

        try:
            license_data = json.loads(self.license_file.read_text())

            # Validate machine fingerprint
            current_fingerprint = self._generate_machine_fingerprint()
            stored_fingerprint = license_data.get("machine_fingerprint", "")

            if current_fingerprint != stored_fingerprint:
                return {
                    "status": "invalid",
                    "edition": "free",
                    "license_key": None,
                    "instance_id": None,
                    "error": "License tied to different machine",
                }

            # Check if expired (if expiry is set)
            expiry = license_data.get("expiry")
            if expiry:
                try:
                    expiry_date = datetime.fromisoformat(expiry)
                    if datetime.now() >= expiry_date:
                        return {
                            "status": "expired",
                            "edition": "free",
                            "license_key": license_data.get("license_key"),
                            "expiry": expiry,
                        }
                except ValueError:
                    pass

            return {
                "status": license_data.get("status", "active"),
                "edition": license_data.get("edition", "pro"),
                "license_key": license_data.get("license_key"),
                "instance_id": license_data.get("instance_id"),
                "local_mode": False,
                "issued_to": license_data.get("issued_to", ""),
                "issued_at": license_data.get("issued_at", ""),
                "expiry": license_data.get("expiry"),
            }

        except Exception as e:
            return {
                "status": "error",
                "edition": "free",
                "error": f"Failed to read license: {str(e)}",
            }


class LicenseManager:
    """Main license manager for Tekmera Fusion Explorer"""

    def __init__(self, license_type: LicenseType = LicenseType.FREE):
        self.license_type = license_type
        self._simple_manager = SimpleLicenseManager()

        # Auto-detect license status from environment and files
        self._update_license_status()

    def _update_license_status(self):
        """Update license status based on current state"""
        info = self._simple_manager.get_license_info()

        if info["status"] == "active" and info["edition"] in ["pro", "premium"]:
            self.license_type = LicenseType.PREMIUM
        else:
            self.license_type = LicenseType.FREE

    def activate_license_key(self, license_key: str) -> tuple[bool, str]:
        """Activate a license key"""
        success, message = self._simple_manager.activate_license_key(license_key)
        if success:
            self._update_license_status()
        return success, message

    def deactivate_license(self) -> tuple[bool, str]:
        """Deactivate current license"""
        success, message = self._simple_manager.deactivate_license()
        if success:
            self._update_license_status()
        return success, message

    def get_license_info(self) -> Dict[str, Any]:
        """Get current license information"""
        return self._simple_manager.get_license_info()

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
        """Validate license when accessing features (simplified)"""
        self._update_license_status()
        info = self.get_license_info()

        # Show warnings for invalid/expired licenses
        if info["status"] in ["invalid", "expired", "error"] and info.get("license_key"):
            if console := getattr(self, "console", None):
                if info["status"] == "expired":
                    console.print(f"⚠️  [yellow]License has expired[/yellow]")
                elif info["status"] == "invalid":
                    console.print(
                        f"⚠️  [yellow]License invalid: {info.get('error', 'Unknown error')}[/yellow]"
                    )
                else:
                    console.print(
                        f"⚠️  [yellow]License error: {info.get('error', 'Unknown error')}[/yellow]"
                    )

        return info["status"] == "active"

    def get_context(self, additional_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get license context for feature evaluation"""
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
