#!/usr/bin/env python3
"""
Main CLI entry point for Tekmera Fusion Explorer
"""
from pathlib import Path

import click
from rich.console import Console

from ...infra.license import license_manager
from ...infra.license_ui import LicenseUI
from .interactive import InteractiveCLI


@click.group()
@click.version_option(version="0.1.0", prog_name="tekmera-fusion-explorer")
@click.pass_context
def cli(ctx):
    """
    Tekmera Fusion Explorer - Diagnostic CLI for Fusion blueprints

    Analyze exported Workfront Fusion blueprint JSON files with interactive
    exploration, governance auditing, and AI-powered insights.
    """
    ctx.ensure_object(dict)


@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False, dir_okay=True))
def analyze(directory: str):
    """
    Analyze blueprint directory with interactive exploration

    DIRECTORY: Path to directory containing blueprint JSON files
    """
    directory_path = Path(directory)

    # Launch interactive CLI - license auto-detected from environment variables
    cli_instance = InteractiveCLI()
    cli_instance.start(directory_path)


@cli.group()
def license():
    """Manage Tekmera Pro licenses"""
    pass


@license.command()
@click.argument("license_key", type=str)
def activate(license_key: str):
    """Activate a Tekmera Pro license using a license key"""
    console = Console()

    console.print("🔑 [bold blue]Activating Tekmera Pro License...[/bold blue]\n")

    success, message = license_manager.activate_license_key(license_key)

    if success:
        info = license_manager.get_license_info()
        LicenseUI.show_license_activation_result(success, message, info, console)
    else:
        LicenseUI.show_license_activation_result(success, message, None, console)
        return 1


@license.command()
def deactivate():
    """Deactivate current license (revert to free edition)"""
    console = Console()

    info = license_manager.get_license_info()
    if info["status"] == "free":
        console.print("ℹ️  [yellow]No active license to deactivate[/yellow]")
        return

    success, message = license_manager.deactivate_license()
    LicenseUI.show_license_deactivation_result(success, message, console)

    if not success:
        return 1


@license.command()
def status():
    """Show current license status"""
    console = Console()

    info = license_manager.get_license_info()
    LicenseUI.show_license_status(info, console)


# Main entry point - for backward compatibility, if called with directory argument
# it will run the analyze command
def main():
    """Main entry point with backward compatibility"""
    import sys

    # Check if called with directory argument (backward compatibility)
    if (
        len(sys.argv) >= 2
        and not sys.argv[1].startswith("-")
        and sys.argv[1] not in ["license", "analyze"]
    ):
        # Insert 'analyze' command for backward compatibility
        sys.argv.insert(1, "analyze")

    cli()


if __name__ == "__main__":
    main()
