"""
Centralized search results display utility for consistent search result formatting
"""

import json
from typing import Dict, List

from InquirerPy import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table


class SearchResultsDisplay:
    """Centralized utility for displaying search results in a consistent format."""

    def __init__(self, console: Console = None):
        self.console = console or Console()

    def display_field_search_results(self, results: List[Dict], search_term: str) -> None:
        """
        Display field search results in a formatted table.

        Args:
            results: List of search results containing field matches
            search_term: The search term that was used
        """
        if not results:
            self.console.print(f"[yellow]No fields found matching '{search_term}'[/yellow]")
            return

        self.console.print(
            f"\n[bold green]Found {len(results)} field(s) matching '{search_term}':[/bold green]\n"
        )

        # Create results table
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Scenario", style="cyan", width=30)
        table.add_column("Module ID", style="yellow", width=10)
        table.add_column("Module Type", style="green", width=25)
        table.add_column("Field Context", style="white", width=40)

        for result in results:
            # Truncate long field contexts
            context = result.get("context", "")
            if len(context) > 37:
                context = context[:34] + "..."

            table.add_row(
                result.get("scenario_name", "Unknown"),
                str(result.get("module_id", "Unknown")),
                result.get("module_type", "Unknown"),
                context,
            )

        self.console.print(table)

        # Offer to show details
        if (
            self.console.input("\n[dim]Press Enter to continue or 'd' for detailed view: [/dim]")
            .strip()
            .lower()
            == "d"
        ):
            self._show_detailed_field_results(results, search_term)

    def display_module_search_results(self, results: List[Dict], search_term: str) -> None:
        """
        Display module search results in a formatted table.

        Args:
            results: List of module search results
            search_term: The search term that was used
        """
        if not results:
            self.console.print(f"[yellow]No modules found matching '{search_term}'[/yellow]")
            return

        self.console.print(
            f"\n[bold green]Found {len(results)} module(s) matching '{search_term}':[/bold green]\n"
        )

        # Create results table
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Scenario", style="cyan", width=30)
        table.add_column("Module ID", style="yellow", width=10)
        table.add_column("Module Type", style="green", width=30)
        table.add_column("Label", style="white", width=25)

        for result in results:
            # Truncate long labels
            label = result.get("label", "")
            if len(label) > 22:
                label = label[:19] + "..."

            table.add_row(
                result.get("scenario_name", "Unknown"),
                str(result.get("module_id", "Unknown")),
                result.get("module_type", "Unknown"),
                label,
            )

        self.console.print(table)

        # Offer to show details
        if (
            self.console.input("\n[dim]Press Enter to continue or 'd' for detailed view: [/dim]")
            .strip()
            .lower()
            == "d"
        ):
            self._show_detailed_module_results(results, search_term)

    def display_text_search_results(
        self, results: List[Dict], search_term: str, results_per_page: int = 20
    ) -> None:
        """
        Display text search results with pagination.

        Args:
            results: List of text search results
            search_term: The search term that was used
            results_per_page: Number of results to show per page
        """
        if not results:
            self.console.print(f"[yellow]No text found matching '{search_term}'[/yellow]")
            return

        self.console.print(
            f"\n[bold green]Found {len(results)} text match(es) for '{search_term}':[/bold green]"
        )

        # Paginate results
        self._paginate_text_results(results, search_term, results_per_page)

    def _show_detailed_field_results(self, results: List[Dict], search_term: str) -> None:
        """Show detailed view of field search results."""
        self.console.print(f"\n[bold]Detailed Field Results for '{search_term}':[/bold]\n")

        for i, result in enumerate(results, 1):
            panel_content = []
            panel_content.append(f"[cyan]Scenario:[/cyan] {result.get('scenario_name', 'Unknown')}")
            panel_content.append(
                f"[yellow]Module ID:[/yellow] {result.get('module_id', 'Unknown')}"
            )
            panel_content.append(
                f"[green]Module Type:[/green] {result.get('module_type', 'Unknown')}"
            )
            panel_content.append(f"[white]Field Context:[/white] {result.get('context', '')}")

            if result.get("field_path"):
                panel_content.append(f"[dim]Field Path:[/dim] {result.get('field_path')}")

            content = "\n".join(panel_content)

            panel = Panel(content, title=f"Result {i}/{len(results)}", border_style="blue")
            self.console.print(panel)
            self.console.print()

            # Pagination for many results
            if i % 5 == 0 and i < len(results):
                if not inquirer.confirm(
                    message="Continue to next results?", default=True
                ).execute():
                    break

    def _show_detailed_module_results(self, results: List[Dict], search_term: str) -> None:
        """Show detailed view of module search results."""
        self.console.print(f"\n[bold]Detailed Module Results for '{search_term}':[/bold]\n")

        for i, result in enumerate(results, 1):
            panel_content = []
            panel_content.append(f"[cyan]Scenario:[/cyan] {result.get('scenario_name', 'Unknown')}")
            panel_content.append(
                f"[yellow]Module ID:[/yellow] {result.get('module_id', 'Unknown')}"
            )
            panel_content.append(
                f"[green]Module Type:[/green] {result.get('module_type', 'Unknown')}"
            )
            panel_content.append(f"[white]Label:[/white] {result.get('label', '')}")

            # Show parameters if available
            if result.get("module_data", {}).get("parameters"):
                parameters = json.dumps(result["module_data"]["parameters"], indent=2)
                if len(parameters) < 500:  # Only show if reasonable size
                    panel_content.append(f"[dim]Parameters Preview:[/dim]")
                    syntax = Syntax(parameters, "json", theme="monokai", line_numbers=False)
                    panel_content.append(str(syntax))

            content = "\n".join(panel_content)

            panel = Panel(content, title=f"Module {i}/{len(results)}", border_style="green")
            self.console.print(panel)
            self.console.print()

            # Pagination for many results
            if i % 3 == 0 and i < len(results):
                if not inquirer.confirm(
                    message="Continue to next results?", default=True
                ).execute():
                    break

    def _paginate_text_results(
        self, results: List[Dict], search_term: str, results_per_page: int
    ) -> None:
        """Paginate and display text search results."""
        total_pages = (len(results) - 1) // results_per_page + 1
        current_page = 0

        while current_page < total_pages:
            self._show_text_results_page(
                results, search_term, current_page, results_per_page, total_pages
            )

            if current_page < total_pages - 1:
                choices = [
                    {"name": "➡️  Next page", "value": "next"},
                    {"name": "⬅️  Previous page", "value": "prev"} if current_page > 0 else None,
                    {"name": "🦘 Jump to page", "value": "jump"},
                    {"name": "❌ Done viewing results", "value": "done"},
                ]
                choices = [choice for choice in choices if choice is not None]

                action = inquirer.select(message="Navigation options:", choices=choices).execute()

                if action == "next":
                    current_page += 1
                elif action == "prev" and current_page > 0:
                    current_page -= 1
                elif action == "jump":
                    page_num = inquirer.number(
                        message=f"Enter page number (1-{total_pages}):",
                        min_allowed=1,
                        max_allowed=total_pages,
                    ).execute()
                    if page_num:
                        current_page = page_num - 1
                elif action == "done":
                    break
            else:
                break

    def _show_text_results_page(
        self,
        results: List[Dict],
        search_term: str,
        current_page: int,
        results_per_page: int,
        total_pages: int,
    ) -> None:
        """Display a single page of text search results."""
        start_idx = current_page * results_per_page
        end_idx = min(start_idx + results_per_page, len(results))
        page_results = results[start_idx:end_idx]

        self.console.print(
            f"\n[bold]Page {current_page + 1} of {total_pages}[/bold] "
            f"(Results {start_idx + 1}-{end_idx} of {len(results)})\n"
        )

        for i, result in enumerate(page_results, start_idx + 1):
            panel_content = []
            panel_content.append(f"[cyan]Scenario:[/cyan] {result.get('scenario_name', 'Unknown')}")
            panel_content.append(
                f"[yellow]Module ID:[/yellow] {result.get('module_id', 'Unknown')}"
            )
            panel_content.append(
                f"[green]Module Type:[/green] {result.get('module_type', 'Unknown')}"
            )

            # Show context with highlighting
            context = result.get("context", "")
            if context and search_term:
                # Simple highlighting - replace with bold/yellow
                highlighted = context.replace(
                    search_term, f"[bold yellow]{search_term}[/bold yellow]"
                )
                panel_content.append(f"[white]Context:[/white] {highlighted}")

            content = "\n".join(panel_content)

            panel = Panel(content, title=f"Match {i}", border_style="yellow")
            self.console.print(panel)
            self.console.print()

    def display_search_summary(
        self, field_count: int, module_count: int, text_count: int, search_term: str
    ) -> None:
        """
        Display a summary of all search results.

        Args:
            field_count: Number of field matches
            module_count: Number of module matches
            text_count: Number of text matches
            search_term: The search term that was used
        """
        total = field_count + module_count + text_count

        if total == 0:
            self.console.print(f"[yellow]No results found for '{search_term}'[/yellow]")
            return

        self.console.print(f"\n[bold green]Search Summary for '{search_term}':[/bold green]")
        self.console.print(f"  • [cyan]{field_count}[/cyan] field matches")
        self.console.print(f"  • [green]{module_count}[/green] module matches")
        self.console.print(f"  • [yellow]{text_count}[/yellow] text matches")
        self.console.print(f"  • [bold]{total}[/bold] total matches\n")
