"""
Main CLI entry point with projection commands and legacy interactive mode.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import click

from ..._version import get_version_string
from ...projections import project
from ...projections.meta.types import Platform, UnsupportedPlatformError
from .formatters.table import format_result


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
            if path.suffix.lower() == '.json':
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
    Commands:
      name PATHS... [--format=FORMAT]
      count PATHS... [--format=FORMAT]
      module-count PATHS... [--format=FORMAT]
      interactive DIRECTORY

    \b
    PATHS can be files or directories. Directories scanned 3 levels deep.
    Platform auto-detected. Formats: table (default), json
    """


@cli.command()
@click.argument("paths", nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    "--format", type=click.Choice(["table", "json"]), default="table", help="Output format"
)
def name(paths, format):
    """Extract blueprint name(s) from files or directories"""
    blueprints = load_blueprints_from_paths(list(paths))

    try:
        result = project("blueprints", "basic", "name", blueprints)
        format_result(result, format)
    except UnsupportedPlatformError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("paths", nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    "--format", type=click.Choice(["table", "json"]), default="table", help="Output format"
)
def count(paths, format):
    """Count modules in blueprint(s) from files or directories"""
    blueprints = load_blueprints_from_paths(list(paths))

    try:
        result = project("blueprints", "basic", "module_count", blueprints)
        format_result(result, format)
    except UnsupportedPlatformError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name="module-count")
@click.argument("paths", nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    "--format", type=click.Choice(["table", "json"]), default="table", help="Output format"
)
def module_count(paths, format):
    """Count modules in blueprint(s) from files or directories (alias for count)"""
    blueprints = load_blueprints_from_paths(list(paths))

    try:
        result = project("blueprints", "basic", "module_count", blueprints)
        format_result(result, format)
    except UnsupportedPlatformError as e:
        click.echo(f"Error: {e}", err=True)
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


@cli.command()
def capabilities():
    """Show detailed current capabilities and architecture"""
    click.echo(
        """
TEKMERA EXPLORER - CURRENT CAPABILITIES

=== BLUEPRINT ANALYSIS COMMANDS ===
name           Extract blueprint name from JSON file
count          Count modules in blueprint  
module-count   Count modules (alias for count)
interactive    Launch full-featured legacy interface

=== PLATFORM SUPPORT ===
Workfront Fusion    Full support with auto-detection
Make.com           Basic support with auto-detection

=== OUTPUT FORMATS ===
table (default)    Human-readable tabular output
json              Machine-readable JSON output

=== ARCHITECTURE ===
• Pure functional projection system
• Platform-aware analysis with auto-detection
• Component detection: modules, routers, filters, error handlers
• Immutable input processing with deterministic outputs
• Registry-based function discovery and routing

=== PROJECTION STRUCTURE ===
Components/         Individual component analysis (modules, routers, etc.)
Blueprints/         Whole blueprint analysis (names, counts, etc.)

=== IN DEVELOPMENT ===
• String search across scenarios
• Cross-blueprint corpus analysis
• Enhanced component-level projections
• Additional platform support

Documentation: See CLAUDE.md and docs/ARCHITECTURE.md
    """.strip()
    )


def main():
    """Main entry point"""
    cli()


if __name__ == "__main__":
    main()
