"""
Cryptographic utilities for license signing and verification.
Provides secure digital signature functionality for license protection.
"""
import json
import base64
from typing import Dict, Any, Optional
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature


class LicenseCrypto:
    """Handles cryptographic operations for license signing and verification."""
    
    # Embedded public key for license verification
    # This is the public key corresponding to the private key used for signing
    PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2PDX1/f6ssz1GXjKJKIo
0ed9CP4ngtNWAaTEAxypJSofdJMvjHh1A7b93pzVXcvooPMlR06hZSYywer0UxEl
5YFLn3ria2qFLWL6n6cldUHUWeMhCKOCSuTL4m1IH0DcPH8EzGaXQ79k30BhfiXX
g1QQF6z78PVqGqQqp9HqZz81WOFDuzSLatlWyi+FZ9cBTkkGcMefGphYLX6bmcmu
XsKCjPdniFE9eAx29Jlutw0iEKBKJNGL0nRJGm81rEb8ffzhjd3L0yIE7LDvQBQw
ZimNfkGtAmTPbziEJGxJ3ucysyYGtRykz4HFUz1d5xinORFgE8fngvqQ7j3f7RzP
iQIDAQAB
-----END PUBLIC KEY-----"""
    
    @classmethod
    def load_public_key(cls):
        """Load the embedded public key for signature verification."""
        return serialization.load_pem_public_key(cls.PUBLIC_KEY_PEM.encode())
    
    @classmethod
    def load_private_key(cls, private_key_path: Path) -> rsa.RSAPrivateKey:
        """Load private key from file for signing."""
        with open(private_key_path, 'rb') as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None  # No password for simplicity
            )
        return private_key
    
    @classmethod
    def normalize_license_data(cls, license_data: Dict[str, Any]) -> bytes:
        """Normalize license data for consistent signing/verification."""
        # Remove signature field if present
        signing_data = {k: v for k, v in license_data.items() if k != 'signature'}
        
        # Create canonical JSON representation
        canonical_json = json.dumps(signing_data, sort_keys=True, separators=(',', ':'))
        return canonical_json.encode('utf-8')
    
    @classmethod
    def sign_license(cls, license_data: Dict[str, Any], private_key_path: Path) -> str:
        """Sign license data and return base64-encoded signature."""
        try:
            # Load private key
            private_key = cls.load_private_key(private_key_path)
            
            # Normalize data for signing
            data_to_sign = cls.normalize_license_data(license_data)
            
            # Create signature
            signature = private_key.sign(
                data_to_sign,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Return base64-encoded signature
            return base64.b64encode(signature).decode('ascii')
            
        except Exception as e:
            raise LicenseSigningError(f"Failed to sign license: {e}")
    
    @classmethod
    def verify_license_signature(cls, license_data: Dict[str, Any]) -> bool:
        """Verify the digital signature of a license."""
        try:
            # Extract signature
            signature_b64 = license_data.get('signature')
            if not signature_b64:
                return False
            
            # Decode signature
            try:
                signature = base64.b64decode(signature_b64.encode('ascii'))
            except Exception:
                return False
            
            # Load public key
            public_key = cls.load_public_key()
            
            # Normalize data for verification
            data_to_verify = cls.normalize_license_data(license_data)
            
            # Verify signature
            public_key.verify(
                signature,
                data_to_verify,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except InvalidSignature:
            return False
        except Exception:
            # Any other error means verification failed
            return False
    
    @classmethod
    def update_embedded_public_key(cls, public_key_path: Path):
        """Helper to update the embedded public key in this file.
        
        This is a development utility to update the PUBLIC_KEY_PEM constant.
        Run this after generating new keys to embed the public key.
        """
        with open(public_key_path, 'r') as f:
            public_key_pem = f.read()
        
        print("Update the PUBLIC_KEY_PEM constant in crypto_utils.py with:")
        print('PUBLIC_KEY_PEM = """' + public_key_pem + '"""')


class LicenseSigningError(Exception):
    """Exception raised when license signing fails."""
    pass


class LicenseVerificationError(Exception):
    """Exception raised when license verification fails."""
    pass


def embed_public_key_from_file(public_key_file: Path) -> str:
    """Utility function to get public key content for embedding."""
    with open(public_key_file, 'r') as f:
        return f.read().strip()


# Development utility
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'update-key':
        if len(sys.argv) < 3:
            print("Usage: python crypto_utils.py update-key <public_key_file>")
            sys.exit(1)
        
        public_key_path = Path(sys.argv[2])
        LicenseCrypto.update_embedded_public_key(public_key_path)
    else:
        print("License cryptographic utilities")
        print("Use 'python crypto_utils.py update-key <public_key_file>' to update embedded key")