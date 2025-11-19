"""
Base CLI class for common initialization and utilities across all CLI interfaces
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from rich.console import Console

from ..core.analyzer import BlueprintAnalyzer
from ..core.parser import BlueprintParser
from .blueprint_loader import BlueprintLoader
from .search_display import SearchResultsDisplay


class BaseCLI(ABC):
    """
    Abstract base class for all CLI interfaces providing common functionality.

    Standardizes initialization of common components like console, parsers,
    analyzers, and utilities to reduce boilerplate code across CLI classes.
    """

    def __init__(self, enable_search_display: bool = True):
        """
        Initialize common CLI components.

        Args:
            enable_search_display: Whether to initialize SearchResultsDisplay utility
        """
        # Core components used by all CLI interfaces
        self.console = Console()
        self.parser = BlueprintParser()
        self.analyzer = BlueprintAnalyzer()
        self.blueprint_loader = BlueprintLoader(self.console)

        # Optional components
        if enable_search_display:
            self.search_display = SearchResultsDisplay(self.console)
        else:
            self.search_display = None

        # Common state
        self.blueprints = {}
        self.loaded = False

    @abstractmethod
    def start(self, directory: Path, **kwargs) -> None:
        """
        Start the CLI interface. Must be implemented by subclasses.

        Args:
            directory: Directory containing blueprint files
            **kwargs: Additional interface-specific arguments
        """

    def load_blueprints(self, directory: Path, include_modules: bool = True) -> None:
        """
        Load blueprint files using the standardized loader.

        Args:
            directory: Directory to search for blueprint files
            include_modules: Whether to parse and include module information
        """
        self.blueprints = self.blueprint_loader.load_blueprints(
            directory=directory, include_modules=include_modules
        )
        self.loaded = True

    def get_blueprint_summary(self) -> dict:
        """
        Get a summary of loaded blueprints.

        Returns:
            Dictionary with blueprint statistics
        """
        if not self.loaded:
            return {"total": 0, "message": "No blueprints loaded"}

        return {
            "total": len(self.blueprints),
            "scenarios": [bp["scenario_name"] for bp in self.blueprints.values()],
            "total_modules": sum(bp.get("module_count", 0) for bp in self.blueprints.values()),
            "message": f"Loaded {len(self.blueprints)} blueprints successfully",
        }

    def display_welcome(self, title: str, subtitle: Optional[str] = None) -> None:
        """
        Display a standardized welcome message.

        Args:
            title: Main title for the interface
            subtitle: Optional subtitle with additional information
        """
        self.console.print(f"\n🔧 [bold blue]{title}[/bold blue]")
        if subtitle:
            self.console.print(f"[dim]{subtitle}[/dim]")
        self.console.print()

    def confirm_exit(self, message: str = "Are you sure you want to exit?") -> bool:
        """
        Standardized exit confirmation.

        Args:
            message: Confirmation message to display

        Returns:
            True if user confirms exit, False otherwise
        """
        from InquirerPy import inquirer

        return inquirer.confirm(message=message, default=False).execute()

    def show_error(self, message: str, details: Optional[str] = None) -> None:
        """
        Display standardized error messages.

        Args:
            message: Error message to display
            details: Optional additional error details
        """
        self.console.print(f"[red]Error: {message}[/red]")
        if details:
            self.console.print(f"[dim]{details}[/dim]")

    def show_success(self, message: str) -> None:
        """
        Display standardized success messages.

        Args:
            message: Success message to display
        """
        self.console.print(f"[green]✅ {message}[/green]")

    def show_warning(self, message: str) -> None:
        """
        Display standardized warning messages.

        Args:
            message: Warning message to display
        """
        self.console.print(f"[yellow]⚠️ {message}[/yellow]")

    def wait_for_input(self, message: str = "Press Enter to continue...") -> None:
        """
        Standardized pause for user input.

        Args:
            message: Message to display while waiting
        """
        self.console.input(f"\n[dim]{message}[/dim]")

    def clear_screen(self) -> None:
        """Clear the console screen."""
        self.console.clear()

    def print_separator(self, char: str = "─", length: int = 80) -> None:
        """
        Print a visual separator line.

        Args:
            char: Character to use for the separator
            length: Length of the separator line
        """
        self.console.print(f"[dim]{char * length}[/dim]")


class InteractiveCLIBase(BaseCLI):
    """
    Base class for interactive CLI interfaces with menu systems.

    Extends BaseCLI with interactive menu functionality and navigation patterns.
    """

    def __init__(self, enable_search_display: bool = True):
        super().__init__(enable_search_display)
        self.current_menu = "main"
        self.menu_history = []

    def show_menu_header(self, title: str, blueprint_count: Optional[int] = None) -> None:
        """
        Display a standardized menu header.

        Args:
            title: Menu title
            blueprint_count: Optional count of loaded blueprints to display
        """
        self.console.print(f"\n[bold cyan]═══ {title} ═══[/bold cyan]")
        if blueprint_count is not None:
            self.console.print(f"[dim]({blueprint_count} blueprints loaded)[/dim]")
        self.console.print()

    def navigate_to_menu(self, menu_name: str) -> None:
        """
        Navigate to a different menu, maintaining history.

        Args:
            menu_name: Name of the menu to navigate to
        """
        if self.current_menu != menu_name:
            self.menu_history.append(self.current_menu)
            self.current_menu = menu_name

    def go_back(self) -> bool:
        """
        Navigate back to the previous menu.

        Returns:
            True if navigation was possible, False if at root
        """
        if self.menu_history:
            self.current_menu = self.menu_history.pop()
            return True
        return False

    def get_back_choice(self) -> dict:
        """
        Get a standardized "back" menu choice.

        Returns:
            Dictionary representing a back navigation choice
        """
        return {"name": "← Back", "value": "back"}

    def get_quit_choice(self) -> dict:
        """
        Get a standardized "quit" menu choice.

        Returns:
            Dictionary representing a quit choice
        """
        return {"name": "❌ Quit", "value": "quit"}

    def handle_keyboard_interrupt(self) -> None:
        """Handle Ctrl+C interruption gracefully."""
        self.console.print("\n[yellow]Operation cancelled. Goodbye![/yellow]")
