# Tekmera Fusion Explorer — Lemon Squeezy License Strategy

## Objective

Enable Tekmera to sell and provision **Pro licenses** for the Fusion Explorer CLI using Lemon Squeezy's robust license management platform.

---

## Overview

Tekmera Fusion Explorer is distributed as a downloadable CLI tool with two editions:

- **Free Edition:** Full functionality for exploration and static analysis.
- **Pro Edition:** Unlocks AI features, advanced governance checks, and cross-scenario analysis.

Licensing is designed to be:

- **Online-validated** — periodic verification with Lemon Squeezy API.
- **Transparent** — users understand what they purchased.
- **Reliable** — leverages Lemon Squeezy's proven infrastructure.
- **Scalable** — supports team licensing and advanced features.

---

## Core Principles

1. **Secure validation:** License keys are validated with Lemon Squeezy's API.
2. **Frictionless upgrades:** Every "Pro" prompt links to the purchase page.
3. **Environment-based persistence:** License keys stored in environment variables.
4. **Professional infrastructure:** Leverages Lemon Squeezy's license management.

---

## Sales & Delivery Flow

### Step 1: Purchase

- Users purchase **Tekmera Pro** via **Lemon Squeezy Checkout**.
- Product: "Tekmera Fusion Explorer — Pro Edition".
- Pricing: One-time or subscription-based.

### Step 2: License Key Generation

- Lemon Squeezy automatically generates a **unique license key**.
- License key format: `LS-XXXX-XXXX-XXXX` or similar.
- Associated with buyer's email and purchase details.

### Step 3: Delivery

- Lemon Squeezy emails the buyer:
  - Subject: **"Your Tekmera Pro License Key"**
  - Body: step-by-step activation instructions
  - License key included in email body
- Email is sent automatically by Lemon Squeezy.

### Step 4: Activation

- The buyer receives their license key via email.
- In the CLI, they run:

```bash
tekmera license activate LS-1234-5678-9ABC
```

- The CLI validates the key with Lemon Squeezy and stores it in environment variables.
- User receives instructions to persist the license in their shell profile.

### Step 5: Validation

- On each CLI launch, Tekmera loads license from environment variables.
- Periodic validation (hourly) with Lemon Squeezy API for active licenses.
- If validation fails or key is invalid, the CLI runs in Free mode.
- Premium features remain visible but display an upgrade prompt when selected.

---

## License Persistence

### Environment Variables

```bash
export TEKMERA_LICENSE_KEY=LS-1234-5678-9ABC
export TEKMERA_INSTANCE_ID=inst_abcd1234
```

### User Workflow

1. **Activate license:** `tekmera license activate LICENSE-KEY`
2. **Add to shell profile:** User manually adds environment variables to `.bashrc`/`.zshrc`
3. **Automatic loading:** License loads on every CLI startup

---

## Administrative System

### Lemon Squeezy Dashboard

- Central management of all issued licenses
- Real-time analytics and sales data
- Customer support tools and license management
- Automatic refund and chargeback handling

### Support Workflow

- Support team accesses Lemon Squeezy dashboard
- Can deactivate/reactivate licenses as needed
- Users can manage their licenses through Lemon Squeezy portal

---

## License Validation Flow

```
CLI Startup
    ↓
Load environment variables
    ↓
Validate with Lemon Squeezy API (hourly rate limit)
    ↓
Set license type (FREE/PREMIUM)
    ↓
Feature access control
```

### Validation States

- **Active:** License is valid and enabled
- **Expired:** Subscription has expired
- **Disabled:** License has been manually disabled
- **Invalid:** License key doesn't exist

---

## Renewal / Upgrade Handling

- **One-time licenses:** Perpetual access to current major version
- **Subscription plans:** Automatic renewal through Lemon Squeezy
- **Upgrade workflow:** Clicking **"Upgrade to Tekmera Pro"** in CLI opens purchase URL
- **Renewal reminders:** CLI shows expiry warnings 30 days before expiration

---

## Legal & Policy Considerations

- **License Agreement:** Covered by Lemon Squeezy's standard terms
- **Terms of Use for Pro buyers:**
  - Single-seat use per license key
  - Instance-based activation limits
  - Online validation required
- **Privacy:** License validation calls only (no usage telemetry)

---

## Technical Implementation

### Core Components

1. **Lemon Squeezy API Integration** (`lemon_squeezy.py`)
   - License activation
   - Validation and deactivation
   - Error handling and rate limiting

2. **Environment-based Storage** (`license.py`)
   - No file-based operations
   - Environment variable persistence
   - Memory-only license data during runtime

3. **CLI Integration** (`main.py`)
   - Simple license key activation
   - Status checking and deactivation
   - Clear user guidance

### API Endpoints Used

- `POST /v1/licenses/activate` - Activate license key
- `POST /v1/licenses/validate` - Validate existing license
- `POST /v1/licenses/deactivate` - Deactivate license instance

---

## Future Expansion Options

| Phase | Feature | Description |
|-------|---------|-------------|
| Phase 2 | Team Licensing | Multi-user license pools and management |
| Phase 3 | Usage Analytics | Optional usage reporting and insights |
| Phase 4 | Advanced Features | License-based feature tiers |
| Phase 5 | Enterprise Portal | Custom licensing portal for large customers |

---

## Required Assets

- ✅ Lemon Squeezy product configuration
- ✅ License key activation flow
- ✅ Environment variable persistence
- ✅ Validation and rate limiting
- ⏳ Customer email templates
- ⏳ Purchase page integration
- ⏳ Documentation updates

---

## Example User Experience

1. User visits `tekmera.io/pricing` and buys "Pro Edition" via Lemon Squeezy.
2. Within minutes, they receive:
   - Email confirmation from Lemon Squeezy
   - License key in email body
3. User activates license:

```bash
tekmera license activate LS-1234-5678-9ABC
```

4. CLI shows:

```bash
✅ License activated successfully with Lemon Squeezy

To persist this license, add these to your shell profile:
export TEKMERA_LICENSE_KEY=LS-1234-5678-9ABC
export TEKMERA_INSTANCE_ID=inst_abcd1234
```

5. User adds environment variables to shell profile
6. CLI restarts showing Pro edition with all features unlocked

---

## Migration from Legacy System

### Completed

- ✅ Removed file-based license storage
- ✅ Implemented Lemon Squeezy API integration
- ✅ Environment variable persistence
- ✅ Online validation with rate limiting
- ✅ Cleaned legacy code and documentation

### Benefits

- **Simplified architecture:** No file operations or crypto dependencies
- **Professional infrastructure:** Leverages Lemon Squeezy's proven platform
- **Better security:** Online validation prevents key sharing
- **Easier support:** Centralized license management
- **Scalable foundation:** Ready for team licensing and advanced features

---

## Summary

This Lemon Squeezy-based model gives Tekmera:

- Professional license management without backend maintenance
- Secure online validation with graceful offline operation
- Environment-based persistence that works across platforms
- Proven infrastructure for payments and customer management
- Clear path to advanced licensing features (teams, analytics, etc.)
- Simplified codebase with no legacy dependencies