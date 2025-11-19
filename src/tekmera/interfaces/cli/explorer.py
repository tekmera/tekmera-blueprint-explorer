"""
Interactive explorer for Workfront Fusion blueprints
"""

import json
from pathlib import Path
from typing import Any, Dict

from InquirerPy import inquirer
from InquirerPy.separator import Separator
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from ...analysis.connections import (
    ConnectionAnalyzer,
    display_connection_summary,
    display_connection_table,
)
from ...analysis.corpus_analyzer import CorpusAnalyzer
from ...utils.base_cli import InteractiveCLIBase


class BlueprintExplorer(InteractiveCLIBase):
    """Interactive explorer for Fusion blueprint analysis."""

    def __init__(self):
        super().__init__(enable_search_display=True)
        self.corpus_analyzer = CorpusAnalyzer()
        self.current_scenario = None
        self.current_modules = []
        self.modules_per_page = 15
        self.current_page = 0
        self.corpus_loaded = False

    def start(self, directory: Path):
        """Start the interactive exploration session."""
        self.console.print("\n🔍 [bold blue]Workfront Fusion Blueprint Explorer[/bold blue]")
        self.console.print("Navigate through scenarios and explore module details interactively.\n")

        # Load all blueprints
        self.load_blueprints(directory, include_modules=True)

        if not self.blueprints:
            self.show_error("No valid blueprint files found")
            return

        # Load corpus for search functionality
        self.corpus_analyzer.load_corpus(directory)
        self.corpus_loaded = True

        # Auto-select the first (and likely only) scenario
        if self.blueprints:
            first_scenario = list(self.blueprints.keys())[0]
            self.current_scenario = first_scenario
            self._load_scenario_modules()

        # Main exploration loop
        while True:
            try:
                action = self._main_menu()
                if action == "quit":
                    break
                elif action == "explore_modules":
                    self._module_exploration()
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
            except KeyboardInterrupt:
                self.handle_keyboard_interrupt()
                break

    def _main_menu(self) -> str:
        """Display main menu and get user choice."""
        choices = []

        if self.current_scenario:
            scenario_name = self.blueprints[self.current_scenario]["scenario_name"]
            choices.extend(
                [
                    {
                        "name": f"🔍 Explore modules in '{scenario_name}'",
                        "value": "explore_modules",
                    },
                    Separator(),
                ]
            )

        # Add search options
        if self.corpus_loaded:
            choices.extend(
                [
                    {"name": "🔎 Search for Workfront field (DE:)", "value": "field_search"},
                    {"name": "🔎 Search for module type", "value": "module_search"},
                    {"name": "🔎 Search for text/string", "value": "text_search"},
                    {"name": "📊 Field usage rankings", "value": "field_rankings"},
                    {"name": "📈 Module type usage", "value": "module_rankings"},
                    {"name": "⚠️  Detect inconsistent field naming", "value": "inconsistent_fields"},
                    {"name": "🔗 Analyze connections", "value": "connections"},
                    Separator(),
                ]
            )

        choices.append({"name": "❌ Quit", "value": "quit"})

        return inquirer.select(message="What would you like to do?", choices=choices).execute()

    def _load_scenario_modules(self):
        """Load modules for the currently selected scenario."""
        blueprint_data = self.blueprints[self.current_scenario]["data"]
        modules = self.parser.get_modules(blueprint_data, include_orphans=False)

        self.current_modules = []
        for i, module in enumerate(modules):
            module_info = self.analyzer.get_detailed_module_info(module, i + 1)
            self.current_modules.append(module_info)

        # Reset pagination when loading new scenario
        self.current_page = 0

    def _module_exploration(self):
        """Explore modules in the current scenario."""
        if not self.current_modules:
            self.console.print("[red]No modules found in this scenario.[/red]")
            return

        while True:
            # Display module index
            self._display_module_index()

            # Get current page modules
            start_idx = self.current_page * self.modules_per_page
            end_idx = min(start_idx + self.modules_per_page, len(self.current_modules))
            page_modules = self.current_modules[start_idx:end_idx]

            # Get user choice
            choices = []
            for module in page_modules:
                name = f"{module['index']}. {module['name']}"
                type_info = f"[dim]({module['type']})[/dim]"
                summary = f"[green]{module['summary']}[/green]" if module["summary"] else ""

                display_name = f"{name} {type_info}"
                if summary:
                    display_name += f" - {summary}"

                choices.append({"name": display_name, "value": module["index"] - 1})

            # Add pagination controls
            pagination_choices = []
            total_pages = (len(self.current_modules) - 1) // self.modules_per_page + 1

            if self.current_page > 0:
                pagination_choices.append({"name": "⬅️  Previous page", "value": "prev_page"})
            if self.current_page < total_pages - 1:
                pagination_choices.append({"name": "➡️  Next page", "value": "next_page"})

            if pagination_choices:
                choices.extend([Separator()] + pagination_choices)

            choices.extend([Separator(), {"name": "← Back", "value": "back"}])

            selection = inquirer.select(
                message=f"Select a module to explore (Page {self.current_page + 1}/{total_pages}):",
                choices=choices,
            ).execute()

            if selection == "back":
                break
            elif selection == "prev_page":
                self.current_page = max(0, self.current_page - 1)
            elif selection == "next_page":
                self.current_page = min(total_pages - 1, self.current_page + 1)
            else:
                self._explore_single_module(self.current_modules[selection])

    def _display_module_index(self):
        """Display a table of modules in the current scenario."""
        scenario_name = self.blueprints[self.current_scenario]["scenario_name"]

        # Get current page modules
        start_idx = self.current_page * self.modules_per_page
        end_idx = min(start_idx + self.modules_per_page, len(self.current_modules))
        page_modules = self.current_modules[start_idx:end_idx]

        total_pages = (len(self.current_modules) - 1) // self.modules_per_page + 1
        page_info = f" (Page {self.current_page + 1}/{total_pages})" if total_pages > 1 else ""

        table = Table(title=f"Modules in '{scenario_name}'{page_info}")
        table.add_column("#", style="cyan", width=3)
        table.add_column("Name", style="bold")
        table.add_column("Type", style="dim")
        table.add_column("Summary", style="green")

        for module in page_modules:
            table.add_row(str(module["index"]), module["name"], module["type"], module["summary"])

        self.console.print("\n")
        self.console.print(table)

        if total_pages > 1:
            self.console.print(
                f"[dim]Showing {len(page_modules)} of {len(self.current_modules)} total modules[/dim]"
            )

        self.console.print("\n")

    def _explore_single_module(self, module: Dict[str, Any]):
        """Explore a single module in detail."""
        while True:
            self._display_module_details(module)

            choices = [
                {"name": "📋 View parameters", "value": "parameters"},
                {"name": "🔗 View mapper/inputs", "value": "mapper"},
                {"name": "🏷️  View Workfront fields", "value": "de_fields"},
                {"name": "📄 View raw JSON", "value": "raw"},
                Separator(),
                {"name": "← Back to module list", "value": "back"},
            ]

            action = inquirer.select(
                message="What would you like to view?", choices=choices
            ).execute()

            if action == "back":
                break
            elif action == "parameters":
                self._display_parameters(module)
            elif action == "mapper":
                self._display_mapper(module)
            elif action == "de_fields":
                self._display_de_fields(module)
            elif action == "raw":
                self._display_raw_json(module)

    def _display_module_details(self, module: Dict[str, Any]):
        """Display module overview."""
        # Handle None values safely
        de_fields_count = len(module.get("de_fields", []))
        parameters_count = len(module.get("parameters", {}))
        mapper_count = len(module.get("mapper", {}) or {})

        content = f"""[bold]{module['name']}[/bold]

[dim]Type:[/dim] {module['type']}
[dim]ID:[/dim] {module['id']}
[dim]Summary:[/dim] {module['summary']}

[dim]DE Fields:[/dim] {de_fields_count} found
[dim]Parameters:[/dim] {parameters_count} items
[dim]Mapper/Inputs:[/dim] {mapper_count} items"""

        panel = Panel(content, title="📦 Module Details", expand=False)
        self.console.print("\n")
        self.console.print(panel)
        self.console.print("\n")

    def _display_parameters(self, module: Dict[str, Any]):
        """Display module parameters."""
        parameters = module.get("parameters", {}) or {}
        if not parameters:
            self.console.print("[yellow]No parameters found.[/yellow]")
            input("\nPress Enter to continue...")
            return

        self.console.print("\n[bold]📋 Module Parameters[/bold]\n")

        syntax = Syntax(
            json.dumps(parameters, indent=2), "json", theme="monokai", line_numbers=True
        )
        self.console.print(syntax)
        input("\nPress Enter to continue...")

    def _display_mapper(self, module: Dict[str, Any]):
        """Display module mapper/input data."""
        mapper = module.get("mapper", {}) or {}
        if not mapper:
            self.console.print("[yellow]No mapper/input data found.[/yellow]")
            input("\nPress Enter to continue...")
            return

        self.console.print("\n[bold]🔗 Module Mapper/Inputs[/bold]\n")

        syntax = Syntax(json.dumps(mapper, indent=2), "json", theme="monokai", line_numbers=True)
        self.console.print(syntax)
        input("\nPress Enter to continue...")

    def _display_de_fields(self, module: Dict[str, Any]):
        """Display Workfront DE fields found in module."""
        if not module["de_fields"]:
            self.console.print("[yellow]No Workfront fields (DE:) found in this module.[/yellow]")
            input("\nPress Enter to continue...")
            return

        self.console.print("\n[bold]🏷️  Workfront Fields in Module[/bold]\n")

        for field in module["de_fields"]:
            self.console.print(f"  • [green]{field}[/green]")

        input("\nPress Enter to continue...")

    def _display_raw_json(self, module: Dict[str, Any]):
        """Display raw JSON data for module."""
        self.console.print("\n[bold]📄 Raw Module JSON[/bold]\n")

        syntax = Syntax(
            json.dumps(module["raw_data"], indent=2), "json", theme="monokai", line_numbers=True
        )
        self.console.print(syntax)
        input("\nPress Enter to continue...")

    def _field_search(self):
        """Interactive Workfront field search."""
        field_pattern = inquirer.text(
            message="Enter field to search for (e.g., 'DE:client_id' or just 'client'):"
        ).execute()

        if not field_pattern:
            return

        exact_match = inquirer.confirm(message="Require exact match?", default=False).execute()

        matches = self.corpus_analyzer.search_de_fields(field_pattern, exact_match)

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

        matches = self.corpus_analyzer.search_module_types(type_pattern, exact_match)

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

        matches = self.corpus_analyzer.search_text(search_text, case_sensitive)

        if not matches:
            self.console.print(f"[red]No matches found for '{search_text}'[/red]")
            input("\nPress Enter to continue...")
            return

        self.search_display.display_text_search_results(matches, search_text)

    def _show_field_rankings(self):
        """Show DE field usage rankings."""
        rankings = self.corpus_analyzer.get_de_field_rankings()

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
        rankings = self.corpus_analyzer.get_module_type_rankings()

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
            ],
        ).execute()

        with self.console.status("[bold green]Analyzing field naming patterns..."):
            inconsistencies = self.corpus_analyzer.detect_inconsistent_field_naming(threshold)

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
        # For single-scenario analysis, use the centralized analyzer directly
        if not self.current_scenario:
            self.console.print("[red]No scenario selected.[/red]")
            input("\nPress Enter to continue...")
            return

        blueprint_data = self.blueprints[self.current_scenario]["data"]
        scenario_name = self.blueprints[self.current_scenario]["scenario_name"]

        with self.console.status("[bold green]Analyzing connections..."):
            # Use centralized connection analyzer for consistency
            analyzer = ConnectionAnalyzer()
            analysis_result = analyzer.analyze_blueprint_connections(blueprint_data, scenario_name)

        connections = analysis_result.get("connections", {})
        connection_labels = analysis_result.get("connection_labels", {})
        connection_types = analysis_result.get("connection_types", {})

        if not connections:
            self.console.print("[yellow]No connections found.[/yellow]")
            input("\nPress Enter to continue...")
            return

        # Display connection usage table using shared utility (no warnings for single scenario)
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
