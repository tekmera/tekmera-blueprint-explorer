#!/usr/bin/env python3
"""
Main CLI entry point for Tekmera Fusion Explorer
"""
from pathlib import Path

import click
from rich.console import Console

from ..._version import get_version_string
from ...infra.license import license_manager
from ...infra.license_ui import LicenseUI
from .interactive import InteractiveCLI


@click.group()
@click.version_option(version=get_version_string(), prog_name="tekmera-fusion-explorer")
@click.pass_context
def cli(ctx):
    """
    Tekmera Fusion Explorer - Professional CLI for Workfront Fusion blueprint analysis

    Analyze exported Fusion blueprint JSON files with comprehensive diagnostic capabilities:
    
    \b
    🔍 SCENARIO EXPLORATION
    • Interactive module exploration and search within scenarios
    • Live scenario walkthrough with step-by-step execution flow (Pro)
    • AI-powered business process descriptions (Pro)
    
    \b
    📊 BLUEPRINT ANALYSIS  
    • Static analysis reports with module counts and field analysis
    • Cross-blueprint search and pattern detection (Pro)
    • Cross-blueprint AI queries for organizational insights (Pro)
    
    \b
    ⚖️ GOVERNANCE AUDITING
    • 5 essential governance checks (naming, structure, connections) - FREE
    • 6 advanced complexity and density analysis checks - PRO
    • Compliance reporting for operational standards
    
    \b
    🔄 BLUEPRINT COMPARISON
    • Side-by-side scenario comparison
    • Functional difference identification
    • Change impact analysis
    
    \b
    💼 LICENSING MODEL
    • FREE EDITION: Core exploration, basic governance, scenario comparison
    • PRO EDITION: AI features, cross-blueprint analysis, advanced governance
    • Activate Pro: 'tekmera license activate <key>' 
    • Check status: 'tekmera license status'
    
    \b
    EXAMPLES:
      tekmera analyze ./blueprints          # Launch interactive analysis
      tekmera license status               # Check current license  
      tekmera license activate ABC-123     # Activate Pro license
    
    Visit https://tekmera.com for Pro licenses and documentation.
    """
    ctx.ensure_object(dict)


@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False, dir_okay=True))
def analyze(directory: str):
    """
    Launch interactive blueprint analysis for a directory of Fusion scenarios

    Recursively discovers and analyzes all .json blueprint files in DIRECTORY
    and its subdirectories. Launches an interactive menu system providing:
    
    \b
    • Scenario exploration and module-level inspection
    • Cross-blueprint search and analysis (Pro)
    • Governance auditing with 11 available checks (5 free + 6 Pro)
    • Blueprint comparison and diff analysis
    • AI-powered insights and business process descriptions (Pro)
    
    The interactive interface automatically detects your license status
    and enables appropriate features.
    
    \b
    DIRECTORY: Path to directory containing exported Fusion blueprint JSON files
               Supports nested folder structures (e.g., client/environment/scenario)
    
    \b
    EXAMPLES:
      tekmera analyze ./fusion-blueprints     # Analyze all blueprints
      tekmera analyze ~/Downloads/scenarios   # Analyze downloaded blueprints
      tekmera analyze .                       # Analyze current directory
    """
    directory_path = Path(directory)

    # Launch interactive CLI - license auto-detected from environment variables
    cli_instance = InteractiveCLI()
    cli_instance.start(directory_path)


@cli.group()
def license():
    """
    Manage Tekmera Pro licenses and subscription status
    
    \b
    PRO FEATURES UNLOCKED:
    • Cross-blueprint search and organizational analysis
    • AI-powered business process descriptions (requires OpenAI API key)
    • Live scenario walkthrough with step-by-step execution
    • Advanced governance checks (6 complexity/density metrics)
    • Cross-blueprint AI queries for strategic insights
    
    \b
    LICENSE MANAGEMENT:
      tekmera license status          # Check current license status
      tekmera license activate <key>  # Activate Pro license with key
      tekmera license deactivate      # Revert to Free edition
      tekmera license local           # Enable local development mode
    
    Visit https://tekmera.com to purchase Pro licenses.
    """


@license.command()
@click.argument("license_key", type=str)
def activate(license_key: str):
    """
    Activate Tekmera Pro license with your license key
    
    LICENSE_KEY: Your Pro license key (format: ABC-DEF-123)
    
    Unlocks all Pro features including cross-blueprint analysis,
    AI insights, and advanced governance checks.
    """
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
def local():
    """
    Show instructions for enabling local Pro mode
    
    Local Pro mode bypasses license validation for development
    and testing purposes. Set TEKMERA_LOCAL_PRO=true environment
    variable to enable.
    """
    console = Console()

    console.print("🛠️  [bold blue]Local Pro Mode[/bold blue]\n")
    console.print("To enable local pro mode, set the environment variable:")
    console.print("\n[bold green]export TEKMERA_LOCAL_PRO=true[/bold green]\n")
    console.print("This bypasses license validation for local development.")
    console.print("Add to your shell profile (.bashrc, .zshrc) to persist.")

    # Show current status
    import os

    if os.getenv("TEKMERA_LOCAL_PRO", "").lower() in ["true", "1", "yes", "on"]:
        console.print("\n✅ [green]Local pro mode is currently [bold]ENABLED[/bold][/green]")
    else:
        console.print("\n❌ [yellow]Local pro mode is currently [bold]DISABLED[/bold][/yellow]")


@license.command()
def deactivate():
    """
    Deactivate Pro license and revert to Free edition
    
    Removes stored license information and reverts to Free tier.
    You can reactivate anytime with 'tekmera license activate <key>'.
    """
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
    """
    Display current license status and feature availability
    
    Shows active license type (Free/Pro), expiration date,
    and which features are currently available.
    """
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
