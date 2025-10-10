# License Generation Guide

This guide explains how to generate license files for Tekmera Fusion Explorer's premium licensing system.

## Overview

The license generation system creates JSON-formatted license files that can be activated using the `tekmera license activate` command. These licenses enable premium features in Tekmera Fusion Explorer.

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
  "expiry": "2026-10-10T13:44:32.166874"
}
```

**Fields:**
- `license_key`: Unique UUID identifier for the license
- `edition`: License edition (`pro` or `enterprise`)
- `issued_to`: Customer identification string
- `issued_at`: ISO 8601 timestamp when license was issued
- `expiry`: ISO 8601 expiry timestamp (null for permanent licenses)

## License Distribution Workflow

### For Customer Sales

1. **Generate Customer License:**
   ```bash
   python3 scripts/generate_license.py generate \
     --issued-to "Customer Name <email@example.com> (Company)" \
     --days 365 \
     --output customer_license.json
   ```

2. **Send to Customer:** Provide the generated JSON file to the customer

3. **Customer Activation:**
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
- Uses UUID4 for license keys (cryptographically secure)
- Trust-based validation (no cryptographic signatures)
- Local file storage in `~/.tekmera/license.json`

### Future Enhancements
- Digital signatures for license authenticity
- Server-based license validation
- License transfer and migration support

## Troubleshooting

### License Activation Issues

**Problem:** "Invalid license file format"
- **Solution:** Ensure JSON is valid and contains required fields

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
# 1. Generate customer license
python3 scripts/generate_license.py generate \
  --issued-to "Acme Corp <admin@acme.com>" \
  --days 365 \
  --output acme_corp_license.json

# 2. Verify license file
cat acme_corp_license.json

# 3. Test activation
tekmera license activate --file acme_corp_license.json

# 4. Verify status
tekmera license status

# 5. Test premium features
tekmera analyze ./blueprints
# Navigate to premium features and confirm [Pro] labels are gone
```