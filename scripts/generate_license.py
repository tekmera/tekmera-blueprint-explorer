#!/usr/bin/env python3
"""
License Generator for Tekmera Fusion Explorer

Generates license files for testing the premium licensing system.
"""
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import click


@click.command()
@click.option('--edition', default='pro', help='License edition (pro, enterprise)')
@click.option('--issued-to', required=True, help='Name or organization the license is issued to')
@click.option('--days', default=365, help='Number of days until expiry (default: 365, 0 = never expires)')
@click.option('--output', '-o', default='license.json', help='Output file path')
def generate_license(edition: str, issued_to: str, days: int, output: str):
    """Generate a Tekmera Pro license file."""
    
    # Generate unique license key
    license_key = str(uuid.uuid4()).upper()
    
    # Calculate expiry date
    issued_at = datetime.now().isoformat()
    expiry = None
    if days > 0:
        expiry_date = datetime.now() + timedelta(days=days)
        expiry = expiry_date.isoformat()
    
    # Create license data
    license_data = {
        "license_key": license_key,
        "edition": edition.lower(),
        "issued_to": issued_to,
        "issued_at": issued_at,
        "expiry": expiry
    }
    
    # Write license file
    output_path = Path(output)
    with open(output_path, 'w') as f:
        json.dump(license_data, f, indent=2)
    
    print(f"✅ License generated successfully!")
    print(f"📄 File: {output_path.absolute()}")
    print(f"🔑 License Key: {license_key}")
    print(f"👤 Issued To: {issued_to}")
    print(f"🏷️  Edition: {edition.title()}")
    print(f"📅 Issued: {issued_at}")
    
    if expiry:
        print(f"⏰ Expires: {expiry} ({days} days)")
    else:
        print(f"⏰ Expires: Never")
    
    print(f"\n🚀 To activate this license:")
    print(f"   tekmera license activate --file {output}")


@click.command()
@click.option('--name', required=True, help='Customer name')
@click.option('--email', help='Customer email (optional)')
@click.option('--company', help='Company name (optional)')
@click.option('--trial-days', default=30, help='Trial period in days (default: 30)')
@click.option('--output', '-o', help='Output file path (default: {name}_trial_license.json)')
def generate_trial(name: str, email: str, company: str, trial_days: int, output: str):
    """Generate a trial license with customer information."""
    
    # Build issued_to string
    issued_to_parts = [name]
    if email:
        issued_to_parts.append(f"<{email}>")
    if company:
        issued_to_parts.append(f"({company})")
    
    issued_to = " ".join(issued_to_parts)
    
    # Default output filename
    if not output:
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_').lower()
        output = f"{safe_name}_trial_license.json"
    
    # Generate trial license
    license_key = str(uuid.uuid4()).upper()
    issued_at = datetime.now().isoformat()
    expiry_date = datetime.now() + timedelta(days=trial_days)
    expiry = expiry_date.isoformat()
    
    license_data = {
        "license_key": license_key,
        "edition": "pro",
        "issued_to": issued_to,
        "issued_at": issued_at,
        "expiry": expiry,
        "trial": True
    }
    
    # Write license file
    output_path = Path(output)
    with open(output_path, 'w') as f:
        json.dump(license_data, f, indent=2)
    
    print(f"✅ Trial license generated!")
    print(f"📄 File: {output_path.absolute()}")
    print(f"🔑 License Key: {license_key}")
    print(f"👤 Customer: {issued_to}")
    print(f"⏰ Trial Expires: {expiry} ({trial_days} days)")
    print(f"\n🚀 Customer can activate with:")
    print(f"   tekmera license activate --file {output}")


@click.group()
def cli():
    """Tekmera License Generator
    
    Generate license files for testing or customer distribution.
    """
    pass


cli.add_command(generate_license, name='generate')
cli.add_command(generate_trial, name='trial')


if __name__ == '__main__':
    cli()