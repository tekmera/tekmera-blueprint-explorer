# License Generation Guide

This guide explains how to generate license files for Tekmera Fusion Explorer's premium licensing system.

## Overview

The license generation system creates JSON-formatted license files that can be activated using the `tekmera license activate` command. These licenses enable premium features in Tekmera Fusion Explorer.

## Prerequisites

Before generating licenses, you must first create RSA key pairs for digital signatures:

```bash
# Generate RSA key pair (required before first license generation)
python3 scripts/generate_keys.py
```

This creates:
- `license_private_key.pem` - Private key for signing licenses (keep secure!)
- `license_public_key.pem` - Public key for verification (embedded in application)

⚠️  **SECURITY WARNING**: Keep the private key secure and never commit it to version control.

## License Generator Script

The license generator is located at `scripts/generate_license.py` and provides two main commands:

### 1. Generate Standard License

```bash
python3 scripts/generate_license.py generate [OPTIONS]
```

**Options:**
- `--edition`: License edition (default: `pro`, options: `pro`, `enterprise`)
- `--issued-to`: **Required** - Name or organization the license is issued to
- `--days`: Number of days until expiry (default: `365`, use `0` for never expires)
- `--output`, `-o`: Output file path (default: `license.json`)
- `--private-key`: Private key file for signing (default: `license_private_key.pem`)

**Examples:**

```bash
# Generate a 1-year Pro license
python3 scripts/generate_license.py generate --issued-to "Acme Corporation" --days 365

# Generate a never-expiring license
python3 scripts/generate_license.py generate --issued-to "John Doe" --days 0 --output permanent_license.json

# Generate a 90-day trial license
python3 scripts/generate_license.py generate --issued-to "Trial User" --days 90 --output trial.json
```

### 2. Generate Trial License

```bash
python3 scripts/generate_license.py trial [OPTIONS]
```

**Options:**
- `--name`: **Required** - Customer name
- `--email`: Customer email (optional)
- `--company`: Company name (optional)
- `--trial-days`: Trial period in days (default: `30`)
- `--output`, `-o`: Output file path (auto-generated if not specified)
- `--private-key`: Private key file for signing (default: `license_private_key.pem`)

**Examples:**

```bash
# Generate a 30-day trial
python3 scripts/generate_license.py trial --name "Jane Smith" --email "jane@example.com" --company "Tech Corp"

# Generate a 14-day trial
python3 scripts/generate_license.py trial --name "Bob Johnson" --trial-days 14

# Generate trial with custom output file
python3 scripts/generate_license.py trial --name "Alice Brown" --output custom_trial.json
```

## License File Format

Generated license files follow this JSON structure:

```json
{
  "license_key": "12345678-ABCD-EFGH-IJKL-123456789012",
  "edition": "pro",
  "issued_to": "Customer Name <email@example.com> (Company Name)",
  "issued_at": "2025-10-10T13:44:32.166874",
  "expiry": "2026-10-10T13:44:32.166874",
  "signature": "dGhpcyBpcyBhIGJhc2U2NCBlbmNvZGVkIGRpZ2l0YWwgc2lnbmF0dXJl..."
}
```

**Fields:**
- `license_key`: Unique UUID identifier for the license
- `edition`: License edition (`pro` or `enterprise`)
- `issued_to`: Customer identification string
- `issued_at`: ISO 8601 timestamp when license was issued
- `expiry`: ISO 8601 expiry timestamp (null for permanent licenses)
- `signature`: Base64-encoded RSA-PSS digital signature for tamper detection

## License Distribution Workflow

### For Customer Sales

1. **Generate RSA Keys (one-time setup):**
   ```bash
   python3 scripts/generate_keys.py
   ```

2. **Generate Customer License:**
   ```bash
   python3 scripts/generate_license.py generate \
     --issued-to "Customer Name <email@example.com> (Company)" \
     --days 365 \
     --output customer_license.json
   ```

3. **Send to Customer:** Provide the generated JSON file to the customer

4. **Customer Activation:**
   ```bash
   tekmera license activate --file customer_license.json
   ```

### For Trial Users

1. **Generate Trial License:**
   ```bash
   python3 scripts/generate_license.py trial \
     --name "Trial User" \
     --email "trial@example.com" \
     --trial-days 30
   ```

2. **Send Trial File:** Provide the generated trial license file

3. **Trial Activation:**
   ```bash
   tekmera license activate --file trial_license.json
   ```

## License Management Commands

### Check License Status
```bash
tekmera license status
```

### Activate License
```bash
tekmera license activate --file license.json
```

### Deactivate License
```bash
tekmera license deactivate
```

## Premium Features Enabled

When a valid license is activated, these premium features become available:

### Core Premium Features
- **🎥 Live Scenario Walkthrough** - Interactive step-by-step execution flow
- **📝 AI Business Process Description** - OpenAI-powered business process analysis
- **🔎 Search across all blueprints** - Advanced cross-blueprint search capabilities

### Premium Governance Checks
- **GOV-COMP-001: Flow Complexity Index** - Algorithmic complexity analysis
- **GOV-SIZE-001: Functional Density Index** - Module clustering analysis  
- **GOV-COMP-002: Router Density Analysis** - Branching logic patterns
- **GOV-COMP-003: Route Fan-Out Profile** - Complex router detection
- **GOV-COMP-004: Flow Depth Estimate** - Execution path depth analysis
- **GOV-FIELD-003: Field Mapping Complexity** - Deep field reference analysis

## License File Security

### Current Implementation
- **Digital Signatures**: RSA-PSS signatures with SHA-256 for tamper detection
- **UUID4 License Keys**: Cryptographically secure license identifiers
- **Public Key Embedding**: Public key embedded in application for verification
- **Local File Storage**: Licenses stored in `~/.tekmera/license.json`

### Security Features
- **Tamper Detection**: Any modification to license data invalidates the signature
- **Signature Verification**: All license fields (except signature) are verified
- **Canonical JSON**: Consistent JSON serialization for reliable signature verification
- **Secure Private Key Storage**: Private keys are protected with 0600 permissions

### Security Considerations
- **Private Key Protection**: Keep `license_private_key.pem` secure and off version control
- **Key Rotation**: If private key is compromised, generate new keys and re-sign all licenses
- **Trust Model**: Public key is embedded in application - secure distribution is critical
- **Offline Verification**: No network required for license validation

### Future Enhancements
- Hardware security module (HSM) integration for production environments
- Server-based license validation for real-time revocation
- License transfer and migration support

## Troubleshooting

### License Generation Issues

**Problem:** "Private key file not found"
- **Solution:** Run `python3 scripts/generate_keys.py` first to generate key pair

**Problem:** "Failed to sign license"
- **Solution:** Check private key file permissions and format

### License Activation Issues

**Problem:** "Invalid license file format"
- **Solution:** Ensure JSON is valid and contains required fields

**Problem:** "License signature verification failed"
- **Solution:** License may be tampered with or generated with wrong key - regenerate license

**Problem:** "License expired" 
- **Solution:** Generate new license with extended expiry date

**Problem:** "Permission denied writing license file"
- **Solution:** Check write permissions to `~/.tekmera/` directory

### Generate New License

If a license is lost or corrupted:

```bash
# Generate replacement license
python3 scripts/generate_license.py generate \
  --issued-to "Original Customer Name" \
  --days 365 \
  --output replacement_license.json
```

## Integration with CI/CD

For automated testing or development:

```bash
# Generate test license in CI pipeline
python3 scripts/generate_license.py generate \
  --issued-to "CI Test Environment" \
  --days 1 \
  --output ci_test_license.json

# Activate for tests
tekmera license activate --file ci_test_license.json
```

## License Analytics

Track license usage by monitoring:
- License activation dates from `issued_at` field
- Expiry warnings from license status
- Feature usage patterns (future enhancement)

## Support

For license generation issues:
1. Check Python environment and dependencies
2. Verify script permissions (`chmod +x scripts/generate_license.py`)
3. Review generated JSON format for validity
4. Test activation with `tekmera license activate`

## Example Complete Workflow

```bash
# 1. Generate RSA keys (one-time setup)
python3 scripts/generate_keys.py

# 2. Generate customer license with digital signature
python3 scripts/generate_license.py generate \
  --issued-to "Acme Corp <admin@acme.com>" \
  --days 365 \
  --output acme_corp_license.json

# 3. Verify license file (should show signature field)
cat acme_corp_license.json

# 4. Test activation (signature will be verified)
tekmera license activate --file acme_corp_license.json

# 5. Verify status (should show "Digital Signature: ✅ Verified")
tekmera license status

# 6. Test premium features
tekmera analyze ./blueprints
# Navigate to premium features and confirm [Pro] labels are gone
```