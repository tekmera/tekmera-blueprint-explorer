#!/usr/bin/env python3
"""
Generate Premium Licenses for Tekmera Fusion Explorer

This script generates permanent premium licenses for customers who have
purchased Tekmera Pro. These licenses never expire and provide access to
all paid features.

Usage:
    ./scripts/generate-pro-license.py
    python scripts/generate-pro-license.py

Examples:
    ./scripts/generate-pro-license.py              # Generate premium license
    ./scripts/generate-pro-license.py --bulk 5     # Generate 5 licenses
    ./scripts/generate-pro-license.py --customer "Acme Corp" --order "12345"
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add src to path to import tekmera modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tekmera.infra.license import license_manager


def main():
    parser = argparse.ArgumentParser(
        description="Generate permanent premium licenses for Tekmera Fusion Explorer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                        # Generate premium license
  %(prog)s --bulk 10              # Generate 10 licenses
  %(prog)s --customer "Acme Corp" # Add customer info
  %(prog)s --format csv --output licenses.csv  # CSV output

License Format:
  TEKMERA-{base64_encoded_signed_data}
  
Features:
  - All premium features (AI analysis, advanced governance, etc.)
  - No expiration (permanent license)
  - Cryptographically signed for tamper resistance
  - Machine-bound for security
  
Common Use Cases:
  - Individual purchases: Single premium licenses
  - Team purchases: Bulk premium licenses
  - Customer fulfillment: After payment processing
        """
    )
    
    parser.add_argument(
        "--bulk",
        type=int,
        metavar="COUNT",
        help="Generate multiple licenses for team purchases"
    )
    
    parser.add_argument(
        "--customer",
        type=str,
        metavar="NAME",
        help="Customer name for license tracking"
    )
    
    parser.add_argument(
        "--order",
        type=str,
        metavar="ID",
        help="Order ID or reference number"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        metavar="FILE",
        help="Save licenses to file (default: print to stdout)"
    )
    
    parser.add_argument(
        "--format",
        choices=["simple", "csv", "json"],
        default="simple",
        help="Output format (default: simple)"
    )
    
    args = parser.parse_args()
    
    # Generate licenses
    try:
        if args.bulk:
            licenses = []
            print(f"Generating {args.bulk} premium licenses...", file=sys.stderr)
            
            for i in range(args.bulk):
                license_key = license_manager.generate_premium_license()
                licenses.append({
                    "license_key": license_key,
                    "license_type": "premium",
                    "customer": args.customer,
                    "order_id": args.order,
                    "generated_at": datetime.now().isoformat(),
                    "expires": None,  # Permanent licenses never expire
                    "license_number": i + 1 if args.bulk > 1 else None
                })
                print(f"Generated {i+1}/{args.bulk}", file=sys.stderr, end="\r")
            
            print(f"\nGenerated {args.bulk} premium licenses successfully!", file=sys.stderr)
            output_licenses(licenses, args.format, args.output, args.customer, args.order)
            
        else:
            license_key = license_manager.generate_premium_license()
            license_data = {
                "license_key": license_key,
                "license_type": "premium",
                "customer": args.customer,
                "order_id": args.order,
                "generated_at": datetime.now().isoformat(),
                "expires": None,  # Permanent licenses never expire
                "license_number": None
            }
            
            print(f"Generated premium license:", file=sys.stderr)
            if args.customer:
                print(f"Customer: {args.customer}", file=sys.stderr)
            if args.order:
                print(f"Order ID: {args.order}", file=sys.stderr)
                
            output_licenses([license_data], args.format, args.output, args.customer, args.order)
            
    except Exception as e:
        print(f"Error generating license: {e}", file=sys.stderr)
        sys.exit(1)


def output_licenses(licenses, format_type, output_file, customer, order_id):
    """Output licenses in specified format"""
    import json
    
    if format_type == "simple":
        output = "\n".join(license["license_key"] for license in licenses)
        
        # Add header for context if customer or order provided
        if customer or order_id:
            header = []
            if customer:
                header.append(f"# Customer: {customer}")
            if order_id:
                header.append(f"# Order: {order_id}")
            header.append(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            header.append("")
            output = "\n".join(header) + output
            
    elif format_type == "csv":
        output = "license_key,license_type,customer,order_id,license_number,generated_at\n"
        for license in licenses:
            output += f"{license['license_key']},{license['license_type']},{license.get('customer', '')},{license.get('order_id', '')},{license.get('license_number', '')},{license['generated_at']}\n"
            
    elif format_type == "json":
        output = json.dumps(licenses, indent=2)
    
    if output_file:
        Path(output_file).write_text(output)
        print(f"Licenses saved to {output_file}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()