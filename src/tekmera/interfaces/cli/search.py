"""
Interactive search interface for cross-blueprint analysis
"""

from pathlib import Path
from typing import Any, Dict, List

from InquirerPy import inquirer
from InquirerPy.separator import Separator
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from ...analysis.connections import (
    classify_connection_environment,
    display_connection_summary,
    display_connection_table,
    display_connection_warnings,
)
from ...analysis.corpus_analyzer import CorpusAnalyzer


class SearchInterface:
    """Interactive search interface for cross-blueprint analysis."""

    def __init__(self):
        self.console = Console()
        self.analyzer = CorpusAnalyzer()
        self.loaded = False

    def start(self, directory: Path):
        """Start the interactive search session."""
        self.console.print("\n🔍 [bold blue]Cross-Blueprint Search & Analysis[/bold blue]")
        self.console.print("Search and analyze patterns across all Fusion blueprints.\n")

        # Load corpus
        with self.console.status("[bold green]Loading blueprints..."):
            self.analyzer.load_corpus(directory)

        stats = self.analyzer.get_corpus_stats()
        self.console.print(
            f"✅ Loaded {stats['total_blueprints']} blueprints with {stats['total_modules']} total modules\n"
        )

        self.loaded = True

        # Main search loop
        while True:
            try:
                action = self._main_menu()
                if action == "quit":
                    break
                elif action == "field_search":
                    self._field_search()
                elif action == "module_search":
                    self._module_type_search()
                elif action == "text_search":
                    self._text_search()
                elif action == "field_rankings":
                    self._show_field_rankings()
                elif action == "module_rankings":
                    self._show_module_rankings()
                elif action == "inconsistent_fields":
                    self._show_inconsistent_fields()
                elif action == "connections":
                    self._show_connections()
                elif action == "corpus_stats":
                    self._show_corpus_stats()
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Goodbye![/yellow]")
                break

    def _main_menu(self) -> str:
        """Display main search menu."""
        choices = [
            {"name": "🔎 Search for Workfront field (DE:)", "value": "field_search"},
            {"name": "🔎 Search for module type", "value": "module_search"},
            {"name": "🔎 Search for text/string", "value": "text_search"},
            Separator(),
            {"name": "📊 Field usage rankings", "value": "field_rankings"},
            {"name": "📈 Module type usage", "value": "module_rankings"},
            {"name": "⚠️  Detect inconsistent field naming", "value": "inconsistent_fields"},
            {"name": "🔗 Analyze connections", "value": "connections"},
            Separator(),
            {"name": "📋 Show corpus statistics", "value": "corpus_stats"},
            {"name": "❌ Quit", "value": "quit"},
        ]

        return inquirer.select(message="What would you like to do?", choices=choices).execute()

    def _field_search(self):
        """Interactive Workfront field search."""
        field_pattern = inquirer.text(
            message="Enter field to search for (e.g., 'DE:client_id' or just 'client'):"
        ).execute()

        if not field_pattern:
            return

        exact_match = inquirer.confirm(message="Require exact match?", default=False).execute()

        matches = self.analyzer.search_de_fields(field_pattern, exact_match)

        if not matches:
            self.console.print(f"[red]No matches found for '{field_pattern}'[/red]")
            input("\nPress Enter to continue...")
            return

        self._display_field_search_results(field_pattern, matches, exact_match)

    def _module_type_search(self):
        """Interactive module type search."""
        type_pattern = inquirer.text(
            message="Enter module type to search for (e.g., 'workfront' or 'workfront-workfront:searchv3'):"
        ).execute()

        if not type_pattern:
            return

        exact_match = inquirer.confirm(message="Require exact match?", default=False).execute()

        matches = self.analyzer.search_module_types(type_pattern, exact_match)

        if not matches:
            self.console.print(f"[red]No matches found for '{type_pattern}'[/red]")
            input("\nPress Enter to continue...")
            return

        self._display_module_search_results(type_pattern, matches, exact_match)

    def _text_search(self):
        """Interactive text search."""
        search_text = inquirer.text(message="Enter text to search for:").execute()

        if not search_text:
            return

        case_sensitive = inquirer.confirm(message="Case sensitive search?", default=False).execute()

        matches = self.analyzer.search_text(search_text, case_sensitive)

        if not matches:
            self.console.print(f"[red]No matches found for '{search_text}'[/red]")
            input("\nPress Enter to continue...")
            return

        self._display_text_search_results(search_text, matches, case_sensitive)

    def _show_field_rankings(self):
        """Show DE field usage rankings."""
        rankings = self.analyzer.get_de_field_rankings()

        if not rankings:
            self.console.print("[yellow]No DE fields found.[/yellow]")
            input("\nPress Enter to continue...")
            return

        # Show top fields in a table
        table = Table(title="Workfront Field Usage Rankings")
        table.add_column("Rank", style="cyan", width=6)
        table.add_column("Field", style="green")
        table.add_column("Count", style="yellow", justify="right")
        table.add_column("Scenarios", style="dim")

        for i, (field, count, usages) in enumerate(rankings[:20], 1):
            scenarios = list(set(usage["scenario_name"] for usage in usages))
            scenario_text = ", ".join(scenarios[:3])
            if len(scenarios) > 3:
                scenario_text += f" (+{len(scenarios)-3} more)"

            table.add_row(str(i), field, str(count), scenario_text)

        self.console.print("\n")
        self.console.print(table)

        if len(rankings) > 20:
            self.console.print(f"\n[dim]Showing top 20 of {len(rankings)} total fields[/dim]")

        input("\nPress Enter to continue...")

    def _show_module_rankings(self):
        """Show module type usage rankings."""
        rankings = self.analyzer.get_module_type_rankings()

        if not rankings:
            self.console.print("[yellow]No modules found.[/yellow]")
            input("\nPress Enter to continue...")
            return

        table = Table(title="Module Type Usage Rankings")
        table.add_column("Rank", style="cyan", width=6)
        table.add_column("Module Type", style="green")
        table.add_column("Count", style="yellow", justify="right")
        table.add_column("Scenarios", style="dim")

        for i, (module_type, count, usages) in enumerate(rankings[:15], 1):
            scenarios = list(set(usage["scenario_name"] for usage in usages))
            scenario_text = ", ".join(scenarios[:2])
            if len(scenarios) > 2:
                scenario_text += f" (+{len(scenarios)-2} more)"

            table.add_row(str(i), module_type, str(count), scenario_text)

        self.console.print("\n")
        self.console.print(table)

        if len(rankings) > 15:
            self.console.print(f"\n[dim]Showing top 15 of {len(rankings)} total types[/dim]")

        input("\nPress Enter to continue...")

    def _show_inconsistent_fields(self):
        """Show inconsistent field naming analysis."""
        threshold = inquirer.select(
            message="Select similarity threshold:",
            choices=[
                {"name": "High (0.9) - Very similar only", "value": 0.9},
                {"name": "Medium (0.8) - Moderately similar", "value": 0.8},
                {"name": "Low (0.7) - Broadly similar", "value": 0.7},
                {"name": "← Go back", "value": "back"},
            ],
        ).execute()

        if threshold == "back":
            return

        with self.console.status("[bold green]Analyzing field naming patterns..."):
            inconsistencies = self.analyzer.detect_inconsistent_field_naming(threshold)

        if not inconsistencies:
            self.console.print(
                f"[green]No inconsistent field naming detected at threshold {threshold}[/green]"
            )
            input("\nPress Enter to continue...")
            return

        self.console.print(
            f"\n[bold red]⚠️  Found {len(inconsistencies)} potential field naming inconsistencies:[/bold red]\n"
        )

        for i, inconsistency in enumerate(inconsistencies, 1):
            panel_content = f"[bold]{inconsistency['base_field']}[/bold]\n"
            panel_content += "Similar variations:\n"

            for j, variation in enumerate(inconsistency["variations"]):
                similarity = inconsistency["similarity_scores"][j]
                panel_content += f"  • {variation} [dim](similarity: {similarity:.2f})[/dim]\n"

            panel = Panel(panel_content, title=f"Group {i}", expand=False)
            self.console.print(panel)

        input("\nPress Enter to continue...")

    def _show_connections(self):
        """Show connection analysis with environment warnings."""
        with self.console.status("[bold green]Analyzing connections..."):
            analysis_result = self.analyzer.analyze_connections()

        connections = analysis_result.get("connections", {})
        warnings = analysis_result.get("warnings", [])
        connection_types = analysis_result.get("connection_types", {})
        connection_labels = analysis_result.get("connection_labels", {})

        if not connections:
            self.console.print("[yellow]No connections found.[/yellow]")
            input("\nPress Enter to continue...")
            return

        # Add environment classification to connection data
        for conn_id, usages in connections.items():
            connection_label = connection_labels.get(
                int(conn_id) if str(conn_id).isdigit() else conn_id, f"Connection {conn_id}"
            )
            environment = classify_connection_environment(connection_label)

            for usage in usages:
                usage["environment"] = environment

        # Display warnings using shared utility
        display_connection_warnings(self.console, warnings)

        # Display connection usage table using shared utility
        display_connection_table(
            console=self.console,
            connections=connections,
            connection_labels=connection_labels,
            title="Connection Usage Analysis",
            show_labels=True,
            show_environment=True,
        )

        # Show summary of connection types using shared utility
        display_connection_summary(self.console, connection_types)

        input("\nPress Enter to continue...")

    def _show_corpus_stats(self):
        """Show overall corpus statistics."""
        stats = self.analyzer.get_corpus_stats()

        content = f"""[bold]Corpus Overview[/bold]

📊 [cyan]Total Blueprints:[/cyan] {stats['total_blueprints']}
🔧 [cyan]Total Modules:[/cyan] {stats['total_modules']}
📋 [cyan]Unique Module Types:[/cyan] {stats['unique_module_types']}
🏷️  [cyan]Unique DE Fields:[/cyan] {stats['unique_de_fields']}

[bold]Scenarios:[/bold]"""

        for scenario in stats["scenarios"]:
            content += f"\n  • {scenario['scenario_name']} ({scenario['filename']}.json) - {scenario['module_count']} modules"

        panel = Panel(content, title="📊 Corpus Statistics", expand=False)
        self.console.print("\n")
        self.console.print(panel)
        input("\nPress Enter to continue...")

    def _display_field_search_results(self, pattern: str, matches: List[Dict], exact: bool):
        """Display field search results."""
        match_type = "exact" if exact else "partial"
        self.console.print(
            f"\n[bold green]Found {len(matches)} {match_type} matches for '{pattern}':[/bold green]\n"
        )

        # Group by field name
        by_field = {}
        for match in matches:
            field = match["field"]
            if field not in by_field:
                by_field[field] = []
            by_field[field].append(match)

        for field, field_matches in by_field.items():
            table = Table(title=f"Field: {field} ({len(field_matches)} usages)")
            table.add_column("Scenario", style="green")
            table.add_column("Module Type", style="cyan")
            table.add_column("Module ID", style="yellow")

            for match in field_matches:
                table.add_row(match["scenario_name"], match["module_type"], str(match["module_id"]))

            self.console.print(table)
            self.console.print()

        input("Press Enter to continue...")

    def _display_module_search_results(self, pattern: str, matches: List[Dict], exact: bool):
        """Display module type search results."""
        match_type = "exact" if exact else "partial"
        self.console.print(
            f"\n[bold green]Found {len(matches)} {match_type} matches for '{pattern}':[/bold green]\n"
        )

        # Group by module type
        by_type = {}
        for match in matches:
            module_type = match["module_type"]
            if module_type not in by_type:
                by_type[module_type] = []
            by_type[module_type].append(match)

        for module_type, type_matches in by_type.items():
            table = Table(title=f"Module Type: {module_type} ({len(type_matches)} instances)")
            table.add_column("Scenario", style="green")
            table.add_column("Module ID", style="yellow")
            table.add_column("Blueprint File", style="dim")

            for match in type_matches:
                table.add_row(
                    match["scenario_name"], str(match["module_id"]), match["blueprint_file"]
                )

            self.console.print(table)
            self.console.print()

        input("Press Enter to continue...")

    def _display_text_search_results(
        self, search_text: str, matches: List[Dict], case_sensitive: bool
    ):
        """Display text search results with pagination."""
        sensitivity = "case-sensitive" if case_sensitive else "case-insensitive"
        self.console.print(
            f"\n[bold green]Found {len(matches)} {sensitivity} matches for '{search_text}':[/bold green]\n"
        )

        if len(matches) <= 20:
            # Show all results if 20 or fewer
            self._show_text_results_page(matches, search_text, 0, len(matches))
            input("\nPress Enter to continue...")
        else:
            # Use pagination for more than 20 results
            self._paginate_text_results(matches, search_text)

    def _paginate_text_results(self, matches: List[Dict], search_text: str):
        """Handle pagination for text search results."""
        results_per_page = 20
        current_page = 0
        total_pages = (len(matches) - 1) // results_per_page + 1

        while True:
            start_idx = current_page * results_per_page
            end_idx = min(start_idx + results_per_page, len(matches))

            # Show current page of results
            self._show_text_results_page(
                matches[start_idx:end_idx], search_text, current_page, total_pages
            )

            # Show pagination options
            choices = []

            if current_page > 0:
                choices.append({"name": "⬅️  Previous page", "value": "prev"})
            if current_page < total_pages - 1:
                choices.append({"name": "➡️  Next page", "value": "next"})

            choices.extend(
                [
                    Separator(),
                    {"name": "🔍 Jump to page...", "value": "jump"},
                    {"name": "← Back to search menu", "value": "back"},
                ]
            )

            action = inquirer.select(
                message=f"Page {current_page + 1} of {total_pages} ({len(matches)} total matches)",
                choices=choices,
            ).execute()

            if action == "back":
                break
            elif action == "prev":
                current_page = max(0, current_page - 1)
            elif action == "next":
                current_page = min(total_pages - 1, current_page + 1)
            elif action == "jump":
                try:
                    page_num = inquirer.number(
                        message=f"Enter page number (1-{total_pages}):",
                        min_allowed=1,
                        max_allowed=total_pages,
                    ).execute()
                    current_page = page_num - 1
                except (ValueError, KeyboardInterrupt):
                    continue

    def _show_text_results_page(
        self, page_matches: List[Dict], search_text: str, current_page: int, total_pages: int
    ):
        """Display a single page of text search results."""
        page_info = f" (Page {current_page + 1}/{total_pages})" if total_pages > 1 else ""
        table = Table(title=f"Text Search Results{page_info}")
        table.add_column("Scenario", style="green")
        table.add_column("Module Type", style="cyan")
        table.add_column("Module ID", style="yellow")
        table.add_column("Context Preview", style="dim")

        for match in page_matches:
            # Clean up context preview
            context = match["context"].replace("\n", " ").replace("\t", " ")
            if len(context) > 60:
                context = context[:60] + "..."

            table.add_row(
                match["scenario_name"], match["module_type"], str(match["module_id"]), context
            )

        self.console.print(table)

        if total_pages > 1:
            self.console.print(f"\n[dim]Showing {len(page_matches)} results on this page[/dim]")
