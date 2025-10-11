#!/usr/bin/env python3
"""
Test script for Lemon Squeezy license integration
"""
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tekmera.infra.lemon_squeezy import LemonSqueezyAPI, LemonSqueezyLicenseManager
from tekmera.infra.license import license_manager

def test_connectivity():
    """Test connection to Lemon Squeezy API"""
    print("🌐 Testing Lemon Squeezy API connectivity...")
    
    ls_manager = LemonSqueezyLicenseManager()
    is_online = ls_manager.is_online_validation_available()
    
    if is_online:
        print("✅ Lemon Squeezy API is reachable")
    else:
        print("❌ Lemon Squeezy API is not reachable (check internet connection)")
    
    return is_online

def test_license_key_activation():
    """Test license key activation (requires valid key)"""
    print("\n🔑 Testing license key activation...")
    
    # This would require a valid test license key
    test_key = os.getenv("TEST_LICENSE_KEY")
    
    if not test_key:
        print("⏭️  Skipping activation test (set TEST_LICENSE_KEY environment variable)")
        return
    
    success, message = license_manager.activate_license_key(test_key)
    
    if success:
        print(f"✅ Activation successful: {message}")
        
        # Test license info
        info = license_manager.get_license_info()
        print(f"📋 License info: {info}")
        
        # Test deactivation
        success, message = license_manager.deactivate_license()
        if success:
            print(f"✅ Deactivation successful: {message}")
        else:
            print(f"❌ Deactivation failed: {message}")
    else:
        print(f"❌ Activation failed: {message}")

def test_offline_functionality():
    """Test that offline functionality still works"""
    print("\n📴 Testing offline functionality...")
    
    # Test license context without network
    context = license_manager.get_context()
    print(f"✅ License context: {context}")
    
    # Test feature access check
    from tekmera.infra.license import LicenseType
    can_access_free = license_manager.can_access_feature(LicenseType.FREE)
    can_access_premium = license_manager.can_access_feature(LicenseType.PREMIUM)
    
    print(f"✅ Can access free features: {can_access_free}")
    print(f"📊 Can access premium features: {can_access_premium}")

def test_api_error_handling():
    """Test API error handling with invalid data"""
    print("\n🚫 Testing error handling...")
    
    api = LemonSqueezyAPI()
    
    # Test with invalid license key
    success, response = api.validate_license("invalid-key-123")
    
    if not success:
        print(f"✅ Error handling works: {response.get('error', 'Unknown error')}")
    else:
        print("❓ Unexpected success with invalid key")

def main():
    """Run all tests"""
    print("🧪 Lemon Squeezy Integration Test Suite\n")
    
    try:
        # Test basic connectivity
        is_online = test_connectivity()
        
        # Test offline functionality (always works)
        test_offline_functionality()
        
        if is_online:
            # Test error handling
            test_api_error_handling()
            
            # Test license key activation (if test key provided)
            test_license_key_activation()
        else:
            print("\n⚠️  Skipping online tests (no internet connection)")
        
        print("\n✅ Test suite completed")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())