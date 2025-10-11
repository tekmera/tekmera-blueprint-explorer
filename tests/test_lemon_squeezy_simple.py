#!/usr/bin/env python3
"""
Simple test for Lemon Squeezy license integration
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_imports():
    """Test that all modules import correctly"""
    try:
        from tekmera.infra.lemon_squeezy import LemonSqueezyAPI, LemonSqueezyLicenseManager
        print("✅ lemon_squeezy module imports successfully")
        
        from tekmera.infra.license import license_manager, LicenseType
        print("✅ license module imports successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_license_manager():
    """Test license manager basic functionality"""
    try:
        from tekmera.infra.license import license_manager, LicenseType
        
        # Test getting license info (should work even without license)
        info = license_manager.get_license_info()
        print(f"✅ License info: {info['status']} edition")
        
        # Test feature access
        can_access_free = license_manager.can_access_feature(LicenseType.FREE)
        can_access_premium = license_manager.can_access_feature(LicenseType.PREMIUM)
        
        print(f"✅ Can access free features: {can_access_free}")
        print(f"📊 Can access premium features: {can_access_premium}")
        
        # Test context
        context = license_manager.get_context()
        print(f"✅ License context: {context}")
        
        return True
    except Exception as e:
        print(f"❌ License manager error: {e}")
        return False

def test_api_connectivity():
    """Test Lemon Squeezy API connectivity"""
    try:
        from tekmera.infra.lemon_squeezy import LemonSqueezyLicenseManager
        
        ls_manager = LemonSqueezyLicenseManager()
        is_online = ls_manager.is_online_validation_available()
        
        if is_online:
            print("✅ Lemon Squeezy API is reachable")
        else:
            print("⚠️  Lemon Squeezy API is not reachable (offline or network issue)")
        
        return True
    except Exception as e:
        print(f"❌ API connectivity error: {e}")
        return False

def main():
    """Run simple tests"""
    print("🧪 Lemon Squeezy Simple Test Suite\n")
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    print()
    
    # Test license manager
    if not test_license_manager():
        all_passed = False
    
    print()
    
    # Test API connectivity
    if not test_api_connectivity():
        all_passed = False
    
    print()
    
    if all_passed:
        print("✅ All tests passed! Lemon Squeezy integration is ready.")
        print("\nTo activate a license:")
        print("  tekmera license activate YOUR-LICENSE-KEY")
    else:
        print("❌ Some tests failed.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())