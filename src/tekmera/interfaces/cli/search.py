"""
Interactive search interface for cross-blueprint analysis
"""

from pathlib import Path

from InquirerPy import inquirer
from InquirerPy.separator import Separator
from rich.panel import Panel
from rich.table import Table

from ...analysis.connections import (
    classify_connection_environment,
    display_connection_summary,
    display_connection_table,
    display_connection_warnings,
)
from ...analysis.corpus_analyzer import CorpusAnalyzer
from ...utils.base_cli import InteractiveCLIBase


class SearchInterface(InteractiveCLIBase):
    """Interactive search interface for cross-blueprint analysis."""

    def __init__(self):
        super().__init__(enable_search_display=True)
        self.analyzer = CorpusAnalyzer()

    def start(self, directory: Path):
        """Start the interactive search session."""
        self.console.print("\n🔍 [bold blue]Cross-Blueprint Search & Analysis[/bold blue]")
        self.console.print("Search and analyze patterns across all Fusion blueprints.\n")

        # Load corpus
        with self.console.status("[bold green]Loading blueprints..."):
            self.analyzer.load_corpus(directory)

        stats = self.analyzer.get_corpus_stats()
        self.show_success(
            f"Loaded {stats['total_blueprints']} blueprints with {stats['total_modules']} total modules"
        )
        self.console.print()

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
                self.handle_keyboard_interrupt()
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

        self.search_display.display_field_search_results(matches, field_pattern)

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

        self.search_display.display_module_search_results(matches, type_pattern)

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

        self.search_display.display_text_search_results(matches, search_text)

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
