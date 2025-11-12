# Tekmera Development and License Scripts

This directory contains scripts for development, license generation, and testing different license modes.

## Development License Testing Scripts

These scripts allow you to quickly test Tekmera with different license types during development:

### 🆓 Free Mode
```bash
./scripts/run-dev-free.sh ./blueprints
```
- Clears any existing license
- Runs in FREE mode with basic features only
- Tests free-tier functionality and upgrade prompts
- Features: Basic exploration, 5 governance rules, blueprint comparison

### ⏰ Evaluation Mode
```bash
# 30-day evaluation (default)
./scripts/run-dev-eval.sh ./blueprints

# Custom duration evaluation  
./scripts/run-dev-eval.sh 7 ./blueprints     # 7-day trial
./scripts/run-dev-eval.sh 60 ./blueprints    # 60-day evaluation
```
- Generates temporary evaluation license
- Tests evaluation functionality and expiration warnings
- Features: ALL Pro features for specified duration
- Automatic expiration and reversion to Free

### 💎 Premium Mode
```bash
./scripts/run-dev-pro.sh ./blueprints
```
- Generates temporary premium license
- Tests full Pro functionality without expiration
- Features: ALL Pro features permanently enabled
- No expiration warnings or upgrade prompts

### 🛠️ Local Pro Mode (Fastest)
```bash
./scripts/run-dev-local-pro.sh ./blueprints
```
- Uses `TEKMERA_LOCAL_PRO=true` environment variable
- Bypasses license system entirely for development
- Fastest way to test Pro features
- No license generation or activation required

## License Generation Scripts

These scripts are for sales teams and administrators to generate customer licenses:

### Generate Evaluation Licenses
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

**Output formats:**
- `simple`: Just license keys (default) - opaque cryptographic format
- `csv`: CSV format with metadata
- `json`: JSON format with full details

**Security Note:** All license keys are now cryptographically signed and base64-encoded for tamper resistance.

### Generate Premium Licenses
```bash
# Basic usage  
./scripts/generate-pro-license.py                     # Standard Pro license
./scripts/generate-pro-license.py pro                 # Pro license explicitly
./scripts/generate-pro-license.py enterprise          # Enterprise license

# With customer information
./scripts/generate-pro-license.py --customer "Acme Corp" --order "ORD-12345"

# Bulk generation for teams
./scripts/generate-pro-license.py --bulk 5            # 5 Pro licenses
./scripts/generate-pro-license.py --bulk 10 enterprise # 10 Enterprise licenses

# Save to file with metadata
./scripts/generate-pro-license.py --bulk 5 --customer "TechCorp" --format csv --output techcorp-licenses.csv
```

## Common Development Workflows

### Testing License Transitions
```bash
# Test free → evaluation → pro progression
./scripts/run-dev-free.sh ./blueprints
./scripts/run-dev-eval.sh 7 ./blueprints  
./scripts/run-dev-pro.sh ./blueprints
```

### Testing Evaluation Expiration
```bash
# Generate 1-day evaluation for quick testing
./scripts/run-dev-eval.sh 1 ./blueprints

# Wait 24 hours or manually expire license for testing
rm ~/.tekmera/license.json
./scripts/run-dev-free.sh ./blueprints  # Should show "evaluation expired"
```

### Sales Team License Generation
```bash
# Generate evaluation licenses for a campaign
./scripts/generate-eval-license.py --bulk 50 30 --format csv --output marketing-campaign-eval.csv

# Generate customer licenses after purchase
./scripts/generate-pro-license.py --customer "BigCorp Inc" --order "PO-98765" --format json --output bigcorp-license.json

# Generate extended evaluations for enterprise prospects
./scripts/generate-eval-license.py 90 --output enterprise-prospect.txt
```

### Development Feature Testing
```bash
# Quick Pro feature testing (no license setup)
./scripts/run-dev-local-pro.sh ./blueprints

# Test specific license validation
./scripts/run-dev-pro.sh ./blueprints     # Test premium license validation
./scripts/run-dev-eval.sh 3 ./blueprints  # Test expiration warnings (3 days)
```

## License File Locations

- **License Storage**: `~/.tekmera/license.json`
- **Machine Fingerprint**: `~/.tekmera/.machine_id` (created automatically)

## Environment Variables

- `TEKMERA_LOCAL_PRO=true` - Enable all Pro features without license (development only)
- `OPENAI_API_KEY` - Required for AI features (all license types)

## Script Dependencies

All scripts require:
1. Virtual environment activated (`venv/bin/activate`)
2. Tekmera installed in development mode (`pip install -e .`)
3. Python 3.8+ with required dependencies

## Troubleshooting

### Common Issues

1. **Virtual environment not active**:
   ```bash
   source venv/bin/activate
   ```

2. **License activation fails**:
   ```bash
   # Clear existing license and try again
   rm -f ~/.tekmera/license.json
   ./scripts/run-dev-pro.sh ./blueprints
   ```

3. **Permission denied**:
   ```bash
   chmod +x scripts/*.py scripts/*.sh
   ```

4. **Module not found**:
   ```bash
   # Ensure you're in the project directory and have installed in dev mode
   pip install -e .
   ```

### Debug License Status
```bash
# Check current license
python -m tekmera.interfaces.cli.main license status

# Test license generation manually
python scripts/generate-eval-license.py 30
python scripts/generate-pro-license.py pro
```

## Use Cases by Role

### **Developers**
- Use `run-dev-local-pro.sh` for fastest Pro feature testing
- Use other scripts to test license validation and UI flows
- Generate test licenses for unit/integration testing

### **Sales Teams**  
- Use `generate-eval-license.py` to create trial licenses for prospects
- Use `generate-pro-license.py` to fulfill customer purchases
- Use bulk generation for campaigns and team sales

### **Support Teams**
- Use license generation scripts to replace lost/expired licenses
- Use development scripts to reproduce customer license issues
- Test different license scenarios for troubleshooting

### **Marketing Teams**
- Use bulk evaluation license generation for campaigns
- Create time-limited trials for events and webinars
- Generate analytics-ready license batches with CSV output

## Security Notes

- Development scripts generate temporary licenses for testing only
- Production license generation should use secure key generation
- Machine fingerprints prevent license sharing across devices
- License files are stored locally and tied to specific machines