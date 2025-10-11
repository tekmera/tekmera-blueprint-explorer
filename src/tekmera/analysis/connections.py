"""
Shared utilities for connection analysis and display.
"""

from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class ConnectionAnalyzer:
    """Centralized connection analysis service for Workfront Fusion blueprints."""

    def __init__(self):
        self.connection_labels = {}  # Map connection IDs to labels
        self.connection_types = {}  # Map connection IDs to types

    def find_connections_in_json(self, json_obj, path="") -> List[Tuple[int, str]]:
        """
        Recursively search for __IMTCONN__ references throughout JSON structure.

        Args:
            json_obj: JSON object to search
            path: Current path in the JSON structure

        Returns:
            List of tuples (connection_id, context_path)
        """
        connections = []

        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                current_path = f"{path}.{key}" if path else key

                # Check if this key contains __IMTCONN__
                if "__IMTCONN__" in str(key):
                    if isinstance(value, int):
                        connections.append((value, current_path))

                # Check if the value contains __IMTCONN__
                if isinstance(value, (int, str)) and "__IMTCONN__" in str(value):
                    try:
                        # Try to extract connection ID from value
                        if isinstance(value, int):
                            connections.append((value, current_path))
                        elif isinstance(value, str) and value.isdigit():
                            connections.append((int(value), current_path))
                    except (ValueError, TypeError):
                        pass

                # Recursively search nested objects
                connections.extend(self.find_connections_in_json(value, current_path))

        elif isinstance(json_obj, list):
            for i, item in enumerate(json_obj):
                current_path = f"{path}[{i}]" if path else f"[{i}]"
                connections.extend(self.find_connections_in_json(item, current_path))

        return connections

    def extract_connection_labels(self, blueprint_data: Dict[str, Any]) -> Dict[int, str]:
        """
        Extract connection labels from blueprint metadata.

        Args:
            blueprint_data: Blueprint JSON data

        Returns:
            Dictionary mapping connection IDs to labels
        """
        labels = {}

        # Method 1: From metadata.restore.__IMTCONN__<id>
        metadata = blueprint_data.get("metadata", {})
        restore = metadata.get("restore", {})

        for key, value in restore.items():
            if "__IMTCONN__" in key and isinstance(value, dict) and "label" in value:
                try:
                    connection_id = int(key.replace("__IMTCONN__", ""))
                    labels[connection_id] = value["label"]
                except (ValueError, TypeError):
                    continue

        # Method 2: From individual module metadata (main flow)
        modules = blueprint_data.get("flow", [])
        self._extract_labels_from_modules(modules, labels)

        # Method 3: From orphan modules
        metadata = blueprint_data.get("metadata", {})
        designer = metadata.get("designer", {})
        orphans = designer.get("orphans", [])

        # Handle nested orphan structure
        for orphan_group in orphans:
            if isinstance(orphan_group, list):
                self._extract_labels_from_modules(orphan_group, labels)
            elif isinstance(orphan_group, dict):
                self._extract_labels_from_modules([orphan_group], labels)

        return labels

    def _extract_labels_from_modules(self, modules, labels):
        """Helper method to extract connection labels from a list of modules."""
        if not isinstance(modules, list):
            return

        for module in modules:
            if not isinstance(module, dict):
                continue

            # Check parameters for connection references
            parameters = module.get("parameters", {})
            connection_id = parameters.get("__IMTCONN__")

            if connection_id:
                # Get label from metadata.restore.__IMTCONN__.label
                module_metadata = module.get("metadata", {})
                module_restore = module_metadata.get("restore", {})
                imtconn_data = module_restore.get("__IMTCONN__", {})

                if isinstance(imtconn_data, dict) and "label" in imtconn_data:
                    labels[connection_id] = imtconn_data["label"]

            # Check routes recursively
            if "routes" in module:
                for route in module["routes"]:
                    if "flow" in route:
                        self._extract_labels_from_modules(route["flow"], labels)

            # Check error handlers
            if "onerror" in module and isinstance(module["onerror"], list):
                self._extract_labels_from_modules(module["onerror"], labels)

    def determine_connection_type(
        self, module_type: str, connection_label: str = "", context: str = ""
    ) -> str:
        """
        Determine connection type based on module type, label, and context.

        Args:
            module_type: The module type string
            connection_label: Connection label if available
            context: Context where connection was found

        Returns:
            Connection type string
        """
        # Normalize inputs
        module_lower = module_type.lower()
        label_lower = connection_label.lower()
        context_lower = context.lower()

        # Service type mapping (comprehensive)
        service_mapping = {
            "workfront": "Workfront",
            "http": "HTTP",
            "json": "JSON",
            "webhook": "Webhook",
            "email": "Email",
            "ftp": "FTP",
            "sftp": "SFTP",
            "database": "Database",
            "mysql": "MySQL",
            "postgresql": "PostgreSQL",
            "mongodb": "MongoDB",
            "salesforce": "Salesforce",
            "sharepoint": "SharePoint",
            "dropbox": "Dropbox",
            "googledrive": "Google Drive",
            "onedrive": "OneDrive",
            "slack": "Slack",
            "teams": "Microsoft Teams",
            "jira": "Jira",
            "trello": "Trello",
            "github": "GitHub",
            "gitlab": "GitLab",
            "azure": "Azure",
            "aws": "AWS",
            "google": "Google",
        }

        # Check module type first
        for keyword, service_type in service_mapping.items():
            if keyword in module_lower:
                return service_type

        # Check connection label
        for keyword, service_type in service_mapping.items():
            if keyword in label_lower:
                return service_type

        # Check context
        for keyword, service_type in service_mapping.items():
            if keyword in context_lower:
                return service_type

        # Special checks for common patterns
        if any(term in module_lower for term in ["builtin", "tools", "util"]):
            return "Builtin"

        if any(term in label_lower for term in ["api", "rest", "soap"]):
            return "API"

        return "Unknown"

    def analyze_blueprint_connections(
        self, blueprint_data: Dict[str, Any], scenario_name: str
    ) -> Dict[str, Any]:
        """
        Comprehensive connection analysis for a single blueprint.

        Args:
            blueprint_data: Blueprint JSON data
            scenario_name: Name of the scenario

        Returns:
            Dictionary with connection analysis results
        """
        # Extract connection labels
        connection_labels = self.extract_connection_labels(blueprint_data)

        # Simple mapping for main flow modules - recursive search handles all connections
        module_id_map = {}
        main_flow = blueprint_data.get("flow", [])
        for i, module in enumerate(main_flow):
            if isinstance(module, dict):
                actual_id = module.get("id", f"module_{i+1}")
                module_id_map[i] = actual_id

        # Find all connections in the blueprint (this already includes orphans in metadata.designer.orphans)
        all_connections = self.find_connections_in_json(blueprint_data)

        # Group connections and analyze
        connections_data = defaultdict(list)
        connection_types = defaultdict(set)

        for connection_id, context in all_connections:
            connection_label = connection_labels.get(connection_id, f"Connection {connection_id}")

            # Improved module ID extraction for router paths
            actual_module_id = "Unknown"
            if "flow[" in context:
                import re

                # Extract all flow indices in the path (handles nested routers)
                flow_matches = re.findall(r"flow\[(\d+)\]", context)
                if flow_matches:
                    # Use the first (main) flow index for the base module ID
                    flow_index = int(flow_matches[0])
                    base_module_id = module_id_map.get(flow_index, f"Module_{flow_index+1}")

                    # If this is in a router route, add route information
                    if len(flow_matches) > 1:
                        # This connection is in a nested router structure
                        route_info = f"_Route_{'.'.join(flow_matches[1:])}"
                        actual_module_id = f"{base_module_id}{route_info}"
                    else:
                        actual_module_id = base_module_id
            elif "orphan" in context.lower():
                actual_module_id = "Orphan"

            # Determine connection type
            module_type = "unknown"
            if "workfront" in context.lower():
                module_type = "workfront"
            elif "http" in context.lower():
                module_type = "http"

            connection_type = self.determine_connection_type(module_type, connection_label, context)
            environment = classify_connection_environment(connection_label)

            connection_info = {
                "scenario_name": scenario_name,
                "module_type": module_type,
                "connection_type": connection_type,
                "environment": environment,
                "context": context,
                "module_id": actual_module_id,
                "is_orphan": "orphan" in context.lower(),
            }

            connections_data[connection_id].append(connection_info)
            connection_types[connection_type].add(connection_id)

        return {
            "connections": dict(connections_data),
            "connection_labels": connection_labels,
            "connection_types": {k: list(v) for k, v in connection_types.items()},
            "total_connections": len(connection_labels),
            "unique_connections": len(set(conn_id for conn_id, _ in all_connections)),
        }


def classify_connection_environment(connection_label: str) -> str:
    """
    Classify a connection as DEV or PROD based on its label.

    Args:
        connection_label: The connection label/name

    Returns:
        'DEV', 'PROD', or 'Unknown'
    """
    if not connection_label:
        return "Unknown"

    connection_lower = connection_label.lower()

    # Development connection keywords (including Workfront-specific patterns)
    dev_keywords = [
        "dev",
        "sandbox",
        "test",
        "staging",
        "demo",
        "preview",
        "sb01",
        "sb02",
        "sb03",
        "sb04",
        "sb05",
    ]

    # Check if connection label contains development keywords
    for keyword in dev_keywords:
        if keyword in connection_lower:
            return "DEV"

    # Production connections typically have 'my' as subdomain for Workfront
    if "my." in connection_lower or connection_lower.startswith("my"):
        return "PROD"

    # If no clear indicators, return Unknown
    return "Unknown"


def display_connection_table(
    console: Console,
    connections: Dict[str, List[Dict]],
    connection_labels: Dict[int, str] = None,
    title: str = "Connection Usage Analysis",
    show_labels: bool = False,
    show_environment: bool = False,
):
    """
    Display a formatted table of connection usage analysis.

    Args:
        console: Rich console for output
        connections: Dictionary mapping connection IDs to usage info
        connection_labels: Optional mapping of connection IDs to human-readable labels
        title: Table title
        show_labels: Whether to show connection labels instead of just IDs
        show_environment: Whether to show DEV/PROD environment classification
    """
    if not connections:
        console.print("[yellow]No connections found to display.[/yellow]")
        return

    # Create table
    table = Table(title=title)

    if show_labels and connection_labels:
        table.add_column("Connection", style="cyan", width=50)
    else:
        table.add_column("Connection ID", style="cyan", width=15)

    table.add_column("Type", style="magenta", width=10)
    if show_environment:
        table.add_column("Environment", style="bold red", justify="center", width=11)
    table.add_column("Usage Count", style="yellow", justify="right", width=11)
    table.add_column("Module IDs", style="cyan", width=25)
    table.add_column("Scenarios", style="green", width=25)

    # Populate table
    for conn_id, usages in sorted(connections.items()):
        scenarios = list(set(usage["scenario_name"] for usage in usages))
        module_types = list(set(usage["module_type"] for usage in usages))

        # Extract actual module IDs from usage data
        module_ids = []
        for usage in usages:
            actual_module_id = usage.get("module_id", "Unknown")
            # Convert to string to ensure we can join them
            module_ids.append(str(actual_module_id))

        # Remove duplicates and format
        unique_module_ids = list(set(module_ids))
        module_id_text = ", ".join(unique_module_ids[:3])
        if len(unique_module_ids) > 3:
            module_id_text += f" (+{len(unique_module_ids)-3} more)"

        # Get connection type from first usage
        connection_type = usages[0].get("connection_type", "Unknown") if usages else "Unknown"

        # Get environment classification if available
        environment = usages[0].get("environment", "Unknown") if usages else "Unknown"

        # Format scenario text
        scenario_text = ", ".join(scenarios[:1])  # Show fewer scenarios to save space
        if len(scenarios) > 1:
            scenario_text += f" (+{len(scenarios)-1} more)"

        # Determine connection display name
        if show_labels and connection_labels and conn_id in connection_labels:
            connection_display = f"{connection_labels[conn_id]}\n[dim](ID: {conn_id})[/dim]"
        else:
            connection_display = str(conn_id)

        # Build row data
        row_data = [connection_display, connection_type]
        if show_environment:
            # Color code the environment
            env_display = environment
            if environment.upper() == "DEV":
                env_display = f"[red]{environment}[/red]"
            elif environment.upper() == "PROD":
                env_display = f"[green]{environment}[/green]"
            row_data.append(env_display)
        row_data.extend(
            [str(len(unique_module_ids)), module_id_text, scenario_text]
        )  # Use unique count, no module_text

        table.add_row(*row_data)

    console.print(table)


def display_connection_warnings(console: Console, warnings: List[Dict[str, Any]]):
    """
    Display connection warnings in formatted panels.

    Args:
        console: Rich console for output
        warnings: List of warning dictionaries
    """
    if not warnings:
        return

    console.print("\n[bold yellow]⚠️  Connection Warnings:[/bold yellow]")

    for warning in warnings:
        severity_color = "red" if warning.get("severity") == "high" else "yellow"
        panel_title = f"[{severity_color}]{warning.get('connection_type', 'Unknown')} - {warning.get('type', 'Warning').title()}[/{severity_color}]"

        # Build warning content
        content_lines = [
            f"[bold]Message:[/bold] {warning.get('message', 'No message')}",
            f"[bold]Recommendation:[/bold] {warning.get('recommendation', 'No recommendation')}",
        ]

        if "connection_details" in warning:
            content_lines.append(
                f"[bold]Connections:[/bold] {', '.join(warning['connection_details'])}"
            )

        panel = Panel("\n".join(content_lines), title=panel_title, border_style=severity_color)
        console.print(panel)


def display_connection_summary(console: Console, connection_types: Dict[str, List[int]]):
    """
    Display a summary of connection types.

    Args:
        console: Rich console for output
        connection_types: Dictionary mapping connection types to lists of connection IDs
    """
    if not connection_types:
        return

    console.print("\n[bold]Connection Types Summary:[/bold]")
    for conn_type, conn_ids in connection_types.items():
        console.print(f"  [magenta]{conn_type}:[/magenta] {len(conn_ids)} connection(s)")
