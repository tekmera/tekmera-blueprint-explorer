#!/usr/bin/env python3
"""
Main CLI entry point for Tekmera Fusion Explorer
"""
import click
from pathlib import Path
from rich.console import Console

from .interactive import InteractiveCLI
from ...infra.license import license_manager


@click.group()
@click.version_option(version='0.1.0', prog_name='tekmera-fusion-explorer')
@click.pass_context
def cli(ctx):
    """
    Tekmera Fusion Explorer - Diagnostic CLI for Fusion blueprints
    
    Analyze exported Workfront Fusion blueprint JSON files with interactive
    exploration, governance auditing, and AI-powered insights.
    """
    ctx.ensure_object(dict)


@cli.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def analyze(directory: str):
    """
    Analyze blueprint directory with interactive exploration
    
    DIRECTORY: Path to directory containing blueprint JSON files
    """
    directory_path = Path(directory)
    
    # Launch interactive CLI - license auto-detected from ~/.tekmera/license.json
    cli_instance = InteractiveCLI()
    cli_instance.start(directory_path)


@cli.group()
def license():
    """Manage Tekmera Pro licenses"""
    pass


@license.command()
@click.option('--file', 'license_file', required=True, 
              type=click.Path(exists=True, file_okay=True, dir_okay=False),
              help='Path to license.json file')
def activate(license_file: str):
    """Activate a Tekmera Pro license from file"""
    console = Console()
    
    console.print("🔑 [bold blue]Activating Tekmera Pro License...[/bold blue]\n")
    
    license_path = Path(license_file)
    success, message = license_manager.activate_license(license_path)
    
    if success:
        console.print(f"✅ [green]{message}[/green]")
        
        # Show license info
        info = license_manager.get_license_info()
        console.print(f"\n📋 [bold]License Details:[/bold]")
        console.print(f"  Edition: {info['edition']}")
        console.print(f"  License Key: {info['license_key']}")
        console.print(f"  Issued To: {info['issued_to']}")
        if info.get('expiry'):
            if info.get('days_remaining') is not None:
                days = info['days_remaining']
                if days > 30:
                    console.print(f"  Expires: {info['expiry']} ({days} days remaining)")
                elif days > 0:
                    console.print(f"  Expires: [yellow]{info['expiry']} ({days} days remaining)[/yellow]")
                else:
                    console.print(f"  Expires: [red]{info['expiry']} (EXPIRED)[/red]")
        else:
            console.print("  Expires: Never")
        
        console.print(f"\n🎉 [bold green]Pro features are now unlocked![/bold green]")
        console.print("Use [bold]tekmera analyze --premium /path/to/blueprints[/bold] to access premium features.")
    else:
        console.print(f"❌ [red]{message}[/red]")
        return 1


@license.command()
def deactivate():
    """Deactivate current license (revert to free edition)"""
    console = Console()
    
    info = license_manager.get_license_info()
    if info['status'] == 'free':
        console.print("ℹ️  [yellow]No active license to deactivate[/yellow]")
        return
    
    console.print("🔓 [bold yellow]Deactivating license...[/bold yellow]")
    
    success, message = license_manager.deactivate_license()
    
    if success:
        console.print(f"✅ [green]{message}[/green]")
        console.print("Tekmera Fusion Explorer is now running in Free mode.")
    else:
        console.print(f"❌ [red]{message}[/red]")
        return 1


@license.command()
def status():
    """Show current license status"""
    console = Console()
    
    info = license_manager.get_license_info()
    
    console.print("📄 [bold blue]Tekmera License Status[/bold blue]\n")
    
    if info['status'] == 'active':
        console.print(f"Status: [green]✅ Active ({info['edition']} Edition)[/green]")
        console.print(f"License Key: {info['license_key']}")
        console.print(f"Issued To: {info['issued_to']}")
        console.print(f"Issued At: {info['issued_at']}")
        
        if info.get('expiry'):
            if info.get('days_remaining') is not None:
                days = info['days_remaining']
                if days > 30:
                    console.print(f"Expires: {info['expiry']} ({days} days remaining)")
                elif days > 0:
                    console.print(f"Expires: [yellow]{info['expiry']} ({days} days remaining)[/yellow]")
                else:
                    console.print(f"Expires: [red]{info['expiry']} (EXPIRED)[/red]")
        else:
            console.print("Expires: [green]Never[/green]")
            
        console.print(f"\n🎯 Premium features are [green]enabled[/green]")
        
    else:
        console.print(f"Status: [yellow]Free Edition[/yellow]")
        console.print("License Key: None")
        console.print("\n🔒 Premium features are [yellow]locked[/yellow]")
        console.print("\nTo unlock premium features:")
        console.print("1. Purchase a license at [link]https://tekmera.com/pricing[/link]")
        console.print("2. Activate with: [bold]tekmera license activate --file license.json[/bold]")


# Main entry point - for backward compatibility, if called with directory argument
# it will run the analyze command
def main():
    """Main entry point with backward compatibility"""
    import sys
    
    # Check if called with directory argument (backward compatibility)
    if len(sys.argv) >= 2 and not sys.argv[1].startswith('-') and sys.argv[1] not in ['license', 'analyze']:
        # Insert 'analyze' command for backward compatibility
        sys.argv.insert(1, 'analyze')
    
    cli()


if __name__ == '__main__':
    main()