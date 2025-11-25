"""Unified rendering system for CLI commands."""

import os
import platform
import subprocess
from datetime import datetime
from pathlib import Path

import click

from tekmera.reporting.common.types import BaseReport, ReportFormat

from .formatters import get_formatter


def render_and_output(report: BaseReport, format_type: str, base_filename: str = None) -> None:
    """Unified function to render reports and handle output.

    Args:
        report: The report object to render
        format_type: Output format ("table", "json", "html")
        base_filename: Base filename for file output (without extension)
    """
    # Convert string format to enum
    if format_type == "table":
        format_enum = ReportFormat.TABLE
    elif format_type == "json":
        format_enum = ReportFormat.JSON
    elif format_type == "html":
        format_enum = ReportFormat.HTML
    else:
        valid_formats = ["table", "json", "html"]
        raise ValueError(
            f"Unsupported format: {format_type}\nValid formats: {', '.join(valid_formats)}"
        )

    # Get the appropriate formatter
    try:
        formatter = get_formatter(report.metadata.report_type, format_enum)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        return

    # Render the report
    rendered_output = formatter.render(report)

    # Handle output
    if formatter.should_write_to_file():
        # Write to file and open it
        output_path = _create_output_path(base_filename, formatter.get_file_extension())

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered_output)

        click.echo(
            f"{report.metadata.report_type.value.title()} {format_enum.value.upper()} report generated: {output_path}"
        )

        # Auto-open the file
        _open_file(str(output_path))

    else:
        # Write to stdout
        click.echo(rendered_output)


def _create_output_path(base_filename: str, extension: str) -> Path:
    """Create output file path with reports directory."""
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    if base_filename:
        # Use provided base filename
        filename = f"{base_filename}{extension}"
    else:
        # Use timestamp-based filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}{extension}"

    return reports_dir / filename


def _open_file(file_path: str):
    """Open file with the default system application."""
    try:
        if platform.system() == "Darwin":  # macOS
            subprocess.run(["open", file_path], check=True)
        elif platform.system() == "Windows":  # Windows
            os.startfile(file_path)
        else:  # Linux and others
            subprocess.run(["xdg-open", file_path], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError, AttributeError):
        # If opening fails, just continue silently
        pass


def _simplify_blueprint_name(name: str) -> str:
    """Simplify blueprint name for file naming."""
    # Basic cleaning
    simplified = (
        name.replace(" ", "_")
        .replace("/", "_")
        .replace("|", "_")
        .replace(":", "_")
        .replace(">", "_")
    )

    # Remove common prefixes
    for prefix in [
        "FUS001",
        "FUS002",
        "FUS003",
        "FUS004",
        "FUS005",
        "FUS006",
        "FUS007",
        "FUS008",
        "FUS009",
        "FUS010",
        "FUS011",
        "FUS012",
        "FUS013",
        "FUS014",
        "FUS015",
        "FUS016",
        "FUS017",
        "FUS018",
        "FUS019",
        "FUS020",
        "FUS",
        "MAKE",
        "Blueprint_",
        "Scenario_",
        "Template_",
    ]:
        if simplified.startswith(prefix):
            simplified = simplified[len(prefix) :]
            # Clean up leading separators
            while simplified.startswith(("_", "-", ".", " ")):
                simplified = simplified[1:]
            break

    # Remove version suffixes like v1.2, v2.1, V1.2, etc.
    import re

    simplified = re.sub(r"_?[vV]\d+[\.\d]*$", "", simplified)

    # Intelligent truncation - try to preserve meaningful parts
    if len(simplified) > 35:
        # Split on underscores and try to keep key parts
        parts = simplified.split("_")
        if len(parts) > 1:
            # Keep first and last meaningful parts
            key_parts = []
            current_length = 0

            # Always include first part if it's meaningful
            if parts[0] and len(parts[0]) > 2:
                key_parts.append(parts[0])
                current_length = len(parts[0])

            # Add middle parts if they fit
            for part in parts[1:-1]:
                if current_length + len(part) + 1 <= 25:  # +1 for underscore
                    key_parts.append(part)
                    current_length += len(part) + 1
                else:
                    # Skip long middle parts but indicate truncation
                    if "..." not in key_parts:
                        key_parts.append("...")
                    break

            # Always try to include last part if it's meaningful
            last_part = parts[-1]
            if (
                last_part and len(last_part) > 2 and current_length + len(last_part) + 4 <= 35
            ):  # +4 for _...
                if key_parts[-1] == "...":
                    key_parts.append(last_part)
                else:
                    key_parts.append(last_part)

            simplified = "_".join(key_parts)
        else:
            # Single long string, truncate intelligently
            simplified = simplified[:32] + "..."

    return simplified
