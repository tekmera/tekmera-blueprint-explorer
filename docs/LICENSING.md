# Tekmera Fusion Explorer — Comprehensive Licensing Guide

This document covers both the business strategy and technical implementation of Tekmera's self-contained licensing system.

---

## Table of Contents

1. [Business Overview](#business-overview)
2. [License Types](#license-types)
3. [Security Architecture](#security-architecture)
4. [License Generation](#license-generation)
5. [License Activation](#license-activation)
6. [Technical Implementation](#technical-implementation)
7. [Sales Strategy](#sales-strategy)
8. [Administrative Tools](#administrative-tools)
9. [Troubleshooting](#troubleshooting)

---

## Business Overview

### Objective

Enable Tekmera to distribute and manage **paid licenses** for the Fusion Explorer CLI using a self-contained, offline-capable licensing system with evaluation license support.

### Licensing Model

Tekmera Fusion Explorer uses a simple two-tier licensing model:

- **Free:** Basic exploration and blueprint comparison
- **Paid:** Permanent or evaluation license with all features including AI analysis and cross-blueprint search

### Core Principles

1. **Offline operation:** Licenses work without internet connectivity
2. **Evaluation-first:** 30-day trials convert to permanent purchases
3. **Machine binding:** Licenses tied to activation machine for security
4. **Clear expiration:** Evaluation licenses automatically revert to Free tier
5. **Simple activation:** Single command license activation
6. **Cryptographic security:** HMAC-SHA256 signed licenses prevent tampering

---

## License Types

### Free License
- Always available, no key required
- Includes basic exploration and blueprint comparison
- Perfect for evaluation and basic use cases

### Evaluation License
- **Format**: `TEKMERA-{base64_encoded_signed_data}`
- **Example**: `TEKMERA-eyJwIjp7InQiOiJldmFsdWF0aW9uIiwiaSI6MTc2Mjk1OTMxMC4zNjA1NCwidiI6Mn0sInMiOiI1NjgzYWNkMDMxMzJkMzQ5In0=`
- **Duration**: 1-365 days (typically 30 days)
- **Features**: Full paid feature set during evaluation period
- **Expiration**: Automatic reversion to Free tier when expired

### Permanent Paid License
- **Format**: `TEKMERA-{base64_encoded_signed_data}`
- **Example**: `TEKMERA-eyJwIjp7InQiOiJwcmVtaXVtIiwiaSI6MTc2Mjk1OTMxMC4zNjA1NCwidiI6Mn0sInMiOiI1NjgzYWNkMDMxMzJkMzQ5In0=`
- **Duration**: Permanent (no expiration)
- **Features**: All paid features permanently

---

## Security Architecture

### Cryptographic Protection
- **HMAC-SHA256 Signatures**: All licenses are cryptographically signed to prevent tampering
- **Base64 Encoding**: License keys are opaque and cannot be easily modified
- **Machine Binding**: Licenses are tied to specific machines using hardware fingerprints
- **Version Control**: License format versioning prevents downgrade attacks

### Tamper Resistance
- **Signature Validation**: Any modification to license data invalidates the signature
- **Time-based Expiration**: Evaluation periods are cryptographically enforced
- **Machine Fingerprinting**: Prevents license sharing across different machines
- **Secure Key Storage**: Signing secrets are stored with restricted file permissions

### Validation Process

```
License Key Received
    ↓
Extract Base64 Data
    ↓
JSON Decode Payload + Signature
    ↓
Verify HMAC Signature
    ↓
Check Machine Fingerprint
    ↓
Validate Expiration (if applicable)
    ↓
Grant/Deny Access
```

### Security Features

1. **Tamper Detection**: Any modification invalidates the HMAC signature
2. **Replay Protection**: Machine fingerprint prevents cross-machine usage
3. **Time Integrity**: Evaluation periods cannot be extended without new license
4. **Format Versioning**: Prevents downgrade to less secure formats

---

## License Generation

### For Evaluation Licenses

```python
from tekmera.infra.license import license_manager

# Generate 30-day evaluation license
eval_key = license_manager.generate_evaluation_license(30)
print(f"30-day evaluation: {eval_key}")

# Generate custom duration (7-365 days)
trial_key = license_manager.generate_evaluation_license(7)
print(f"7-day trial: {trial_key}")
```

### For Permanent Paid Licenses

```python
from tekmera.infra.license import license_manager

# Generate permanent paid license
paid_key = license_manager.generate_premium_license()
print(f"Permanent paid license: {paid_key}")
```

### Using Generation Scripts

#### Generate Evaluation Licenses
```bash
# Basic usage
./scripts/generate-eval-license.py                    # 30-day default
./scripts/generate-eval-license.py 60                 # 60-day evaluation
./scripts/generate-eval-license.py 7                  # 7-day quick trial

# Bulk generation for campaigns
./scripts/generate-eval-license.py --bulk 10          # 10 licenses (30-day each)
./scripts/generate-eval-license.py --bulk 5 14        # 5 licenses (14-day each)

# Save to file
./scripts/generate-eval-license.py --bulk 20 --output campaign-licenses.txt

# Different formats
./scripts/generate-eval-license.py --format csv --output licenses.csv
./scripts/generate-eval-license.py --format json --output licenses.json
```

#### Generate Permanent Paid Licenses
```bash
# Basic usage  
./scripts/generate-pro-license.py              # Generate permanent paid license

# With customer information
./scripts/generate-pro-license.py --customer "Acme Corp" --order "ORD-12345"

# Bulk generation for teams
./scripts/generate-pro-license.py --bulk 5     # 5 paid licenses

# Save to file with metadata
./scripts/generate-pro-license.py --bulk 5 --customer "TechCorp" --format csv --output techcorp-licenses.csv
```

---

## License Activation

### CLI Commands

```bash
# Activate any license type (cryptographic format)
tekmera license activate TEKMERA-eyJwIjp7InQiOiJldmFsdWF0aW9uIiwiaSI6MTc2Mjk1OTMxMC4zNjA1NCwidiI6Mn0sInMiOiI1NjgzYWNkMDMxMzJkMzQ5In0=

# Check current license status
tekmera license status

# Deactivate current license
tekmera license deactivate
```

### License Status Information

The `tekmera license status` command shows:
- License type (Free or Paid)
- Cryptographic validation status
- Expiration date (for evaluation licenses)
- Days remaining (for evaluation licenses)
- Machine fingerprint for security
- License ID for tracking

### User Experience Flow

#### Evaluation Journey

1. **Discovery:** User downloads Tekmera with evaluation license
2. **Activation:** Simple one-command activation
3. **Exploration:** 30 days of full paid features
4. **Reminder:** Clear expiration warnings
5. **Conversion:** Seamless upgrade to permanent license

#### Purchase Experience

1. **Expired evaluation** or **direct purchase** triggers purchase flow
2. **Payment processing** through existing sales channels
3. **Immediate delivery** of permanent license key
4. **Simple activation** replaces evaluation license
5. **Permanent access** with no further expiration concerns

---

## Technical Implementation

### Core Components

1. **License Manager** (`license.py`)
   - Cryptographic license generation and validation
   - Machine fingerprint creation
   - Expiration checking and warnings

2. **License Storage** (`~/.tekmera/license.json`)
   - Local file storage
   - Machine-specific validation
   - Secure license metadata

3. **Feature Gating** (throughout codebase)
   - Runtime license checking
   - Graceful feature disabling
   - Clear upgrade prompts

### License File Format
```json
{
  "license_type": "premium",
  "status": "active", 
  "issued_at": "2025-11-12T10:55:10.360540",
  "expiry": null,
  "is_evaluation": false,
  "machine_fingerprint": "a1b2c3d4e5f6g7h8",
  "license_key": "TEKMERA-eyJwIjp7InQiOiJwcmVtaXVtIiwiaSI6MTc2Mjk1OTMxMC4zNjA1NCwidiI6Mn0sInMiOiI1NjgzYWNkMDMxMzJkMzQ5In0=",
  "instance_id": "2d23c967"
}
```

### File Structure

#### License Storage
- **Location**: `~/.tekmera/license.json`
- **Format**: JSON with license metadata
- **Security**: Machine fingerprint validation

#### Signing Secret Storage
- **Location**: `~/.tekmera/.signing_secret`
- **Permissions**: 600 (owner read/write only)
- **Format**: Base64-encoded 32-byte secret
- **Generation**: Automatic on first use

### Feature Gating

```python
from tekmera.infra.license import LicenseType

# Check if user can access paid features
if license_manager.can_access_feature(LicenseType.PREMIUM):
    # Enable AI features, cross-blueprint search, etc.
    pass
```

---

## Sales Strategy

### Distribution Channels

1. **Website Downloads**
   - Embedded 30-day evaluation in installer
   - Immediate paid feature access
   - Built-in conversion prompts

2. **Conference/Event Distribution**
   - Extended 60-day evaluations for qualified prospects
   - QR codes or business cards with license keys
   - Follow-up sequences for conversion

3. **Direct Sales**
   - Custom evaluation periods for enterprise prospects
   - Personalized demonstrations with evaluation licenses
   - Account-specific license generation

### Sales & Distribution Flow

1. **Evaluation Distribution**: Prospects receive 30-day evaluation licenses
2. **Evaluation Experience**: Users activate and explore full paid features for 30 days
3. **Purchase Conversion**: Users purchase permanent license through website or sales
4. **Permanent License Delivery**: Customers receive permanent license key via email
5. **Permanent Activation**: Simple one-command activation provides permanent access

### Conversion Optimization

1. **Expiration Warnings**
   - Clear upgrade prompts with purchase links
   - Remaining days countdown
   - Feature-specific upgrade messaging

### Evaluation Strategy
- **30-day standard:** Sufficient for thorough evaluation
- **60-day extended:** Enterprise prospects and conferences  
- **90-day custom:** Large enterprise sales cycles

---

## Administrative Tools

### License Generation Tools

```python
# Bulk license generation for campaigns
def generate_campaign_licenses(count: int, days: int = 30):
    licenses = []
    for i in range(count):
        key = license_manager.generate_evaluation_license(days)
        licenses.append(key)
    return licenses

# Extended evaluation for enterprise prospects  
enterprise_eval = license_manager.generate_evaluation_license(90)

# Permanent license fulfillment
customer_license = license_manager.generate_premium_license()
```

### Support Tools

1. **License Status Checking**
   - Validate customer license issues
   - Machine fingerprint mismatches
   - Expiration date verification

2. **License Replacement**
   - Generate replacement licenses for issues
   - Machine transfer assistance
   - License key regeneration

### Development Workflows

#### Testing License Types
```python
# Test evaluation license generation and validation
eval_key = license_manager.generate_evaluation_license(1)  # 1-day for testing
license_manager.activate_license_key(eval_key)

# Check license info
info = license_manager.get_license_info()
print(f"Type: {info['license_type']}")
print(f"Days remaining: {info['days_remaining']}")
print(f"Is evaluation: {info['is_evaluation']}")

# Test permanent license
paid_key = license_manager.generate_premium_license()
license_manager.activate_license_key(paid_key)
```

### License Inspection (for debugging)

```python
# Decode license key for inspection (requires signing secret)
success, message, payload = license_manager._simple_manager._decode_license_key(license_key)
if success:
    print(f"License Type: {payload['t']}")
    print(f"Issued: {payload['i']}")
    print(f"Expires: {payload.get('x', 'Never')}")
```

---

## Troubleshooting

### Common Issues

1. **License Signature Invalid**:
   - License has been modified or corrupted
   - Generate new license with current signing secret
   - Check for transmission errors (copy/paste issues)

2. **Machine Fingerprint Mismatch**:
   - License activated on different machine
   - Hardware configuration changed significantly
   - Generate new license for current machine

3. **License Expired**:
   - Evaluation period has ended
   - Generate new evaluation license for testing
   - Purchase permanent license for production use

4. **Signing Secret Missing**:
   - `.signing_secret` file deleted or corrupted
   - Will regenerate automatically but invalidates existing licenses
   - Backup signing secret for production deployments

### Debug Commands

```bash
# Detailed license information with security status
tekmera license status

# Test cryptographic validation
python -c "
from tekmera.infra.license import license_manager
info = license_manager.get_license_info()
print('Security Status:', info.get('version', 'Legacy'))
print('License ID:', info.get('license_id', 'None'))
print('Signature Valid:', info.get('status') == 'active')
"

# Check feature access
python -c "
from tekmera.infra.license import license_manager, LicenseType
print('Paid Access:', license_manager.can_access_feature(LicenseType.PREMIUM))
print('Evaluation Access:', license_manager.can_access_feature(LicenseType.EVALUATION))
"
```

---

## Implementation Status

### Technical Implementation ✅ Complete
- Self-contained license generation
- Evaluation license support with expiration
- Machine binding security
- Graceful feature degradation
- Clear expiration warnings
- Cryptographic license signing
- Tamper-proof license validation

### Business Process ⏳ In Progress
- Sales team license generation training
- Customer onboarding documentation
- Support team license troubleshooting guide
- Marketing campaign integration

---

## Summary

This self-contained licensing system provides:

- **Evaluation-driven sales:** 30-day trials convert to permanent purchases
- **Simple user experience:** One-command activation and clear upgrade paths
- **Technical reliability:** Offline operation with no external dependencies
- **Security compliance:** Cryptographically signed, machine-bound licenses prevent unauthorized sharing
- **Flexible distribution:** Multiple channels for evaluation license distribution
- **Clear business model:** Free → Paid conversion funnel
- **Tamper-Proof Licenses:** HMAC-SHA256 signatures prevent modification
- **Machine-Bound Security:** Hardware fingerprinting prevents license sharing
- **Privacy-Focused:** No external tracking or data collection
- **Simple Generation:** Easy license creation for sales and support

The approach balances user convenience, technical simplicity, and business effectiveness while maintaining strong cryptographic security and license compliance.