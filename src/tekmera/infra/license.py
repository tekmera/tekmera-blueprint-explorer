"""
License management for Tekmera Fusion Explorer with simple licensing framework
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
import uuid
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Tuple


class LicenseType(Enum):
    FREE = "free"
    EVALUATION = "evaluation"
    PREMIUM = "premium"


class SimpleLicenseManager:
    """Simple license manager without external dependencies"""

    def __init__(self):
        self.license_dir = Path.home() / ".tekmera"
        self.license_file = self.license_dir / "license.json"
        self._ensure_license_dir()

        # Signing secret - in production, this should be securely managed
        # For now, we'll use a fixed secret. In production, use env var or secure key management
        self._signing_secret = self._get_or_create_signing_secret()

    def _get_or_create_signing_secret(self) -> str:
        """Get or create signing secret for license validation"""
        # In production, this should come from environment variable or secure key store
        # For now, we'll use a application-specific secret
        secret_file = self.license_dir / ".signing_secret"

        if secret_file.exists():
            return secret_file.read_text().strip()
        else:
            # Generate a new secret key
            secret = base64.b64encode(secrets.token_bytes(32)).decode("ascii")
            secret_file.write_text(secret)
            secret_file.chmod(0o600)  # Make it readable only by owner
            return secret

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

    def _convert_timestamp_to_iso(self, timestamp) -> str:
        """Convert timestamp to ISO format, handling various input types"""
        if timestamp is None:
            return datetime.now().isoformat()

        # If already a string (ISO format), return as-is
        if isinstance(timestamp, str):
            return timestamp

        # If timestamp (float/int), convert to ISO
        try:
            return datetime.fromtimestamp(float(timestamp)).isoformat()
        except (ValueError, TypeError):
            return datetime.now().isoformat()

    def _generate_license_payload(
        self, license_type: str, duration_days: int = None
    ) -> Dict[str, Any]:
        """Generate compact license payload data"""
        # Use compact field names and minimal data
        # Don't include machine fingerprint in generation - will be added during activation
        payload = {
            "t": license_type,  # type
            "i": datetime.now().timestamp(),  # issued timestamp (shorter than ISO)
            "v": 2,  # version (integer instead of string)
        }

        if license_type == "evaluation" and duration_days:
            payload["x"] = (
                datetime.now() + timedelta(days=duration_days)
            ).timestamp()  # expiry timestamp
            payload["d"] = duration_days  # days

        return payload

    def _sign_license_payload(self, payload: Dict[str, Any]) -> str:
        """Create compact HMAC signature for license payload"""
        # Create canonical string from payload (excluding signature)
        canonical_data = json.dumps(payload, sort_keys=True, separators=(",", ":"))

        # Generate HMAC signature and truncate to 16 chars (64 bits security)
        signature = hmac.new(
            self._signing_secret.encode("utf-8"), canonical_data.encode("utf-8"), hashlib.sha256
        ).hexdigest()[
            :16
        ]  # Truncate for shorter keys

        return signature

    def _encode_license_key(self, payload: Dict[str, Any], signature: str) -> str:
        """Encode license payload and signature into compact opaque license key"""
        # Combine payload and signature with compact structure
        license_data = {"p": payload, "s": signature}  # payload -> p  # signature -> s

        # Convert to compact JSON and base64 encode for opacity
        json_data = json.dumps(license_data, separators=(",", ":"))
        encoded_data = base64.b64encode(json_data.encode("utf-8")).decode("ascii")

        # Create final license key with prefix
        license_key = f"TEKMERA-{encoded_data}"

        return license_key

    def _decode_license_key(self, license_key: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Decode and validate license key"""
        try:
            # Check prefix
            if not license_key.startswith("TEKMERA-"):
                return False, "Invalid license key format", {}

            # Extract encoded data
            encoded_data = license_key[8:]  # Remove "TEKMERA-" prefix

            # Base64 decode
            try:
                json_data = base64.b64decode(encoded_data.encode("ascii")).decode("utf-8")
                license_data = json.loads(json_data)
            except (ValueError, json.JSONDecodeError) as e:
                return False, f"Invalid license key encoding: {str(e)}", {}

            # Extract payload and signature (handle both compact and legacy formats)
            payload = license_data.get("p", license_data.get("payload", {}))
            provided_signature = license_data.get("s", license_data.get("signature", ""))

            # Verify signature
            expected_signature = self._sign_license_payload(payload)

            if not hmac.compare_digest(provided_signature, expected_signature):
                return False, "License signature verification failed", {}

            # Check license format version (handle both compact and legacy)
            version = payload.get("v", payload.get("version", "1.0"))
            if str(version) not in ["2.0", "2"]:
                return False, f"Unsupported license format version: {version}", {}

            # Machine fingerprint verification is now done during activation, not here
            # This allows licenses to be generated without being tied to a specific machine

            return True, "License key is valid", payload

        except Exception as e:
            return False, f"License validation error: {str(e)}", {}

    def _validate_license_key(self, license_key: str) -> tuple[bool, str, Dict[str, Any]]:
        """Validate a cryptographically signed license key"""
        # Use the new cryptographic validation
        success, message, payload = self._decode_license_key(license_key)

        if not success:
            return False, message, {}

        # Convert compact payload to expected license_data format
        license_type = payload.get("t", payload.get("license_type", "premium"))
        license_data = {
            "license_type": license_type,
            "status": "active",
            "issued_at": self._convert_timestamp_to_iso(payload.get("i", payload.get("issued_at"))),
            "machine_fingerprint": payload.get("m", payload.get("machine_fingerprint", "")),
            "expiry": (
                self._convert_timestamp_to_iso(payload.get("x"))
                if payload.get("x")
                else payload.get("expiry")
            ),
            "evaluation_days": payload.get("d", payload.get("evaluation_days")),
            "is_evaluation": license_type == "evaluation",
            "license_id": payload.get("lid", payload.get("license_id")),
            "version": str(payload.get("v", payload.get("version", "2.0"))),
        }

        return True, message, license_data

    def activate_license_key(self, license_key: str) -> tuple[bool, str]:
        """Activate a license key"""
        try:
            success, message, license_data = self._validate_license_key(license_key)

            if not success:
                return False, message

            # Store license data and bind to current machine
            license_data.update(
                {
                    "license_key": license_key,
                    "activated_at": datetime.now().isoformat(),
                    "instance_id": str(uuid.uuid4())[:8],
                    "machine_fingerprint": self._generate_machine_fingerprint(),
                }
            )

            self.license_file.write_text(json.dumps(license_data, indent=2))

            license_type = (
                "Paid" if license_data["license_type"] in ["evaluation", "premium"] else "Free"
            )
            return (
                True,
                f"License activated successfully!\n\nType: {license_type}\nInstance ID: {license_data['instance_id']}",
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
                "license_type": "premium",
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
                "license_type": "free",
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
                    "license_type": "free",
                    "license_key": None,
                    "instance_id": None,
                    "error": "License tied to different machine",
                }

            # Check if expired and calculate remaining days (if expiry is set)
            expiry = license_data.get("expiry")
            days_remaining = None
            if expiry:
                try:
                    expiry_date = datetime.fromisoformat(expiry)
                    now = datetime.now()
                    if now >= expiry_date:
                        return {
                            "status": "expired",
                            "license_type": "free",
                            "license_key": license_data.get("license_key"),
                            "expiry": expiry,
                            "days_remaining": 0,
                            "is_evaluation": license_data.get("is_evaluation", False),
                        }
                    else:
                        # Calculate remaining days
                        time_remaining = expiry_date - now
                        days_remaining = time_remaining.days
                        if time_remaining.seconds > 0:
                            days_remaining += 1  # Round up partial days
                except ValueError:
                    pass

            return {
                "status": license_data.get("status", "active"),
                "license_type": license_data.get("license_type", "premium"),
                "license_key": license_data.get("license_key"),
                "instance_id": license_data.get("instance_id"),
                "local_mode": False,
                "issued_to": license_data.get("issued_to", ""),
                "issued_at": license_data.get("issued_at", ""),
                "expiry": license_data.get("expiry"),
                "days_remaining": days_remaining,
                "is_evaluation": license_data.get("is_evaluation", False),
                "evaluation_days": license_data.get("evaluation_days"),
            }

        except Exception as e:
            return {
                "status": "error",
                "license_type": "free",
                "error": f"Failed to read license: {str(e)}",
            }

    def generate_evaluation_license(self, days: int = 30) -> str:
        """Generate a cryptographically signed evaluation license key"""
        if days <= 0 or days > 365:
            raise ValueError("Evaluation period must be between 1 and 365 days")

        # Generate license payload
        payload = self._generate_license_payload("evaluation", duration_days=days)

        # Sign the payload
        signature = self._sign_license_payload(payload)

        # Encode into opaque license key
        return self._encode_license_key(payload, signature)

    def generate_premium_license(self) -> str:
        """Generate a cryptographically signed permanent premium license key"""
        # Generate license payload
        payload = self._generate_license_payload("premium")

        # Sign the payload
        signature = self._sign_license_payload(payload)

        # Encode into opaque license key
        return self._encode_license_key(payload, signature)


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

        if info["status"] == "active":
            if info.get("is_evaluation", False):
                self.license_type = LicenseType.EVALUATION
            elif info["license_type"] in ["premium", "evaluation"]:
                self.license_type = (
                    LicenseType.PREMIUM
                    if info["license_type"] == "premium"
                    else LicenseType.EVALUATION
                )
            else:
                self.license_type = LicenseType.FREE
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
        """Check if user has premium license (including evaluation)"""
        return self.license_type in [LicenseType.PREMIUM, LicenseType.EVALUATION]

    def has_evaluation(self) -> bool:
        """Check if user has evaluation license"""
        return self.license_type == LicenseType.EVALUATION

    def can_access_feature(self, required_license: LicenseType) -> bool:
        """Check if current license allows access to a feature"""
        if required_license == LicenseType.FREE:
            return True
        elif required_license == LicenseType.EVALUATION:
            return self.license_type in [LicenseType.EVALUATION, LicenseType.PREMIUM]
        elif required_license == LicenseType.PREMIUM:
            return self.has_premium()
        return False

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
                    if info.get("is_evaluation"):
                        console.print(f"⚠️  [yellow]Evaluation license has expired[/yellow]")
                    else:
                        console.print(f"⚠️  [yellow]License has expired[/yellow]")
                elif info["status"] == "invalid":
                    console.print(
                        f"⚠️  [yellow]License invalid: {info.get('error', 'Unknown error')}[/yellow]"
                    )
                else:
                    console.print(
                        f"⚠️  [yellow]License error: {info.get('error', 'Unknown error')}[/yellow]"
                    )

        # Show evaluation warnings based on days remaining
        if (
            info["status"] == "active"
            and info.get("is_evaluation")
            and info.get("days_remaining") is not None
        ):
            if console := getattr(self, "console", None):
                days = info["days_remaining"]
                if days <= 3:
                    console.print(
                        f"⚠️  [red]Evaluation license expires in {days} day{'s' if days != 1 else ''}![/red]"
                    )
                elif days <= 7:
                    console.print(f"⚠️  [yellow]Evaluation license expires in {days} days[/yellow]")

        return info["status"] == "active"

    def generate_evaluation_license(self, days: int = 30) -> str:
        """Generate a cryptographically signed evaluation license key"""
        return self._simple_manager.generate_evaluation_license(days)

    def generate_premium_license(self) -> str:
        """Generate a cryptographically signed permanent premium license key"""
        return self._simple_manager.generate_premium_license()

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
