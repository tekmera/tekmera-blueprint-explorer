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
        """Show upgrade prompt for paid features - non-interactive safe."""
        if not console:
            console = Console()

        console.print(f"\n[yellow]🔒 Paid Feature Required[/yellow]")
        console.print(f"[bold]{feature_name}[/bold] requires a paid Tekmera license.")
        console.print("Upgrade to unlock AI features and advanced analysis capabilities.")
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

        if license_info["status"] == "active":
            license_type = (
                "Paid" if license_info.get("license_type") in ["evaluation", "premium"] else "Free"
            )
            console.print(f"Status: [green]✅ Active ({license_type})[/green]")
            console.print(f"License Key: {license_info['license_key']}")
            console.print(f"Issued To: {license_info['issued_to']}")
            console.print(f"Issued At: {license_info['issued_at']}")

            # Show validation status
            if license_info.get("local_mode", False):
                console.print(f"Validation: [yellow]🛠️  Local Development Mode[/yellow]")
            else:
                console.print(f"Validation: [green]✅ License Verified[/green]")

            if license_info.get("expiry"):
                days_remaining = license_info.get("days_remaining")
                if days_remaining is not None:
                    if days_remaining > 30:
                        console.print(
                            f"Expires: {license_info['expiry']} ({days_remaining} days remaining)"
                        )
                    elif days_remaining > 0:
                        console.print(
                            f"Expires: [yellow]{license_info['expiry']} ({days_remaining} days remaining)[/yellow]"
                        )
                    else:
                        console.print(f"Expires: [red]{license_info['expiry']} (EXPIRED)[/red]")
            else:
                console.print("Expires: [green]Never[/green]")

            console.print(f"\n🎯 Paid features are [green]enabled[/green]")

        else:
            console.print(f"Status: [yellow]Free[/yellow]")
            console.print("License Key: None")
            console.print("\n🔒 Paid features are [yellow]locked[/yellow]")
            console.print("\nTo unlock paid features:")
            console.print("1. Purchase a license at [link]https://tekmera.com/pricing[/link]")
            console.print(
                "2. Activate with: [bold]tekmera license activate YOUR-LICENSE-KEY[/bold]"
            )

    @staticmethod
    def show_license_activation_result(
        success: bool,
        message: str,
        license_info: Optional[dict] = None,
        console: Optional[Console] = None,
    ) -> None:
        """Display license activation results."""
        if not console:
            console = Console()

        console.print("🔑 [bold blue]Activating Tekmera License...[/bold blue]\n")

        if success:
            console.print(f"✅ [green]{message}[/green]")

            if license_info:
                console.print(f"\n📋 [bold]License Details:[/bold]")
                license_type = (
                    "Paid"
                    if license_info.get("license_type") in ["evaluation", "premium"]
                    else "Free"
                )
                console.print(f"  Type: {license_type}")
                console.print(f"  License Key: {license_info['license_key']}")
                console.print(f"  Issued To: {license_info['issued_to']}")

                # Show validation status
                if license_info.get("local_mode", False):
                    console.print(f"  Validation: [yellow]🛠️  Local Development Mode[/yellow]")
                else:
                    console.print(f"  Validation: [green]✅ License Verified[/green]")

                if license_info.get("expiry"):
                    days_remaining = license_info.get("days_remaining")
                    if days_remaining is not None:
                        if days_remaining > 30:
                            console.print(
                                f"  Expires: {license_info['expiry']} ({days_remaining} days remaining)"
                            )
                        elif days_remaining > 0:
                            console.print(
                                f"  Expires: [yellow]{license_info['expiry']} ({days_remaining} days remaining)[/yellow]"
                            )
                        else:
                            console.print(
                                f"  Expires: [red]{license_info['expiry']} (EXPIRED)[/red]"
                            )
                else:
                    console.print("  Expires: Never")

            console.print(f"\n🎉 [bold green]Paid features are now unlocked![/bold green]")
            console.print(
                "Use [bold]tekmera analyze /path/to/blueprints[/bold] to access paid features."
            )
        else:
            console.print(f"❌ [red]{message}[/red]")

    @staticmethod
    def show_license_deactivation_result(
        success: bool, message: str, console: Optional[Console] = None
    ) -> None:
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
            console.print("[red]⚠️  Your Tekmera license has expired![/red]")
            console.print("Paid features are now disabled. Please renew your license.")
        elif days_remaining <= 7:
            console.print(
                f"[yellow]⚠️  Your Tekmera license expires in {days_remaining} days![/yellow]"
            )
            console.print("Consider renewing to avoid interruption of paid features.")
        elif days_remaining <= 30:
            console.print(f"[dim]ℹ️  Your Tekmera license expires in {days_remaining} days.[/dim]")
