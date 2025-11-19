"""
Configuration management for Tekmera Fusion Explorer
Handles storage and retrieval of user credentials and settings
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt


class ConfigManager:
    """Manages user configuration including license keys and API credentials"""

    def __init__(self):
        self.config_dir = Path.home() / ".tekmera"
        self.config_file = self.config_dir / "config.json"
        self.console = Console()
        self._ensure_config_dir()
        self._config_cache: Optional[Dict[str, Any]] = None

    def _ensure_config_dir(self) -> None:
        """Ensure the configuration directory exists"""
        self.config_dir.mkdir(exist_ok=True)
        # Set directory permissions to be readable only by owner
        self.config_dir.chmod(0o700)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file, with caching"""
        if self._config_cache is None:
            if self.config_file.exists():
                try:
                    with open(self.config_file, "r") as f:
                        self._config_cache = json.load(f)
                except (json.JSONDecodeError, IOError):
                    self._config_cache = {}
            else:
                self._config_cache = {}
        return self._config_cache

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
            # Set file permissions to be readable only by owner
            self.config_file.chmod(0o600)
            self._config_cache = config
        except IOError as e:
            self.console.print(f"[red]Error saving configuration: {e}[/red]")
            raise

    def get_license_key(self) -> Optional[str]:
        """Get stored license key"""
        config = self._load_config()
        return config.get("license_key")

    def get_openai_api_key(self) -> Optional[str]:
        """Get stored OpenAI API key"""
        config = self._load_config()
        # Check config file first, then environment variable
        api_key = config.get("openai_api_key")
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
        return api_key

    def set_license_key(self, license_key: str) -> None:
        """Store license key"""
        config = self._load_config()
        config["license_key"] = license_key
        self._save_config(config)

    def set_openai_api_key(self, api_key: str) -> None:
        """Store OpenAI API key"""
        config = self._load_config()
        config["openai_api_key"] = api_key
        self._save_config(config)

    def remove_license_key(self) -> None:
        """Remove stored license key"""
        config = self._load_config()
        config.pop("license_key", None)
        self._save_config(config)

    def remove_openai_api_key(self) -> None:
        """Remove stored OpenAI API key"""
        config = self._load_config()
        config.pop("openai_api_key", None)
        self._save_config(config)

    def get_config_status(self) -> Dict[str, bool]:
        """Get status of stored configuration"""
        config = self._load_config()
        return {
            "license_key_configured": bool(config.get("license_key")),
            "openai_api_key_configured": bool(self.get_openai_api_key()),
            "config_file_exists": self.config_file.exists(),
        }

    def interactive_setup(self) -> None:
        """Interactive setup wizard for configuration"""
        self.console.print("\n[bold blue]🔧 Tekmera Fusion Explorer - Initial Setup[/bold blue]\n")

        self.console.print(
            Panel(
                "This wizard will help you configure your license key and OpenAI API credentials.\n"
                "These will be securely stored in your home directory (~/.tekmera/config.json)",
                title="Welcome",
                border_style="blue",
            )
        )

        # License key setup
        self.console.print("\n[bold]License Configuration[/bold]")
        current_license = self.get_license_key()
        if current_license:
            self.console.print(
                f"[green]✓[/green] License key already configured: {current_license[:20]}..."
            )
            if Confirm.ask("Do you want to update your license key?", default=False):
                license_key = self._prompt_license_key()
                if license_key:
                    self.set_license_key(license_key)
                    self.console.print("[green]✓ License key updated successfully[/green]")
        else:
            self.console.print("[yellow]No license key configured[/yellow]")
            license_key = self._prompt_license_key()
            if license_key:
                self.set_license_key(license_key)
                self.console.print("[green]✓ License key saved successfully[/green]")

        # OpenAI API key setup
        self.console.print("\n[bold]OpenAI API Configuration[/bold]")
        current_api_key = self.get_openai_api_key()
        if current_api_key:
            self.console.print("[green]✓[/green] OpenAI API key already configured")
            if Confirm.ask("Do you want to update your OpenAI API key?", default=False):
                api_key = self._prompt_openai_key()
                if api_key:
                    self.set_openai_api_key(api_key)
                    self.console.print("[green]✓ OpenAI API key updated successfully[/green]")
        else:
            self.console.print("[yellow]No OpenAI API key configured[/yellow]")
            api_key = self._prompt_openai_key()
            if api_key:
                self.set_openai_api_key(api_key)
                self.console.print("[green]✓ OpenAI API key saved successfully[/green]")

        # Setup complete
        self.console.print(
            Panel(
                "[green]✓ Setup complete![/green]\n\n"
                "Your credentials have been securely stored. You can now:\n"
                "• Run 'tekmera analyze ./blueprints' to start analyzing blueprints\n"
                "• Use 'tekmera license status' to check your license\n"
                "• Run 'tekmera init' again to update your configuration",
                title="Setup Complete",
                border_style="green",
            )
        )

    def _prompt_license_key(self) -> Optional[str]:
        """Prompt user for license key with validation"""
        self.console.print("\nEnter your Tekmera Pro license key:")
        self.console.print("[dim]Format: TEKMERA-PRO-{edition}-{hash} (leave blank to skip)[/dim]")

        license_key = Prompt.ask("License Key", default="").strip()

        if not license_key:
            return None

        if not license_key.startswith("TEKMERA-PRO-"):
            self.console.print(
                "[yellow]⚠️  Warning: License key format doesn't look correct[/yellow]"
            )
            if not Confirm.ask("Continue anyway?", default=True):
                return None

        return license_key

    def _prompt_openai_key(self) -> Optional[str]:
        """Prompt user for OpenAI API key with validation"""
        self.console.print("\nEnter your OpenAI API key for AI features:")
        self.console.print(
            "[dim]Get your API key from: https://platform.openai.com/api-keys (leave blank to skip)[/dim]"
        )

        api_key = Prompt.ask("OpenAI API Key", password=True, default="").strip()

        if not api_key:
            return None

        if not api_key.startswith("sk-"):
            self.console.print(
                "[yellow]⚠️  Warning: OpenAI API key format doesn't look correct[/yellow]"
            )
            if not Confirm.ask("Continue anyway?", default=True):
                return None

        return api_key


# Global config manager instance
config_manager = ConfigManager()
