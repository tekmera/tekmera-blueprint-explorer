"""
Lemon Squeezy License API integration for Tekmera Fusion Explorer
"""
import json
import requests
import os
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class LemonSqueezyConfig:
    """Configuration for Lemon Squeezy API"""
    base_url: str = "https://api.lemonsqueezy.com"
    rate_limit_per_minute: int = 60
    timeout_seconds: int = 30


class LemonSqueezyError(Exception):
    """Custom exception for Lemon Squeezy API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, error_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_data = error_data


class LemonSqueezyAPI:
    """Interface to Lemon Squeezy License API"""
    
    def __init__(self, config: Optional[LemonSqueezyConfig] = None):
        self.config = config or LemonSqueezyConfig()
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "Tekmera-Fusion-Explorer/1.0"
        })
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to Lemon Squeezy API"""
        url = f"{self.config.base_url}{endpoint}"
        
        headers = {}
        if method == "POST":
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                data=data if method == "POST" else None,
                params=data if method == "GET" else None,
                headers=headers,
                timeout=self.config.timeout_seconds
            )
            
            if response.status_code >= 400:
                error_data = {}
                try:
                    error_data = response.json()
                except json.JSONDecodeError:
                    pass
                
                error_message = error_data.get("error", f"HTTP {response.status_code}")
                raise LemonSqueezyError(
                    message=error_message,
                    status_code=response.status_code,
                    error_data=error_data
                )
            
            return response.json()
            
        except requests.RequestException as e:
            raise LemonSqueezyError(f"Network error: {str(e)}")
    
    def activate_license(self, license_key: str, instance_name: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Activate a license key with Lemon Squeezy
        
        Args:
            license_key: The license key to activate
            instance_name: Optional instance name for activation
            
        Returns:
            Tuple of (success, response_data)
        """
        data = {"license_key": license_key}
        if instance_name:
            data["instance_name"] = instance_name
        
        try:
            response = self._make_request("POST", "/v1/licenses/activate", data)
            return True, response
        except LemonSqueezyError as e:
            return False, {"error": str(e), "status_code": e.status_code}
    
    def validate_license(self, license_key: str, instance_id: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate a license key with Lemon Squeezy
        
        Args:
            license_key: The license key to validate
            instance_id: Optional instance ID for validation
            
        Returns:
            Tuple of (success, response_data)
        """
        data = {"license_key": license_key}
        if instance_id:
            data["instance_id"] = instance_id
        
        try:
            response = self._make_request("POST", "/v1/licenses/validate", data)
            return True, response
        except LemonSqueezyError as e:
            return False, {"error": str(e), "status_code": e.status_code}
    
    def deactivate_license(self, license_key: str, instance_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Deactivate a license key instance with Lemon Squeezy
        
        Args:
            license_key: The license key to deactivate
            instance_id: The instance ID to deactivate
            
        Returns:
            Tuple of (success, response_data)
        """
        data = {
            "license_key": license_key,
            "instance_id": instance_id
        }
        
        try:
            response = self._make_request("POST", "/v1/licenses/deactivate", data)
            return True, response
        except LemonSqueezyError as e:
            return False, {"error": str(e), "status_code": e.status_code}


class LemonSqueezyLicenseManager:
    """Enhanced license manager with Lemon Squeezy integration"""
    
    def __init__(self, api: Optional[LemonSqueezyAPI] = None):
        self.api = api or LemonSqueezyAPI()
        self.instance_name = self._generate_instance_name()
    
    def _generate_instance_name(self) -> str:
        """Generate a unique instance name for this installation"""
        import platform
        import socket
        
        try:
            hostname = socket.gethostname()
            system = platform.system()
            return f"tekmera-{system.lower()}-{hostname}"[:50]
        except Exception:
            return f"tekmera-unknown-{datetime.now().strftime('%Y%m%d')}"
    
    def activate_online(self, license_key: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Activate license online with Lemon Squeezy
        
        Returns:
            Tuple of (success, message, license_data)
        """
        success, response = self.api.activate_license(license_key, self.instance_name)
        
        if not success:
            error = response.get("error", "Unknown error")
            return False, f"Activation failed: {error}", None
        
        # Extract license information from response
        license_data = {
            "license_key": license_key,
            "edition": "pro",  # Assume pro for Lemon Squeezy licenses
            "issued_to": response.get("meta", {}).get("customer_email", ""),
            "issued_at": datetime.now().isoformat(),
            "instance_id": response.get("instance", {}).get("id"),
            "lemon_squeezy_activated": True
        }
        
        # Check if license has expiry
        if "expires_at" in response.get("license_key", {}):
            license_data["expiry"] = response["license_key"]["expires_at"]
        
        return True, "License activated successfully with Lemon Squeezy", license_data
    
    def validate_online(self, license_key: str, instance_id: Optional[str] = None) -> Tuple[bool, str]:
        """
        Validate license online with Lemon Squeezy
        
        Returns:
            Tuple of (success, message)
        """
        success, response = self.api.validate_license(license_key, instance_id)
        
        if not success:
            error = response.get("error", "Unknown error")
            return False, f"Validation failed: {error}"
        
        license_status = response.get("license_key", {}).get("status")
        
        if license_status == "active":
            return True, "License is valid and active"
        elif license_status == "expired":
            return False, "License has expired"
        elif license_status == "disabled":
            return False, "License has been disabled"
        else:
            return False, f"License status: {license_status}"
    
    def deactivate_online(self, license_key: str, instance_id: str) -> Tuple[bool, str]:
        """
        Deactivate license online with Lemon Squeezy
        
        Returns:
            Tuple of (success, message)
        """
        success, response = self.api.deactivate_license(license_key, instance_id)
        
        if not success:
            error = response.get("error", "Unknown error")
            return False, f"Deactivation failed: {error}"
        
        return True, "License deactivated successfully"
    
    def is_online_validation_available(self) -> bool:
        """Check if online validation is available (internet connection)"""
        try:
            response = requests.get("https://api.lemonsqueezy.com", timeout=5)
            return response.status_code != 500  # Any response means we can reach the API
        except requests.RequestException:
            return False