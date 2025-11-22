"""
Main CLI entry point with projection commands and legacy interactive mode.
"""

import json
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import click

from ..._version import get_version_string
from ...projections import project
from ...projections.meta.types import UnsupportedPlatformError
from .formatters.table import format_result


def _simplify_blueprint_name(name: str) -> str:
    """Simplify blueprint name for file naming."""
    # Basic cleaning
    simplified = name.replace(" ", "_").replace("/", "_").replace("|", "_").replace(":", "_").replace(">", "_")
    
    # Remove common prefixes
    for prefix in ["FUS001", "FUS002", "FUS003", "FUS004", "FUS005", "FUS006", "FUS007", "FUS008", "FUS009", 
                  "FUS010", "FUS011", "FUS012", "FUS013", "FUS014", "FUS015", "FUS016", "FUS017", "FUS018", 
                  "FUS019", "FUS020", "FUS", "MAKE", "Blueprint_", "Scenario_", "Template_"]:
        if simplified.startswith(prefix):
            simplified = simplified[len(prefix):]
            # Clean up leading separators
            while simplified.startswith(("_", "-", ".", " ")):
                simplified = simplified[1:]
            break
    
    # Remove version suffixes like v1.2, v2.1, V1.2, etc.
    import re
    simplified = re.sub(r'_?[vV]\d+[\.\d]*$', '', simplified)
    
    # Intelligent truncation - try to preserve meaningful parts
    if len(simplified) > 35:
        # Split on underscores and try to keep key parts
        parts = simplified.split("_")
        if len(parts) > 1:
            # Keep first and last meaningful parts
            key_parts = []
            current_length = 0
            
            # Always include first part if it's meaningful
            if parts[0] and len(parts[0]) > 2:
                key_parts.append(parts[0])
                current_length = len(parts[0])
            
            # Add middle parts if they fit
            for part in parts[1:-1]:
                if current_length + len(part) + 1 <= 25:  # +1 for underscore
                    key_parts.append(part)
                    current_length += len(part) + 1
                else:
                    # Skip long middle parts but indicate truncation
                    if "..." not in key_parts:
                        key_parts.append("...")
                    break
            
            # Always try to include last part if it's meaningful
            last_part = parts[-1]
            if last_part and len(last_part) > 2 and current_length + len(last_part) + 4 <= 35:  # +4 for _...
                if key_parts[-1] == "...":
                    key_parts.append(last_part)
                else:
                    key_parts.append(last_part)
            
            simplified = "_".join(key_parts)
        else:
            # Single long string, truncate intelligently
            simplified = simplified[:32] + "..."
    
    return simplified


def _open_file(file_path: str):
    """Open file with the default system application."""
    try:
        if platform.system() == "Darwin":  # macOS
            subprocess.run(["open", file_path], check=True)
        elif platform.system() == "Windows":  # Windows
            os.startfile(file_path)
        else:  # Linux and others
            subprocess.run(["xdg-open", file_path], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError, AttributeError):
        # If opening fails, just continue silently
        pass


def load_blueprint(file_path: str) -> Dict[str, Any]:
    """Load blueprint JSON from file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{file_path}': {e}")
        sys.exit(1)


def load_blueprints_from_paths(paths: List[str], max_depth: int = 3) -> List[Dict[str, Any]]:
    """Load blueprints from files and/or directories (up to 3 levels deep)."""
    blueprints = []

    for path_str in paths:
        path = Path(path_str)

        if path.is_file():
            # Single file
            if path.suffix.lower() == ".json":
                blueprints.append(load_blueprint(str(path)))
            else:
                print(f"Warning: Skipping non-JSON file '{path}'")

        elif path.is_dir():
            # Directory - scan for JSON files with depth limit
            # Build pattern with depth limit
            patterns = ["*.json"]  # Current directory
            for depth in range(1, max_depth + 1):
                patterns.append("*/" * depth + "*.json")

            json_files = []
            for pattern in patterns:
                json_files.extend(path.glob(pattern))
            # Remove duplicates and sort
            json_files = sorted(set(json_files))

            if not json_files:
                print(f"Warning: No JSON files found in directory '{path}'")
                continue

            for json_file in sorted(json_files):
                blueprints.append(load_blueprint(str(json_file)))

        else:
            print(f"Error: Path '{path}' not found")
            sys.exit(1)

    if not blueprints:
        print("Error: No valid blueprint files found")
        sys.exit(1)

    return blueprints


@click.group()
@click.version_option(version=get_version_string(), prog_name="tekmera")
def cli():
    """Tekmera Explorer - Blueprint Analysis Tool

    \b
    PATHS can be files or directories. Directories scanned 3 levels deep.
    Platform auto-detected. Available formats: table (default), json, html
    """


@cli.command()
@click.argument("query", type=str)
@click.argument("paths", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--case-sensitive", "-c", is_flag=True, help="Case sensitive search")
@click.option(
    "--format", type=click.Choice(["table", "json"]), default="table", help="Output format"
)
def search(query, paths, case_sensitive, format):
    """Search for text content across blueprint components"""
    blueprints = load_blueprints_from_paths(list(paths))

    try:
        result = project(
            "blueprints",
            "search",
            "text_content",
            blueprints,
            query=query,
            case_sensitive=case_sensitive,
        )
        format_result(result, format)
    except UnsupportedPlatformError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("blueprint_path", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--format", type=click.Choice(["table", "json", "html"]), default="table", help="Output format"
)
def report(blueprint_path, format):
    """Generate one-page summary report for a single blueprint file"""
    blueprint = load_blueprint(blueprint_path)

    try:
        # Use new reporting system instead of projection directly
        from ...reporting.summary import generate_summary_report
        result = generate_summary_report(blueprint)
        if format == "table":
            # For table format, print the formatted report text
            click.echo(result.data.to_text())
        elif format == "html":
            # For HTML format, generate HTML file
            from .formatters.html import render_report_to_html
            
            # Create reports directory
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)
            
            # Create simplified output filename based on blueprint name
            blueprint_name = _simplify_blueprint_name(result.data.blueprint_name)
            output_path = reports_dir / f"{blueprint_name}_report.html"
            
            html_file = render_report_to_html(result.data, str(output_path))
            click.echo(f"HTML report generated: {html_file}")
            # Auto-open the HTML file
            _open_file(html_file)
        else:
            # For JSON format, output the structured data
            # Convert the typed report to dict for JSON serialization
            json_result = result.__replace__(data=result.data.to_dict())
            format_result(json_result, format)
    except UnsupportedPlatformError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("blueprint1_path", type=click.Path(exists=True, dir_okay=False))
@click.argument("blueprint2_path", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--format", type=click.Choice(["table", "json", "html"]), default="table", help="Output format"
)
def diff(blueprint1_path, blueprint2_path, format):
    """Compare two blueprint files and generate diff report"""
    try:
        # Load both blueprints
        blueprint1 = load_blueprint(blueprint1_path)
        blueprint2 = load_blueprint(blueprint2_path)
        
        # Use new reporting system for diff reports
        from ...reporting.diff import generate_diff_report
        
        # Generate diff report
        result = generate_diff_report(blueprint1, blueprint2)
        
        if format == "table":
            # For table format, print the formatted report text
            click.echo(result.data.to_text())
        elif format == "html":
            # For HTML format, generate HTML file
            from .formatters.html import render_report_to_html
            
            # Create reports directory
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)
            
            # Create timestamp-based filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = reports_dir / f"diff_{timestamp}.html"
            
            html_file = render_report_to_html(result.data, str(output_path))
            click.echo(f"Diff HTML report generated: {html_file}")
            # Auto-open the HTML file
            _open_file(html_file)
        else:
            # For JSON format, output the structured data
            json_result = result.__replace__(data=result.data.to_dict())
            format_result(json_result, format)
            
    except Exception as e:
        click.echo(f"Error generating diff report: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--platform", 
    type=click.Choice(["workfront_fusion", "make_com"]), 
    default="workfront_fusion", 
    help="Platform for sample report"
)
@click.option(
    "--format", type=click.Choice(["table", "json", "html"]), default="table", help="Output format"
)
def demo(platform, format):
    """Generate sample report for demos and documentation"""
    from ...projections.meta.types import Platform
    from ...reporting.summary.sample import create_sample_report
    
    # Convert string to enum
    platform_enum = Platform.WORKFRONT_FUSION if platform == "workfront_fusion" else Platform.MAKE_COM
    
    try:
        # Generate sample report
        result = create_sample_report(platform_enum)
        
        if format == "table":
            # For table format, print the formatted report text
            click.echo(result.data.to_text())
        elif format == "html":
            # For HTML format, generate HTML file
            from .formatters.html import render_report_to_html
            
            # Create output filename based on blueprint name and platform
            blueprint_name = f"Sample_{platform.title()}_Report"
            output_path = f"{blueprint_name}.html"
            
            html_file = render_report_to_html(result.data, output_path)
            click.echo(f"Sample HTML report generated: {html_file}")
        else:
            # For JSON format, output the structured data
            json_result = result.__replace__(data=result.data.to_dict())
            format_result(json_result, format)
            
    except Exception as e:
        click.echo(f"Error generating sample report: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
def interactive(directory):
    """Launch legacy interactive exploration mode"""
    click.echo("🔄 Launching legacy interactive mode...")

    # Import and launch legacy interactive system
    from ...legacy.interfaces.cli.interactive import InteractiveCLI

    try:
        # Initialize and launch legacy interactive CLI
        interactive_cli = InteractiveCLI()
        interactive_cli.start(Path(directory))

    except Exception as e:
        click.echo(f"❌ Error launching interactive mode: {e}", err=True)
        sys.exit(1)


def main():
    """Main entry point"""
    cli()


if __name__ == "__main__":
    main()
