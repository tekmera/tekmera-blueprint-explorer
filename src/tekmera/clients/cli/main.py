"""
Main CLI entry point with projection commands and legacy interactive mode.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

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


@click.group()
@click.version_option(version=get_version_string(), prog_name="tekmera")
def cli():
    """Tekmera Explorer - Blueprint Analysis Tool

    Modern projection-based analysis with legacy interactive mode.
    """
    pass


@cli.command()
@click.argument("blueprint_file", type=click.Path(exists=True))
@click.option(
    "--platform",
    type=click.Choice(["workfront_fusion", "make_com"]),
    help="Override platform detection",
)
@click.option(
    "--format", type=click.Choice(["table", "json"]), default="table", help="Output format"
)
def name(blueprint_file, platform, format):
    """Extract blueprint name"""
    blueprint = load_blueprint(blueprint_file)

    platform_obj = Platform(platform) if platform else None

    try:
        result = project("single", "basic", "name", [blueprint], platform=platform_obj)
        format_result(result, format)
    except UnsupportedPlatformError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("blueprint_file", type=click.Path(exists=True))
@click.option(
    "--platform",
    type=click.Choice(["workfront_fusion", "make_com"]),
    help="Override platform detection",
)
@click.option(
    "--format", type=click.Choice(["table", "json"]), default="table", help="Output format"
)
def count(blueprint_file, platform, format):
    """Count modules in blueprint"""
    blueprint = load_blueprint(blueprint_file)

    platform_obj = Platform(platform) if platform else None

    try:
        result = project("single", "basic", "module_count", [blueprint], platform=platform_obj)
        format_result(result, format)
    except UnsupportedPlatformError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name="module-count")
@click.argument("blueprint_file", type=click.Path(exists=True))
@click.option(
    "--platform",
    type=click.Choice(["workfront_fusion", "make_com"]),
    help="Override platform detection",
)
@click.option(
    "--format", type=click.Choice(["table", "json"]), default="table", help="Output format"
)
def module_count(blueprint_file, platform, format):
    """Count modules in blueprint (alias for count)"""
    blueprint = load_blueprint(blueprint_file)

    platform_obj = Platform(platform) if platform else None

    try:
        result = project("single", "basic", "module_count", [blueprint], platform=platform_obj)
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


def main():
    """Main entry point"""
    cli()


if __name__ == "__main__":
    main()
