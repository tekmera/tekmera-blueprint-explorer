# Lemon Squeezy License Integration

This document outlines Tekmera's current licensing implementation using Lemon Squeezy's online license API.

## Overview

Tekmera Fusion Explorer now uses Lemon Squeezy exclusively for license management:
- **Online licensing only** via Lemon Squeezy API
- Simple license key activation
- Automatic validation and renewal
- No offline file-based licensing

## New Features

### License Key Activation
```bash
# Activate using a license key
tekmera license activate YOUR-LICENSE-KEY
```

### Online Validation
- **Licenses validated** periodically with Lemon Squeezy API
- **Rate limited**: Maximum once per hour to respect API limits
- **Graceful degradation**: If validation fails, continues with cached license

### License Data Format
Lemon Squeezy license format:
```json
{
  "license_key": "uuid-formatted-key",
  "edition": "pro",
  "issued_to": "Customer Name <email@domain.com>",
  "issued_at": "2025-10-10T15:47:03.718321",
  "expiry": "2026-11-09T15:47:03.718367",
  "instance_id": "lemon-squeezy-instance-id",
  "status": "active"
}
```

## Architecture

### Core Components

1. **`lemon_squeezy.py`**: Lemon Squeezy API integration
   - `LemonSqueezyAPI`: HTTP client for API calls
   - `LemonSqueezyLicenseManager`: License lifecycle management
   - Rate limiting and error handling

2. **`license.py`**: Simplified license management
   - `activate_license_key()` method for activation
   - Periodic online validation
   - Clean, Lemon Squeezy-only implementation

3. **Updated CLI**: 
   - Simple license key argument
   - Clear error messages
   - Streamlined activation flow

### Integration Points

#### License Manager Flow
```
User activates license key
    ↓
LemonSqueezyAPI.activate_license()
    ↓
Store license locally with instance_id
    ↓
Periodic validation via LemonSqueezyAPI.validate_license()
    ↓
Graceful degradation if offline
```

#### Validation Strategy
1. **Startup**: Load local license, validate format
2. **Periodic**: Check online every hour (rate limited)
3. **Access**: Validate before premium feature access
4. **Fallback**: Use local validation if online fails

## User Guide

### License Management

1. **Activate license**: Use license keys from Lemon Squeezy
   ```bash
   tekmera license activate LS-123-ABC-DEF
   ```

2. **Check status**: View current license information
   ```bash
   tekmera license status
   ```

3. **Deactivate**: Remove license from current machine
   ```bash
   tekmera license deactivate
   ```

4. **Persist license**: Add environment variables to shell profile
   ```bash
   export TEKMERA_LICENSE_KEY=LS-123-ABC-DEF
   export TEKMERA_INSTANCE_ID=inst_abcd1234
   ```

### For Sales/Distribution

1. **Lemon Squeezy Configuration**:
   - Product configured in Lemon Squeezy dashboard
   - Automatic license key generation on purchase
   - Email delivery handled by Lemon Squeezy

2. **Customer Experience**:
   - Customers receive license keys via email
   - Simple activation with CLI command
   - Environment variable persistence for convenience

### For Development

1. **Testing Online Features**:
   ```python
   from tekmera.infra.lemon_squeezy import LemonSqueezyAPI
   
   api = LemonSqueezyAPI()
   success, response = api.activate_license("test-key")
   ```

2. **Testing Offline Mode**:
   ```python
   # Disconnect internet and test graceful degradation
   license_manager.validate_license_on_access()
   ```

## API Reference

### Lemon Squeezy Endpoints Used

- `POST /v1/licenses/activate`: Activate license key
- `POST /v1/licenses/validate`: Validate existing license
- `POST /v1/licenses/deactivate`: Deactivate license instance

### Rate Limiting
- 60 requests per minute (Lemon Squeezy limit)
- Local rate limiting: 1 validation per hour per license

### Error Handling
- Network failures: Graceful fallback to local validation
- Invalid keys: Clear error messages
- Rate limits: Automatic retry with backoff

## Security Considerations

1. **Instance Tracking**: Each activation creates unique instance ID
2. **Online Validation**: Prevents license sharing across machines
3. **Graceful Degradation**: No internet required for basic functionality
4. **Legacy Support**: Existing digital signatures still validated

## Current Implementation

### Key Features
- License key activation via Lemon Squeezy API
- Environment variable persistence
- Online validation with hourly rate limiting
- Graceful offline operation after activation
- Clean, dependency-free codebase

### Architecture Benefits
- No file-based operations
- Professional license management
- Secure online validation
- Scalable foundation for team licensing

## Future Enhancements

1. **Team Licenses**: Multi-user license management
2. **License Analytics**: Usage tracking and reporting
3. **Auto-renewal**: Seamless subscription renewals
4. **License Pools**: Shared license allocation

## Troubleshooting

### Common Issues

1. **No Internet Connection**:
   - System falls back to local validation
   - All features remain functional

2. **Invalid License Key**:
   ```
   Error: Activation failed: Invalid license key
   ```
   - Verify key format and validity
   - Contact support for replacement

3. **License Already Activated**:
   ```
   Error: License key already activated on maximum instances
   ```
   - Deactivate unused instances
   - Contact support for additional activations

### Debug Commands
```bash
# Check license status
tekmera license status

# Test connectivity
python -c "from tekmera.infra.lemon_squeezy import LemonSqueezyLicenseManager; print(LemonSqueezyLicenseManager().is_online_validation_available())"
```

## Current Status

- ✅ Lemon Squeezy API integration
- ✅ License key activation system
- ✅ Environment variable persistence
- ✅ Online validation with rate limiting
- ✅ Error handling and graceful degradation
- ✅ Complete documentation
- ⏳ Webhook integration (planned)
- ⏳ Team license support (planned)
- ⏳ Usage analytics (planned)