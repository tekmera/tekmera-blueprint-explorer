#!/usr/bin/env python3
"""
Generate Evaluation Licenses for Tekmera Fusion Explorer

This script generates evaluation licenses with specified durations for
sales teams, marketing campaigns, and customer trials.

Usage:
    ./scripts/generate-eval-license.py [days]
    python scripts/generate-eval-license.py [days]

Examples:
    ./scripts/generate-eval-license.py          # 30-day default
    ./scripts/generate-eval-license.py 60       # 60-day evaluation
    ./scripts/generate-eval-license.py 7        # 7-day quick trial
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path to import tekmera modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tekmera.infra.license import license_manager


def main():
    parser = argparse.ArgumentParser(
        description="Generate evaluation licenses for Tekmera Fusion Explorer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                # Generate 30-day evaluation
  %(prog)s 60             # Generate 60-day evaluation  
  %(prog)s 7              # Generate 7-day quick trial
  %(prog)s --bulk 10      # Generate 10 licenses (30-day each)
  %(prog)s --bulk 5 14    # Generate 5 licenses (14-day each)

License Format:
  TEKMERA-EVAL-{days}-{hash}
  
Common Use Cases:
  - 7 days: Quick trials for immediate decisions
  - 30 days: Standard evaluation period
  - 60 days: Extended trials for enterprise prospects  
  - 90 days: Large enterprise sales cycles
        """
    )
    
    parser.add_argument(
        "days",
        type=int,
        nargs="?",
        default=30,
        help="Number of evaluation days (1-365, default: 30)"
    )
    
    parser.add_argument(
        "--bulk",
        type=int,
        metavar="COUNT",
        help="Generate multiple licenses for campaigns"
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
    
    # Validate days
    if args.days < 1 or args.days > 365:
        print("Error: Evaluation period must be between 1 and 365 days", file=sys.stderr)
        sys.exit(1)
    
    # Generate licenses
    try:
        if args.bulk:
            licenses = []
            print(f"Generating {args.bulk} evaluation licenses ({args.days} days each)...", file=sys.stderr)
            
            for i in range(args.bulk):
                license_key = license_manager.generate_evaluation_license(args.days)
                licenses.append({
                    "license_key": license_key,
                    "days": args.days,
                    "expires": (datetime.now() + timedelta(days=args.days)).isoformat(),
                    "generated_at": datetime.now().isoformat()
                })
                print(f"Generated {i+1}/{args.bulk}", file=sys.stderr, end="\r")
            
            print(f"\nGenerated {args.bulk} licenses successfully!", file=sys.stderr)
            output_licenses(licenses, args.format, args.output)
            
        else:
            license_key = license_manager.generate_evaluation_license(args.days)
            license_data = {
                "license_key": license_key,
                "days": args.days,
                "expires": (datetime.now() + timedelta(days=args.days)).isoformat(),
                "generated_at": datetime.now().isoformat()
            }
            
            print(f"Generated {args.days}-day evaluation license:", file=sys.stderr)
            output_licenses([license_data], args.format, args.output)
            
    except Exception as e:
        print(f"Error generating license: {e}", file=sys.stderr)
        sys.exit(1)


def output_licenses(licenses, format_type, output_file):
    """Output licenses in specified format"""
    import json
    
    if format_type == "simple":
        output = "\n".join(license["license_key"] for license in licenses)
    elif format_type == "csv":
        output = "license_key,days,expires,generated_at\n"
        for license in licenses:
            output += f"{license['license_key']},{license['days']},{license['expires']},{license['generated_at']}\n"
    elif format_type == "json":
        output = json.dumps(licenses, indent=2)
    
    if output_file:
        Path(output_file).write_text(output)
        print(f"Licenses saved to {output_file}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()