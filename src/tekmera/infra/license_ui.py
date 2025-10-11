"""
User interface utilities for license management.
Separated from core license logic for better separation of concerns.
"""
import sys
from typing import Optional
from rich.console import Console


class LicenseUI:
    """Handles all user interface aspects of license management."""
    
    @staticmethod
    def show_premium_prompt(feature_name: str, console: Optional[Console] = None) -> bool:
        """Show upgrade prompt for premium features - non-interactive safe."""
        if not console:
            console = Console()
            
        console.print(f"\n[yellow]🔒 Premium Feature Required[/yellow]")
        console.print(f"[bold]{feature_name}[/bold] requires Tekmera Pro.")
        console.print("Upgrade to unlock advanced governance intelligence and AI features.")
        console.print("\n[dim]Press Enter to continue...[/dim]")
        
        # Guard for TTY and handle EOFError gracefully
        if sys.stdin.isatty():
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                pass  # Handle non-interactive environments gracefully
        
        return False  # Always return False since this is a blocking prompt
    
    @staticmethod
    def show_license_status(license_info: dict, console: Optional[Console] = None) -> None:
        """Display formatted license status information."""
        if not console:
            console = Console()
            
        console.print("📄 [bold blue]Tekmera License Status[/bold blue]\n")
        
        if license_info['status'] == 'active':
            console.print(f"Status: [green]✅ Active ({license_info['edition']} Edition)[/green]")
            console.print(f"License Key: {license_info['license_key']}")
            console.print(f"Issued To: {license_info['issued_to']}")
            console.print(f"Issued At: {license_info['issued_at']}")
            
            # Lemon Squeezy licenses are always verified online
            console.print(f"Validation: [green]✅ Lemon Squeezy Verified[/green]")
            
            if license_info.get('expiry'):
                days_remaining = license_info.get('days_remaining')
                if days_remaining is not None:
                    if days_remaining > 30:
                        console.print(f"Expires: {license_info['expiry']} ({days_remaining} days remaining)")
                    elif days_remaining > 0:
                        console.print(f"Expires: [yellow]{license_info['expiry']} ({days_remaining} days remaining)[/yellow]")
                    else:
                        console.print(f"Expires: [red]{license_info['expiry']} (EXPIRED)[/red]")
            else:
                console.print("Expires: [green]Never[/green]")
                
            console.print(f"\n🎯 Premium features are [green]enabled[/green]")
            
        else:
            console.print(f"Status: [yellow]Free Edition[/yellow]")
            console.print("License Key: None")
            console.print("\n🔒 Premium features are [yellow]locked[/yellow]")
            console.print("\nTo unlock premium features:")
            console.print("1. Purchase a license at [link]https://tekmera.com/pricing[/link]")
            console.print("2. Activate with: [bold]tekmera license activate YOUR-LICENSE-KEY[/bold]")
    
    @staticmethod
    def show_license_activation_result(success: bool, message: str, 
                                     license_info: Optional[dict] = None,
                                     console: Optional[Console] = None) -> None:
        """Display license activation results."""
        if not console:
            console = Console()
            
        console.print("🔑 [bold blue]Activating Tekmera Pro License...[/bold blue]\n")
        
        if success:
            console.print(f"✅ [green]{message}[/green]")
            
            if license_info:
                console.print(f"\n📋 [bold]License Details:[/bold]")
                console.print(f"  Edition: {license_info['edition']}")
                console.print(f"  License Key: {license_info['license_key']}")
                console.print(f"  Issued To: {license_info['issued_to']}")
                
                # Lemon Squeezy licenses are validated online
                console.print(f"  Validation: [green]✅ Lemon Squeezy Verified[/green]")
                
                if license_info.get('expiry'):
                    days_remaining = license_info.get('days_remaining')
                    if days_remaining is not None:
                        if days_remaining > 30:
                            console.print(f"  Expires: {license_info['expiry']} ({days_remaining} days remaining)")
                        elif days_remaining > 0:
                            console.print(f"  Expires: [yellow]{license_info['expiry']} ({days_remaining} days remaining)[/yellow]")
                        else:
                            console.print(f"  Expires: [red]{license_info['expiry']} (EXPIRED)[/red]")
                else:
                    console.print("  Expires: Never")
            
            console.print(f"\n🎉 [bold green]Pro features are now unlocked![/bold green]")
            console.print("Use [bold]tekmera analyze /path/to/blueprints[/bold] to access premium features.")
        else:
            console.print(f"❌ [red]{message}[/red]")
    
    @staticmethod
    def show_license_deactivation_result(success: bool, message: str,
                                       console: Optional[Console] = None) -> None:
        """Display license deactivation results."""
        if not console:
            console = Console()
            
        console.print("🔓 [bold yellow]Deactivating license...[/bold yellow]")
        
        if success:
            console.print(f"✅ [green]{message}[/green]")
            console.print("Tekmera Fusion Explorer is now running in Free mode.")
        else:
            console.print(f"❌ [red]{message}[/red]")
    
    @staticmethod
    def show_expiry_warning(days_remaining: int, console: Optional[Console] = None) -> None:
        """Show license expiry warning."""
        if not console:
            console = Console()
            
        if days_remaining <= 0:
            console.print("[red]⚠️  Your Tekmera Pro license has expired![/red]")
            console.print("Premium features are now disabled. Please renew your license.")
        elif days_remaining <= 7:
            console.print(f"[yellow]⚠️  Your Tekmera Pro license expires in {days_remaining} days![/yellow]")
            console.print("Consider renewing to avoid interruption of premium features.")
        elif days_remaining <= 30:
            console.print(f"[dim]ℹ️  Your Tekmera Pro license expires in {days_remaining} days.[/dim]")