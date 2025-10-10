# Tekmera Fusion Explorer — License Provisioning Plan

## Objective

Enable Tekmera to sell and provision **Pro licenses** for the Fusion Explorer CLI using lightweight, maintainable systems — without building a full SaaS backend.

---

## Overview

Tekmera Fusion Explorer is distributed as a downloadable CLI tool with two editions:

- **Free Edition:** Full functionality for exploration and static analysis.
- **Pro Edition:** Unlocks AI features, advanced governance checks, and cross-scenario analysis.

Licensing is designed to be:

- **Offline-first** — no runtime verification calls.
- **Transparent** — users understand what they purchased.
- **Lightweight** — minimal infrastructure and cost.
- **Scalable** — can evolve to API-based or signed verification later.

---

## Core Principles

1. **Trust over enforcement:** The license system signals entitlement, not DRM.
2. **Frictionless upgrades:** Every "Pro" prompt links to the purchase page.
3. **Offline verification:** All verification happens locally using the license file.
4. **Self-contained provisioning:** Tekmera controls key generation and fulfillment.

---

## Sales & Delivery Flow

### Step 1: Purchase

- Users purchase **Tekmera Pro** via **Stripe Checkout** (or Lemon Squeezy / Paddle / Gumroad).
- Product: "Tekmera Fusion Explorer — Pro Edition".
- Pricing: One-time or annual subscription.

### Step 2: Webhook Trigger

- A Stripe webhook fires on successful payment (`checkout.session.completed`).
- The webhook triggers an automation in **n8n**, **Zapier**, or a small FastAPI script.

### Step 3: License Generation

- The automation generates a **unique license record**:
  - `license_key`: short alphanumeric string, e.g. `TK-9F3D-4B21`
  - `edition`: `"pro"`
  - `issued_to`: buyer's email
  - `expiry`: optional, if subscription-based
  - `signature`: optional (for future signing support)
- The license is written to a JSON file named `license.json`.

### Step 4: Delivery

- The system emails the buyer:
  - Subject: **"Your Tekmera Pro License"**
  - Body: step-by-step activation instructions
  - Attachment: `license.json`
- Email is sent automatically through the automation platform's SMTP or Gmail integration.

### Step 5: Activation

- The buyer saves the attached license file locally.
- In the CLI, they run:

```bash
tekmera license activate --file /path/to/license.json
```

- The CLI stores the license in `~/.tekmera/license.json`.

### Step 6: Verification

- On each CLI launch, Tekmera checks for a valid local license.
- If missing or invalid, the CLI runs in Free mode.
- Premium features remain visible but display an upgrade prompt when selected.

---

## Administrative System

### License Registry

A central registry of issued licenses is maintained for internal tracking:

- Stored in **Google Sheets**, **Airtable**, or a small SQLite DB.
- Columns: `license_key`, `email`, `edition`, `issued_at`, `expiry`, `status`.
- Each automation step appends to this registry for audit and support.

### Support Workflow

- Support team can search for a license by email or key.
- Users can re-request license files via email if lost.

---

## Renewal / Upgrade Handling

- For one-time licenses: perpetual access to current major version.
- For annual plans: expiry date embedded in license; user prompted to renew when expired.
- Upgrade workflow: clicking **"Upgrade to Tekmera Pro"** in CLI opens the purchase URL.

---

## Legal & Policy Considerations

- Add a `LICENSE.txt` covering software use.
- Add a short **Terms of Use** for Pro buyers:
  - Single-seat use per license key.
  - Non-transferable without Tekmera's consent.
  - Offline verification; no telemetry without consent.
- Include a short privacy statement for any telemetry or email collection.

---

## Future Expansion Options

| Phase | Feature | Description |
|-------|---------|-------------|
| Phase 2 | Signed Licenses | Add Ed25519 signatures to prevent tampering |
| Phase 3 | License Verification API | CLI can verify key validity via HTTPS |
| Phase 4 | Team Licensing | Add seat-based and multi-user plans |
| Phase 5 | Portal | Users log in to manage and re-download licenses |

---

## Required Assets

- Stripe product page + success URL
- Tekmera email template for license delivery
- `license.json` template file
- n8n/Zapier workflow for Stripe → Email → Registry
- README section: **"Activating Tekmera Pro"**

---

## Example User Experience

1. User visits `tekmera.io/pricing` and buys "Pro Edition".
2. Within minutes, they receive:
   - Email confirmation from Stripe
   - Separate email from Tekmera with `license.json`
3. User installs license:

```bash
tekmera license activate --file ~/Downloads/license.json
```

4. CLI restarts showing:

```bash
Tekmera Fusion Explorer 0.1.0  [Edition: Pro]
```

5. Premium commands now execute normally.

---

## Summary

This model gives Tekmera:

- Immediate ability to sell licenses with no backend maintenance.
- Professional provisioning flow through existing automation tools.
- Offline verification with minimal support overhead.
- A clear path to evolve into signed or API-managed licensing later.