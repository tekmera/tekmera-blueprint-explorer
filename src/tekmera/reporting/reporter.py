"""
Report generation and formatting
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from InquirerPy import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class Reporter:
    """Handles formatting and output of analysis results."""

    def __init__(self):
        self.console = Console()
        self.last_report_content = None

    def generate_report(self, results: List[Dict[str, Any]]) -> None:
        """
        Generate and display analysis report with scrollable paging.

        Args:
            results: List of analysis result dictionaries
        """
        total_scenarios = len(results)
        total_modules = sum(r["module_count"] for r in results)
        all_module_types = set()
        all_de_fields = set()

        # Collect all data first
        for result in results:
            all_module_types.update(result["module_types"])
            all_de_fields.update(result["workfront_fields"])

        # Build report content as a string
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("WORKFRONT FUSION BLUEPRINT ANALYSIS REPORT")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 60)
        report_lines.append("")

        # Individual scenario details
        for result in results:
            report_lines.append(f"Scenario: {result['scenario_name']}")
            report_lines.append(f"File: {result['filename']}.json")
            report_lines.append(f"Modules: {result['module_count']}")

            if result["module_types"]:
                report_lines.append("Module Types:")
                for module_type in result["module_types"]:
                    report_lines.append(f"  - {module_type}")

            if result["workfront_fields"]:
                report_lines.append("Workfront Fields:")
                for field in sorted(result["workfront_fields"]):
                    report_lines.append(f"  - {field}")

            report_lines.append("-" * 40)
            report_lines.append("")

        # Summary section
        report_lines.append("SUMMARY")
        report_lines.append("-" * 20)
        report_lines.append(f"Total Scenarios: {total_scenarios}")
        report_lines.append(f"Total Modules: {total_modules}")
        report_lines.append(f"Unique Module Types: {len(all_module_types)}")
        report_lines.append(f"Unique Workfront Fields: {len(all_de_fields)}")

        if all_module_types:
            report_lines.append("")
            report_lines.append("All Module Types Found:")
            for module_type in sorted(all_module_types):
                report_lines.append(f"  - {module_type}")

        if all_de_fields:
            report_lines.append("")
            report_lines.append("All Workfront Fields Found:")
            for field in sorted(all_de_fields):
                report_lines.append(f"  - {field}")

        # Store report content
        self.last_report_content = "\n".join(report_lines)

        # Ask if user wants to export BEFORE displaying
        export = inquirer.confirm(
            message="Export report to file instead of viewing?", default=False
        ).execute()

        if export:
            self._export_report()
        else:
            # Display with pager for scrolling
            with self.console.pager():
                self.console.print(self.last_report_content)

    def _offer_export(self) -> None:
        """Offer to export the report to a file."""
        if not self.last_report_content:
            return

        export = inquirer.confirm(message="Export report to file?", default=False).execute()

        if export:
            self._export_report()

    def _export_report(self) -> None:
        """Export the last generated report to a timestamped file."""
        if not self.last_report_content:
            self.console.print("[red]No report content to export[/red]")
            return

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report-{timestamp}.txt"

        try:
            # Write to current directory
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.last_report_content)

            # Get file info for display
            file_path = Path(filename).resolve()
            file_size = file_path.stat().st_size

            # Format file size
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"

            self.console.print(f"[green]✅ Static analysis report exported successfully![/green]")
            self.console.print(f"[cyan]📄 File: {filename}[/cyan]")
            self.console.print(f"[cyan]📁 Location: {file_path.parent}[/cyan]")
            self.console.print(f"[cyan]📊 Size: {size_str}[/cyan]")

        except Exception as e:
            self.console.print(f"[red]❌ Failed to export report: {str(e)}[/red]")
