"""
Fusion Blueprint Diff CLI - Compare blueprint scenarios
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from InquirerPy import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..analysis.connections import ConnectionAnalyzer
from ..core.analyzer import BlueprintAnalyzer
from ..core.parser import BlueprintParser


class FusionDiff:
    """CLI tool for comparing Fusion blueprint scenarios."""

    def __init__(self):
        self.console = Console()
        self.parser = BlueprintParser()
        self.analyzer = BlueprintAnalyzer()
        self.connection_analyzer = ConnectionAnalyzer()
        self.blueprints = {}

    def run(self, directory: Path):
        """Main entry point for the diff CLI."""
        self.console.print("\n[bold blue]🔄 Fusion Explorer: Diff Scenarios[/bold blue]")
        self.console.print("Compare blueprint scenarios and explore their differences.\n")

        # Load all blueprints
        self._load_blueprints(directory)

        if len(self.blueprints) < 2:
            self.console.print("[red]Need at least 2 blueprint files to compare.[/red]")
            return

        # Interactive scenario selection
        self._interactive_diff()

    def _load_blueprints(self, directory: Path):
        """Load all blueprint files from directory and subfolders."""
        # Recursively find all JSON files
        json_files = list(directory.rglob("*.json"))

        for json_file in json_files:
            try:
                blueprint_data = self.parser.load_blueprint(json_file)

                # Extract scenario name correctly for both structures
                if "blueprint" in blueprint_data:
                    scenario_name = blueprint_data["blueprint"].get("name", json_file.stem)
                else:
                    scenario_name = blueprint_data.get("name", json_file.stem)

                # Create a unique key that includes relative path
                relative_path = json_file.relative_to(directory)
                blueprint_key = str(relative_path.with_suffix(""))  # Remove .json extension

                self.blueprints[blueprint_key] = {
                    "filename": json_file.stem,
                    "scenario_name": scenario_name,
                    "file_path": json_file,
                    "relative_path": relative_path,
                    "data": blueprint_data,
                }
            except Exception as e:
                self.console.print(f"[red]Warning: Could not load {json_file.name}: {e}[/red]")

    def _interactive_diff(self):
        """Interactive scenario selection and comparison."""
        # Get list of available scenarios
        scenario_choices = []
        for i, (key, blueprint) in enumerate(self.blueprints.items(), 1):
            relative_path = blueprint.get("relative_path", Path(blueprint["filename"] + ".json"))
            scenario_choices.append({"name": f"{relative_path}", "value": key})

        # Display available scenarios
        self.console.print("Select the first scenario to compare:")
        for i, choice in enumerate(scenario_choices, 1):
            self.console.print(f"[{i}] {choice['name']}")

        # Select first scenario
        first_selection = inquirer.select(
            message="> Enter number:", choices=scenario_choices
        ).execute()

        if not first_selection:
            return

        # Display available scenarios for second selection
        self.console.print(f"\nSelect the second scenario to compare:")
        for i, choice in enumerate(scenario_choices, 1):
            self.console.print(f"[{i}] {choice['name']}")

        # Select second scenario
        second_selection = inquirer.select(
            message="> Enter number:", choices=scenario_choices
        ).execute()

        if not second_selection or first_selection == second_selection:
            if first_selection == second_selection:
                self.console.print("[yellow]Cannot compare a scenario with itself.[/yellow]")
            return

        # Perform the comparison
        first_blueprint = self.blueprints[first_selection]
        second_blueprint = self.blueprints[second_selection]

        self.console.print(f"\nRunning diff between:")
        self.console.print(f"- {first_blueprint['filename']}.json")
        self.console.print(f"+ {second_blueprint['filename']}.json")

        self._compare_blueprints(first_blueprint, second_blueprint)

    def _compare_blueprints(self, blueprint1: Dict, blueprint2: Dict):
        """Compare two blueprints and display differences."""

        # Compare basic metadata
        self.console.print("\n[bold]📊 Scenario Comparison[/bold]\n")

        comparison_table = Table(title="Scenario Overview")
        comparison_table.add_column("Attribute", style="cyan")
        comparison_table.add_column(f"{blueprint1['filename']}", style="green")
        comparison_table.add_column(f"{blueprint2['filename']}", style="yellow")

        # Get modules for comparison - handle both direct flow and blueprint.flow structures
        data1 = blueprint1["data"]
        data2 = blueprint2["data"]

        # If the data has a 'blueprint' key, use that instead
        if "blueprint" in data1:
            data1 = data1["blueprint"]
        if "blueprint" in data2:
            data2 = data2["blueprint"]

        modules1 = self.parser.get_modules(data1, include_orphans=False)
        modules2 = self.parser.get_modules(data2, include_orphans=False)

        comparison_table.add_row(
            "Scenario Name", blueprint1["scenario_name"], blueprint2["scenario_name"]
        )
        comparison_table.add_row("Total Modules", str(len(modules1)), str(len(modules2)))

        # Get DE fields for comparison
        de_fields1 = set()
        de_fields2 = set()

        for i, module in enumerate(modules1):
            module_info = self.analyzer.get_detailed_module_info(module, i + 1)
            de_fields1.update(module_info.get("de_fields", []))

        for i, module in enumerate(modules2):
            module_info = self.analyzer.get_detailed_module_info(module, i + 1)
            de_fields2.update(module_info.get("de_fields", []))

        comparison_table.add_row("Unique DE Fields", str(len(de_fields1)), str(len(de_fields2)))

        self.console.print(comparison_table)
        self.console.print()

        # Show field differences
        self._show_field_differences(
            de_fields1, de_fields2, blueprint1["filename"], blueprint2["filename"]
        )

        # Show module type differences
        self._show_module_type_differences(
            modules1, modules2, blueprint1["filename"], blueprint2["filename"]
        )

        # Show connection differences specifically
        self._show_connection_differences(
            blueprint1["data"], blueprint2["data"], blueprint1["filename"], blueprint2["filename"]
        )

        # Show detailed module differences
        modified_modules = self._show_module_differences(
            modules1, modules2, blueprint1["filename"], blueprint2["filename"]
        )

        # Show summary of all changes
        self._show_change_summary(modified_modules, blueprint1["filename"], blueprint2["filename"])

    def _show_field_differences(self, fields1: Set[str], fields2: Set[str], name1: str, name2: str):
        """Show differences in DE fields between scenarios."""
        only_in_1 = fields1 - fields2
        only_in_2 = fields2 - fields1
        common = fields1 & fields2

        if only_in_1 or only_in_2:
            self.console.print("[bold]🏷️  DE Field Differences[/bold]\n")

            if only_in_1:
                panel_content = "\n".join(f"• {field}" for field in sorted(only_in_1))
                panel = Panel(
                    panel_content,
                    title=f"Only in {name1} ({len(only_in_1)} fields)",
                    border_style="red",
                    expand=False,
                )
                self.console.print(panel)

            if only_in_2:
                panel_content = "\n".join(f"• {field}" for field in sorted(only_in_2))
                panel = Panel(
                    panel_content,
                    title=f"Only in {name2} ({len(only_in_2)} fields)",
                    border_style="green",
                    expand=False,
                )
                self.console.print(panel)

            if common:
                self.console.print(f"[dim]Common fields: {len(common)}[/dim]\n")
        else:
            self.console.print("[green]✓ DE fields are identical between scenarios[/green]\n")

    def _show_module_type_differences(self, modules1: List, modules2: List, name1: str, name2: str):
        """Show differences in module types between scenarios."""
        types1 = {}
        types2 = {}

        # Count module types in first scenario
        for module in modules1:
            module_type = module.get("type", "unknown")
            types1[module_type] = types1.get(module_type, 0) + 1

        # Count module types in second scenario
        for module in modules2:
            module_type = module.get("type", "unknown")
            types2[module_type] = types2.get(module_type, 0) + 1

        all_types = set(types1.keys()) | set(types2.keys())

        if len(all_types) > 0:
            self.console.print("[bold]🔧 Module Type Comparison[/bold]\n")

            diff_table = Table(title="Module Types")
            diff_table.add_column("Module Type", style="cyan")
            diff_table.add_column(f"{name1}", style="green", justify="right")
            diff_table.add_column(f"{name2}", style="yellow", justify="right")
            diff_table.add_column("Difference", style="red", justify="right")

            for module_type in sorted(all_types):
                count1 = types1.get(module_type, 0)
                count2 = types2.get(module_type, 0)
                diff = count2 - count1

                diff_str = ""
                if diff > 0:
                    diff_str = f"+{diff}"
                elif diff < 0:
                    diff_str = str(diff)
                else:
                    diff_str = "0"

                diff_table.add_row(module_type, str(count1), str(count2), diff_str)

            self.console.print(diff_table)
            self.console.print()

    def _show_module_differences(self, modules1: List, modules2: List, name1: str, name2: str):
        """Show detailed module-level differences."""
        # Create module maps by ID for comparison
        modules1_by_id = {mod.get("id"): mod for mod in modules1 if mod.get("id")}
        modules2_by_id = {mod.get("id"): mod for mod in modules2 if mod.get("id")}

        set(modules1_by_id.keys()) | set(modules2_by_id.keys())
        only_in_1 = set(modules1_by_id.keys()) - set(modules2_by_id.keys())
        only_in_2 = set(modules2_by_id.keys()) - set(modules1_by_id.keys())
        common_ids = set(modules1_by_id.keys()) & set(modules2_by_id.keys())

        if only_in_1 or only_in_2:
            self.console.print("[bold]📦 Module Differences[/bold]\n")

            if only_in_1:
                self.console.print(f"[red]Modules only in {name1} ({len(only_in_1)}):[/red]")
                for mod_id in sorted(only_in_1):
                    module = modules1_by_id[mod_id]
                    mod_name = module.get("name", "Unnamed")
                    mod_type = module.get("type", "unknown")
                    self.console.print(f"  • {mod_name} ({mod_type}) [dim]ID: {mod_id}[/dim]")
                self.console.print()

            if only_in_2:
                self.console.print(f"[green]Modules only in {name2} ({len(only_in_2)}):[/green]")
                for mod_id in sorted(only_in_2):
                    module = modules2_by_id[mod_id]
                    mod_name = module.get("name", "Unnamed")
                    mod_type = module.get("type", "unknown")
                    self.console.print(f"  • {mod_name} ({mod_type}) [dim]ID: {mod_id}[/dim]")
                self.console.print()

        # Check for differences in common modules using functional comparison
        modified_modules = []
        for mod_id in common_ids:
            mod1 = modules1_by_id[mod_id]
            mod2 = modules2_by_id[mod_id]

            # Normalize modules for functional comparison (ignore cosmetic changes)
            norm1 = self._normalize_module_for_comparison(mod1)
            norm2 = self._normalize_module_for_comparison(mod2)

            # Compare normalized modules
            if json.dumps(norm1, sort_keys=True) != json.dumps(norm2, sort_keys=True):
                modified_modules.append((mod1, mod2))

        if modified_modules:
            self.console.print(
                f"[yellow]📝 Functionally modified modules ({len(modified_modules)}):[/yellow]"
            )
            for mod1, mod2 in modified_modules:
                mod_name = mod1.get("name", mod2.get("name", "Unnamed"))
                mod_id = mod1.get("id", mod2.get("id", "unknown"))
                mod_type = mod1.get("module", mod2.get("module", "unknown"))

                # Get actual module name from metadata if available
                if "metadata" in mod1 and "designer" in mod1["metadata"]:
                    mod_name = mod1["metadata"]["designer"].get("name", mod_name)
                elif "metadata" in mod2 and "designer" in mod2["metadata"]:
                    mod_name = mod2["metadata"]["designer"].get("name", mod_name)

                self.console.print(f"  • {mod_name} ({mod_type}) [dim]ID: {mod_id}[/dim]")

                # Show what specific areas changed
                changes = self._identify_functional_changes(mod1, mod2)
                if changes:
                    for change in changes:
                        self.console.print(f"    - {change}")
            self.console.print()

        if common_ids and not modified_modules:
            self.console.print(
                f"[green]✓ All {len(common_ids)} common modules are identical[/green]\n"
            )

        return modified_modules

    def _normalize_module_for_comparison(self, module: Dict) -> Dict:
        """Normalize a module for functional comparison, ignoring cosmetic changes."""
        # Create a copy to avoid modifying the original
        normalized = json.loads(json.dumps(module))

        # Remove cosmetic metadata that doesn't affect functionality
        if "metadata" in normalized:
            metadata = normalized["metadata"]

            # Remove designer positions (cosmetic)
            if "designer" in metadata:
                designer = metadata["designer"]
                # Keep important designer info but remove position
                if "x" in designer:
                    del designer["x"]
                if "y" in designer:
                    del designer["y"]
                # Keep name as it might be functionally relevant

            # Remove restore data (cosmetic, used for UI state)
            if "restore" in metadata:
                del metadata["restore"]

            # If metadata is now empty, remove it entirely
            if not metadata:
                del normalized["metadata"]

        # Sort arrays and objects for consistent comparison
        self._sort_nested_structures(normalized)

        return normalized

    def _sort_nested_structures(self, obj):
        """Recursively sort nested structures for consistent comparison."""
        if isinstance(obj, dict):
            for value in obj.values():
                self._sort_nested_structures(value)
        elif isinstance(obj, list):
            # Only sort if all items are comparable (same type)
            if obj and all(isinstance(item, type(obj[0])) for item in obj):
                try:
                    if isinstance(obj[0], dict):
                        # Sort list of dicts by a stable key if available
                        if all("name" in item for item in obj):
                            obj.sort(key=lambda x: x["name"])
                        elif all("id" in item for item in obj):
                            obj.sort(key=lambda x: str(x["id"]))
                    elif isinstance(obj[0], str):
                        obj.sort()
                except Exception:
                    pass  # Skip sorting if comparison fails

            # Recursively sort nested structures
            for item in obj:
                self._sort_nested_structures(item)

    def _identify_functional_changes(self, mod1: Dict, mod2: Dict) -> List[str]:
        """Identify specific functional changes between two modules."""
        changes = []

        # Normalize both modules first
        norm1 = self._normalize_module_for_comparison(mod1)
        norm2 = self._normalize_module_for_comparison(mod2)

        # Special handling for connection changes (high priority)
        connection_changes = self._analyze_connection_changes(mod1, mod2)
        if connection_changes:
            changes.extend(connection_changes)

        # Special handling for router modules
        if (
            mod1.get("module") == "builtin:BasicRouter"
            or mod2.get("module") == "builtin:BasicRouter"
        ):
            router_changes = self._analyze_router_changes(mod1, mod2)
            changes.extend(router_changes)

        # Check major sections for changes
        sections_to_check = ["mapper", "parameters", "module", "version", "interface"]

        for section in sections_to_check:
            val1 = norm1.get(section)
            val2 = norm2.get(section)

            if val1 != val2:
                if section == "mapper" and isinstance(val1, dict) and isinstance(val2, dict):
                    # For mapper, get detailed field changes
                    mapper_changes = self._analyze_mapper_changes(val1, val2)
                    changes.extend(mapper_changes)
                elif section == "parameters":
                    param_changes = self._analyze_parameter_changes(val1, val2)
                    changes.extend(param_changes)
                elif section == "module":
                    changes.append(f"Module type changed: {val1} → {val2}")
                elif section == "version":
                    changes.append(f"Version changed: {val1} → {val2}")
                elif section == "interface":
                    changes.append("Interface/spec modified")

        # Check for metadata changes (functional ones only)
        meta1 = norm1.get("metadata", {})
        meta2 = norm2.get("metadata", {})

        if meta1.get("interface") != meta2.get("interface"):
            changes.append("Interface specification changed")

        # If no specific changes found, provide detailed analysis
        if not changes:
            detailed_changes = self._get_detailed_module_changes(norm1, norm2)
            changes.extend(detailed_changes)

        return changes

    def _analyze_connection_changes(self, mod1: Dict, mod2: Dict) -> List[str]:
        """Analyze connection changes between two modules using existing ConnectionAnalyzer."""
        changes = []

        # Extract connection data for both modules
        conn1_data = self._extract_module_connection_info(mod1)
        conn2_data = self._extract_module_connection_info(mod2)

        if not conn1_data and not conn2_data:
            return changes

        # Compare connection IDs
        conn1_id = conn1_data.get("id") if conn1_data else None
        conn2_id = conn2_data.get("id") if conn2_data else None

        if conn1_id != conn2_id:
            conn1_label = (
                conn1_data.get("label", f"Connection {conn1_id}") if conn1_data else "None"
            )
            conn2_label = (
                conn2_data.get("label", f"Connection {conn2_id}") if conn2_data else "None"
            )

            if conn1_id is None:
                changes.append(f"🔌 Connection added: {conn2_label} (ID: {conn2_id})")
            elif conn2_id is None:
                changes.append(f"🔌 Connection removed: {conn1_label} (ID: {conn1_id})")
            else:
                # Check if it's an environment change
                env1 = self._classify_environment(conn1_label)
                env2 = self._classify_environment(conn2_label)

                env_note = ""
                if env1 != env2:
                    env_note = f" [{env1} → {env2}]"

                changes.append(
                    f"🔌 Connection swapped: {conn1_label} (ID: {conn1_id}) → {conn2_label} (ID: {conn2_id}){env_note}"
                )

        return changes

    def _extract_module_connection_info(self, module: Dict) -> Dict:
        """Extract connection information from a module."""
        connection_info = {}

        # Look for connection ID in parameters
        params = module.get("parameters", {})
        connection_fields = ["__IMTCONN__", "account", "connection"]

        for field in connection_fields:
            if field in params:
                connection_id = params[field]
                if connection_id:
                    connection_info["id"] = connection_id
                    break

        # Get connection label from metadata if available
        if connection_info.get("id"):
            metadata = module.get("metadata", {})
            restore = metadata.get("restore", {})

            for field in connection_fields:
                if field in restore and isinstance(restore[field], dict):
                    label = restore[field].get("label", "")
                    if label:
                        connection_info["label"] = label
                        break

        return connection_info

    def _classify_environment(self, connection_label: str) -> str:
        """Classify connection environment based on label patterns."""
        if not connection_label:
            return "UNKNOWN"

        label_lower = connection_label.lower()

        # DEV environment indicators
        dev_keywords = [
            "dev",
            "test",
            "testing",
            "sandbox",
            "stage",
            "staging",
            "demo",
            "preview",
            "sb01",
            "sb02",
            "sb03",
            "sb04",
            "sb05",
        ]

        if any(keyword in label_lower for keyword in dev_keywords):
            return "DEV"

        # PROD environment indicators (for Workfront specifically)
        if "my." in label_lower or label_lower.startswith("my"):
            return "PROD"

        # Default to UNKNOWN if can't determine
        return "UNKNOWN"

    def _show_connection_differences(self, data1: Dict, data2: Dict, name1: str, name2: str):
        """Show connection differences between two blueprints."""
        # Extract all connections from both blueprints
        connections1 = self.connection_analyzer.find_connections_in_json(data1)
        connections2 = self.connection_analyzer.find_connections_in_json(data2)

        # Get connection labels
        labels1 = self.connection_analyzer.extract_connection_labels(data1)
        labels2 = self.connection_analyzer.extract_connection_labels(data2)

        # Get unique connection IDs
        conn_ids1 = set([conn[0] for conn in connections1])
        conn_ids2 = set([conn[0] for conn in connections2])

        if conn_ids1 == conn_ids2 and len(conn_ids1) <= 1:
            return  # No significant connection changes to show

        self.console.print("[bold]🔌 Connection Analysis[/bold]\n")

        # Show connection swap summary
        if conn_ids1 != conn_ids2:
            removed_conns = conn_ids1 - conn_ids2
            added_conns = conn_ids2 - conn_ids1

            if removed_conns or added_conns:
                table = Table(title="Connection Changes")
                table.add_column("Change Type", style="cyan")
                table.add_column("Connection", style="yellow")
                table.add_column("Environment", style="green")

                for conn_id in removed_conns:
                    label = labels1.get(conn_id, f"Connection {conn_id}")
                    env = self._classify_environment(label)
                    table.add_row("❌ Removed", label, env)

                for conn_id in added_conns:
                    label = labels2.get(conn_id, f"Connection {conn_id}")
                    env = self._classify_environment(label)
                    table.add_row("✅ Added", label, env)

                self.console.print(table)

                # Show usage counts
                count1 = len(connections1)
                count2 = len(connections2)
                if count1 != count2:
                    self.console.print(
                        f"\n[bold]Usage Count Change:[/bold] {count1} → {count2} references"
                    )

                # Show environment change warning
                if removed_conns and added_conns:
                    old_env = None
                    new_env = None
                    if removed_conns:
                        old_conn = list(removed_conns)[0]
                        old_label = labels1.get(old_conn, "")
                        old_env = self._classify_environment(old_label)
                    if added_conns:
                        new_conn = list(added_conns)[0]
                        new_label = labels2.get(new_conn, "")
                        new_env = self._classify_environment(new_label)

                    if old_env and new_env and old_env != new_env:
                        env_color = (
                            "red"
                            if new_env == "DEV"
                            else "green" if new_env == "PROD" else "yellow"
                        )
                        panel = Panel(
                            f"Environment change detected: {old_env} → [{env_color}]{new_env}[/{env_color}]",
                            title="🚨 Environment Change Warning",
                            border_style="red" if new_env == "DEV" else "yellow",
                            expand=False,
                        )
                        self.console.print(panel)

                self.console.print()

    def _analyze_router_changes(self, mod1: Dict, mod2: Dict) -> List[str]:
        """Analyze changes in router modules, focusing on filter conditions."""
        changes = []

        routes1 = mod1.get("routes", [])
        routes2 = mod2.get("routes", [])

        if len(routes1) != len(routes2):
            changes.append(f"Route count changed: {len(routes1)} → {len(routes2)}")

        # Analyze each route path
        max_routes = max(len(routes1), len(routes2))
        for i in range(max_routes):
            route1 = routes1[i] if i < len(routes1) else None
            route2 = routes2[i] if i < len(routes2) else None

            if route1 is None:
                changes.append(f"Route {i+1}: Added new route")
                continue
            elif route2 is None:
                changes.append(f"Route {i+1}: Removed route")
                continue

            # Analyze route flow changes
            route_changes = self._analyze_route_flow_changes(
                route1.get("flow", []), route2.get("flow", []), i + 1
            )
            changes.extend(route_changes)

        return changes

    def _analyze_route_flow_changes(self, flow1: List, flow2: List, route_num: int) -> List[str]:
        """Analyze changes in a specific route flow, focusing on filters."""
        changes = []

        if len(flow1) != len(flow2):
            changes.append(f"Route {route_num}: Module count changed ({len(flow1)} → {len(flow2)})")

        # Check each module in the flow
        max_modules = max(len(flow1), len(flow2))
        for i in range(max_modules):
            mod1 = flow1[i] if i < len(flow1) else None
            mod2 = flow2[i] if i < len(flow2) else None

            if mod1 is None:
                mod_name = self._get_module_display_name(mod2)
                changes.append(f"Route {route_num}: Added module '{mod_name}'")
                continue
            elif mod2 is None:
                mod_name = self._get_module_display_name(mod1)
                changes.append(f"Route {route_num}: Removed module '{mod_name}'")
                continue

            # Check for filter changes
            filter_changes = self._analyze_filter_changes(
                mod1.get("filter"), mod2.get("filter"), route_num, i + 1
            )
            changes.extend(filter_changes)

        return changes

    def _analyze_filter_changes(
        self, filter1: Optional[Dict], filter2: Optional[Dict], route_num: int, module_num: int
    ) -> List[str]:
        """Analyze changes in filter conditions with detailed diff display."""
        changes = []

        if filter1 is None and filter2 is None:
            return changes

        route_module_label = f"Route {route_num}, Module {module_num}"

        if filter1 is None and filter2 is not None:
            filter_name = filter2.get("name", "Unnamed")
            changes.append(f"{route_module_label}: Added filter '{filter_name}'")
            changes.extend(self._format_filter_conditions(filter2, "  +"))
            return changes

        if filter1 is not None and filter2 is None:
            filter_name = filter1.get("name", "Unnamed")
            changes.append(f"{route_module_label}: Removed filter '{filter_name}'")
            return changes

        # Both filters exist, compare them
        name1 = filter1.get("name", "Unnamed")
        name2 = filter2.get("name", "Unnamed")

        if name1 != name2:
            changes.append(f"{route_module_label}: Filter name changed: '{name1}' → '{name2}'")

        # Compare conditions
        conditions1 = filter1.get("conditions", [])
        conditions2 = filter2.get("conditions", [])

        if conditions1 != conditions2:
            changes.append(f"{route_module_label}: Filter conditions changed for '{name2}':")
            changes.extend(self._detailed_condition_diff(conditions1, conditions2))

        return changes

    def _detailed_condition_diff(self, cond1: List, cond2: List) -> List[str]:
        """Create a detailed diff of filter conditions."""
        changes = []

        # Convert conditions to comparable format
        def condition_to_string(condition):
            if not condition:
                return "ALWAYS TRUE (no conditions)"

            or_groups = []
            for or_group in condition:
                and_conditions = []
                for cond in or_group:
                    a = cond.get("a", "")
                    b = cond.get("b", "")
                    o = cond.get("o", "")
                    and_conditions.append(f"{a} {o} {b}")
                or_groups.append(f"({' AND '.join(and_conditions)})")
            return " OR ".join(or_groups)

        str1 = condition_to_string(cond1)
        str2 = condition_to_string(cond2)

        if str1 != str2:
            # Break long conditions into multiple lines for readability
            changes.append(f"    - Old: {self._wrap_condition_text(str1)}")
            changes.append(f"    + New: {self._wrap_condition_text(str2)}")

        return changes

    def _format_filter_conditions(self, filter_obj: Dict, prefix: str) -> List[str]:
        """Format filter conditions for display."""
        formatted = []
        conditions = filter_obj.get("conditions", [])

        if not conditions:
            formatted.append(f"{prefix} ALWAYS TRUE (no conditions)")
            return formatted

        for i, or_group in enumerate(conditions):
            if i > 0:
                formatted.append(f"{prefix} OR")

            for j, condition in enumerate(or_group):
                if j > 0:
                    formatted.append(f"{prefix}   AND")

                a = condition.get("a", "")
                b = condition.get("b", "")
                o = condition.get("o", "")
                formatted.append(f"{prefix}   {a} {o} {b}")

        return formatted

    def _get_module_display_name(self, module: Dict) -> str:
        """Get a display name for a module."""
        if not module:
            return "Unknown"

        # Try to get name from metadata
        if "metadata" in module and "designer" in module["metadata"]:
            name = module["metadata"]["designer"].get("name")
            if name:
                return name

        # Fall back to module type
        return module.get("module", "Unknown")

    def _wrap_condition_text(self, text: str, width: int = 80) -> str:
        """Wrap long condition text for better readability."""
        if len(text) <= width:
            return text

        # Try to break at logical points (AND/OR operators)
        if " AND " in text:
            parts = text.split(" AND ")
            wrapped = parts[0]
            for part in parts[1:]:
                if len(wrapped + " AND " + part) > width:
                    wrapped += "\n           AND " + part
                else:
                    wrapped += " AND " + part
            return wrapped
        elif " OR " in text:
            parts = text.split(" OR ")
            wrapped = parts[0]
            for part in parts[1:]:
                if len(wrapped + " OR " + part) > width:
                    wrapped += "\n          OR " + part
                else:
                    wrapped += " OR " + part
            return wrapped

        return text

    def _detect_global_connection_changes(self, modified_modules: List) -> str:
        """Detect if the changes represent a global connection swap scenario."""
        connection_changes = []

        # Extract all connection changes from modified modules
        for mod1, mod2 in modified_modules:
            changes = self._identify_functional_changes(mod1, mod2)
            for change in changes:
                if (
                    "Connection swapped:" in change
                    or "Connection added:" in change
                    or "Connection removed:" in change
                ):
                    connection_changes.append(change)

        if not connection_changes:
            return ""

        # Analyze if this looks like a global connection swap
        if len(connection_changes) >= 3:  # Multiple modules with connection changes
            # Extract connection swap pattern
            swap_pattern = None
            for change in connection_changes:
                if "Connection swapped:" in change:
                    swap_pattern = change
                    break

            if swap_pattern:
                # Count how many modules are affected
                total_affected = len(modified_modules)
                connection_affected = len(connection_changes)

                # If most/all changes are connection-related, it's likely a global swap
                if (
                    connection_affected >= total_affected * 0.7
                ):  # 70% or more are connection changes
                    return (
                        f"🔄 [bold yellow]Global Connection Swap Detected[/bold yellow]\n"
                        f"   📊 {connection_affected} modules affected by connection change\n"
                        f"   {swap_pattern.replace('🔌 Connection swapped:', '   🔌 Change:')}\n"
                        f"   💡 This appears to be a systematic connection swap across the scenario"
                    )

        return ""

    def _show_change_summary(self, modified_modules: List, name1: str, name2: str):
        """Show a comprehensive summary of all changes found."""
        if not modified_modules:
            return

        self.console.print("[bold]📋 Change Summary[/bold]\n")

        # First, detect global connection changes
        connection_swap_summary = self._detect_global_connection_changes(modified_modules)
        if connection_swap_summary:
            self.console.print(connection_swap_summary)
            self.console.print()

        # Analyze the types of changes
        router_changes = []
        module_changes = []
        related_changes = {}  # Track modules that are related through router relationships

        for mod1, mod2 in modified_modules:
            mod_id = mod1.get("id", mod2.get("id", "unknown"))
            mod_type = mod1.get("module", mod2.get("module", "unknown"))
            mod_name = self._get_module_display_name(mod1) or self._get_module_display_name(mod2)

            if mod_type == "builtin:BasicRouter":
                # This is a router change - check if it contains other changed modules
                router_changes.append(
                    {
                        "id": mod_id,
                        "name": mod_name,
                        "changes": self._identify_functional_changes(mod1, mod2),
                    }
                )

                # Check if this router contains modules that are also in the changed list
                routes1 = mod1.get("routes", [])
                routes2 = mod2.get("routes", [])
                contained_modules = set()

                # Extract all module IDs from router routes
                def extract_route_module_ids(routes):
                    ids = set()
                    for route in routes:
                        for flow_module in route.get("flow", []):
                            ids.add(flow_module.get("id"))
                    return ids

                contained_modules.update(extract_route_module_ids(routes1))
                contained_modules.update(extract_route_module_ids(routes2))

                related_changes[mod_id] = contained_modules
            else:
                module_changes.append(
                    {
                        "id": mod_id,
                        "name": mod_name,
                        "type": mod_type,
                        "changes": self._identify_functional_changes(mod1, mod2),
                    }
                )

        # Group related changes
        standalone_changes = []
        grouped_changes = []

        for module_change in module_changes:
            mod_id = module_change["id"]
            is_contained = False

            # Check if this module is contained within a changed router
            for router_id, contained_ids in related_changes.items():
                if mod_id in contained_ids:
                    # Find the router change that contains this module
                    router_change = next(
                        (rc for rc in router_changes if rc["id"] == router_id), None
                    )
                    if router_change:
                        grouped_changes.append(
                            {
                                "type": "router_with_module",
                                "router": router_change,
                                "module": module_change,
                            }
                        )
                        is_contained = True
                        break

            if not is_contained:
                standalone_changes.append(module_change)

        # Display the summary
        total_functional_changes = len(grouped_changes) + len(standalone_changes)

        self.console.print(
            f"[bold cyan]Total functional changes: {total_functional_changes}[/bold cyan]\n"
        )

        # Show grouped changes (router + contained module)
        for i, grouped in enumerate(grouped_changes, 1):
            router = grouped["router"]
            module = grouped["module"]

            # Check if this is primarily a connection change
            is_connection_change = any(
                "Connection swapped:" in change for change in module["changes"]
            )

            if is_connection_change:
                self.console.print(f"[yellow]{i}. Connection Change in Router Flow:[/yellow]")
                self.console.print(f"   📍 Router: {router['name']} (ID: {router['id']})")
                self.console.print(
                    f"   📍 Affected Module: {module['name']} ({module['type']}, ID: {module['id']})"
                )

                # Show only connection changes
                for change in module["changes"]:
                    if "Connection swapped:" in change:
                        self.console.print(f"   {change}")
                        break
            else:
                self.console.print(f"[yellow]{i}. Router-Module Change:[/yellow]")
                self.console.print(f"   📍 Router: {router['name']} (ID: {router['id']})")
                self.console.print(
                    f"   📍 Affected Module: {module['name']} ({module['type']}, ID: {module['id']})"
                )
                self.console.print(f"   🔄 Nature of Change:")

                # Show the most relevant changes (prefer router-specific for filter changes)
                relevant_changes = router["changes"] if router["changes"] else module["changes"]
                for change in relevant_changes:
                    self.console.print(f"      • {change}")
            self.console.print()

        # Show standalone changes
        for i, change in enumerate(standalone_changes, len(grouped_changes) + 1):
            self.console.print(f"[yellow]{i}. Standalone Module Change:[/yellow]")
            self.console.print(
                f"   📍 Module: {change['name']} ({change['type']}, ID: {change['id']})"
            )
            self.console.print(f"   🔄 Nature of Change:")
            for ch in change["changes"]:
                self.console.print(f"      • {ch}")
            self.console.print()

        # Show routers that changed but don't have associated module changes
        standalone_routers = [
            rc
            for rc in router_changes
            if rc["id"] not in [gc["router"]["id"] for gc in grouped_changes]
        ]

        for i, router in enumerate(standalone_routers, total_functional_changes + 1):
            self.console.print(f"[yellow]{i}. Router-Only Change:[/yellow]")
            self.console.print(f"   📍 Router: {router['name']} (ID: {router['id']})")
            self.console.print(f"   🔄 Nature of Change:")
            for change in router["changes"]:
                self.console.print(f"      • {change}")
            self.console.print()

    def _analyze_mapper_changes(self, mapper1: Dict, mapper2: Dict) -> List[str]:
        """Analyze detailed changes in mapper configuration."""
        changes = []

        all_keys = set(mapper1.keys()) | set(mapper2.keys())
        changed_keys = []
        added_keys = []
        removed_keys = []

        for key in all_keys:
            val1 = mapper1.get(key)
            val2 = mapper2.get(key)

            if val1 is None and val2 is not None:
                added_keys.append(key)
            elif val1 is not None and val2 is None:
                removed_keys.append(key)
            elif val1 != val2:
                changed_keys.append(key)

        if added_keys:
            changes.append(
                f"Mapper: {len(added_keys)} field(s) added ({', '.join(added_keys[:3])}{'...' if len(added_keys) > 3 else ''})"
            )

        if removed_keys:
            changes.append(
                f"Mapper: {len(removed_keys)} field(s) removed ({', '.join(removed_keys[:3])}{'...' if len(removed_keys) > 3 else ''})"
            )

        if changed_keys:
            # For changed keys, provide more detail about content changes
            content_changes = []
            for key in changed_keys[:3]:  # Show details for first 3 changes
                val1 = mapper1.get(key)
                val2 = mapper2.get(key)
                change_desc = self._describe_value_change(key, val1, val2)
                if change_desc:
                    content_changes.append(change_desc)

            if content_changes:
                changes.extend(content_changes)
            else:
                changes.append(
                    f"Mapper: {len(changed_keys)} field(s) modified ({', '.join(changed_keys[:3])}{'...' if len(changed_keys) > 3 else ''})"
                )

        return changes

    def _analyze_parameter_changes(self, params1: Any, params2: Any) -> List[str]:
        """Analyze detailed changes in parameters."""
        changes = []

        if isinstance(params1, dict) and isinstance(params2, dict):
            all_keys = set(params1.keys()) | set(params2.keys())
            changed_keys = [k for k in all_keys if params1.get(k) != params2.get(k)]

            if changed_keys:
                changes.append(
                    f"Parameters: {len(changed_keys)} setting(s) modified ({', '.join(changed_keys[:3])}{'...' if len(changed_keys) > 3 else ''})"
                )
        else:
            changes.append("Parameters: Configuration structure changed")

        return changes

    def _get_detailed_module_changes(self, norm1: Dict, norm2: Dict) -> List[str]:
        """Get detailed analysis of module changes when no major section changes detected."""
        changes = []

        # Compare all top-level keys
        all_keys = set(norm1.keys()) | set(norm2.keys())

        for key in all_keys:
            val1 = norm1.get(key)
            val2 = norm2.get(key)

            if val1 != val2:
                change_desc = self._describe_value_change(key, val1, val2)
                if change_desc:
                    changes.append(change_desc)

        # If no detailed changes found, fall back to generic message
        if not changes:
            changes.append("Internal configuration modified")

        return changes

    def _describe_value_change(self, key: str, val1: Any, val2: Any) -> Optional[str]:
        """Describe how a specific value has changed."""
        if val1 is None and val2 is not None:
            return f"{key}: Added"
        elif val1 is not None and val2 is None:
            return f"{key}: Removed"
        elif isinstance(val1, str) and isinstance(val2, str):
            # For string changes, detect common patterns
            if len(val1) > 100 and len(val2) > 100:
                # Long strings - look for content patterns
                if self._detect_content_pattern_change(val1, val2):
                    pattern_desc = self._detect_content_pattern_change(val1, val2)
                    return f"{key}: {pattern_desc}"
                else:
                    return f"{key}: Content modified ({len(val1)} → {len(val2)} chars)"
            else:
                # Short strings - show actual change
                return f"{key}: '{val1}' → '{val2}'"
        elif isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            return f"{key}: {val1} → {val2}"
        elif isinstance(val1, bool) and isinstance(val2, bool):
            return f"{key}: {val1} → {val2}"
        elif isinstance(val1, (list, dict)) and isinstance(val2, (list, dict)):
            if isinstance(val1, list) and isinstance(val2, list):
                return f"{key}: List modified ({len(val1)} → {len(val2)} items)"
            else:
                return f"{key}: Structure modified"
        else:
            return f"{key}: Value changed"

    def _detect_content_pattern_change(self, str1: str, str2: str) -> Optional[str]:
        """Detect generic content type changes."""
        # Check for HTML content changes
        if "<html>" in str1 and "<html>" in str2:
            return "HTML template modified"

        # Check for JSON structure changes
        if str1.strip().startswith("{") and str2.strip().startswith("{"):
            return "JSON configuration modified"

        # For any other text content
        if isinstance(str1, str) and isinstance(str2, str):
            return "text content modified"

        return None


def test_diff():
    """Test function to compare specific files."""
    diff_tool = FusionDiff()
    diff_tool.console = Console()
    diff_tool.parser = BlueprintParser()
    diff_tool.analyzer = BlueprintAnalyzer()

    # Load blueprints
    directory = Path("blueprints")
    diff_tool._load_blueprints(directory)

    print(f"Found {len(diff_tool.blueprints)} blueprints:")
    for key, blueprint in diff_tool.blueprints.items():
        print(f"  - {key}")

    # Test with v32 and v33 if they exist (now using path-based keys)
    v32_key = "diff/blueprint-14926-v32"
    v33_key = "diff/blueprint-14926-v33"
    v35_key = "diff/blueprint-14926-v35"

    if v32_key in diff_tool.blueprints and v33_key in diff_tool.blueprints:
        print(f"\nComparing {v32_key} vs {v33_key}:")
        bp1 = diff_tool.blueprints[v32_key]
        bp2 = diff_tool.blueprints[v33_key]
        diff_tool._compare_blueprints(bp1, bp2)

    # Also test v33 vs v35 for more differences
    if v33_key in diff_tool.blueprints and v35_key in diff_tool.blueprints:
        print("\n" + "=" * 80)
        print(f"Comparing {v33_key} vs {v35_key}:")
        bp1 = diff_tool.blueprints[v33_key]
        bp2 = diff_tool.blueprints[v35_key]
        diff_tool._compare_blueprints(bp1, bp2)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Compare Fusion blueprint scenarios")
    parser.add_argument("directory", type=Path, help="Directory containing blueprint JSON files")
    parser.add_argument("--test", action="store_true", help="Run test comparison")

    args = parser.parse_args()

    if args.test:
        test_diff()
        return 0

    if not args.directory.exists():
        print(f"Error: Directory {args.directory} does not exist")
        return 1

    diff_tool = FusionDiff()
    diff_tool.run(args.directory)

    return 0


if __name__ == "__main__":
    exit(main())
