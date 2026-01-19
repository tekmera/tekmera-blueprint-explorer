"""
Main CLI entry point with projection commands.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import click

from ..._version import get_version_string
from ...functions import project
from ...functions.meta.types import UnsupportedPlatformError
from .formatters.table import format_result
from .render import _simplify_blueprint_name, render_and_output


def load_blueprint(file_path: str) -> Dict[str, Any]:
    """Load blueprint JSON from file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{file_path}': {e}")
        sys.exit(1)


def load_blueprints_from_paths(paths: List[str], max_depth: int = 3) -> List[Dict[str, Any]]:
    """Load blueprints from files and/or directories (up to 3 levels deep)."""
    blueprints = []

    for path_str in paths:
        path = Path(path_str)

        if path.is_file():
            # Single file
            if path.suffix.lower() == ".json":
                blueprints.append(load_blueprint(str(path)))
            else:
                print(f"Warning: Skipping non-JSON file '{path}'")

        elif path.is_dir():
            # Directory - scan for JSON files with depth limit
            # Build pattern with depth limit
            patterns = ["*.json"]  # Current directory
            for depth in range(1, max_depth + 1):
                patterns.append("*/" * depth + "*.json")

            json_files = []
            for pattern in patterns:
                json_files.extend(path.glob(pattern))
            # Remove duplicates and sort
            json_files = sorted(set(json_files))

            if not json_files:
                print(f"Warning: No JSON files found in directory '{path}'")
                continue

            for json_file in sorted(json_files):
                blueprints.append(load_blueprint(str(json_file)))

        else:
            print(f"Error: Path '{path}' not found")
            sys.exit(1)

    if not blueprints:
        print("Error: No valid blueprint files found")
        sys.exit(1)

    return blueprints


@click.group()
@click.version_option(version=get_version_string(), prog_name="tekmera")
def cli():
    """Tekmera Explorer - Blueprint Analysis Tool

    \b
    PATHS can be files or directories. Directories scanned 3 levels deep.
    Platform auto-detected. Available formats: table (default), json, html
    """


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.argument("queries", nargs=-1, required=True, type=str)
@click.option("--case-sensitive", "-c", is_flag=True, help="Case sensitive search")
@click.option("--regex", "-r", is_flag=True, help="Treat query as regex pattern")
@click.option(
    "--format", type=click.Choice(["table", "json", "html"]), default="table", help="Output format"
)
def search(path, queries, case_sensitive, regex, format):
    """Search for text content across blueprint components

    PATH: Single blueprint file or directory to search
    QUERIES: One or more search terms (OR logic)

    Examples:
      tekmera search ./blueprints/ "PI43"
      tekmera search blueprint.json "term1" "term2" "term3"
      tekmera search ./blueprints/ "PI\\d+" --regex
    """
    blueprints = load_blueprints_from_paths([path])

    try:
        result = project(
            "blueprints",
            "search",
            "text_content",
            blueprints,
            queries=queries,
            case_sensitive=case_sensitive,
            regex=regex,
        )
        format_result(result, format)
    except UnsupportedPlatformError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("blueprint_path", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--format", type=click.Choice(["table", "json", "html"]), default="table", help="Output format"
)
def report(blueprint_path, format):
    """Generate one-page summary report for a single blueprint file"""
    blueprint = load_blueprint(blueprint_path)

    try:
        # Use new reporting system to generate summary report
        from ...reporting.summary import generate_summary_report

        result = generate_summary_report(blueprint)

        # Use unified rendering system
        blueprint_name = _simplify_blueprint_name(result.data.blueprint_name)
        render_and_output(result.data, format, f"{blueprint_name}_report")

    except UnsupportedPlatformError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("blueprint1_path", type=click.Path(exists=True, dir_okay=False))
@click.argument("blueprint2_path", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--format", type=click.Choice(["table", "json", "html"]), default="table", help="Output format"
)
def diff(blueprint1_path, blueprint2_path, format):
    """Compare two blueprint files and generate diff report"""
    try:
        # Load both blueprints
        blueprint1 = load_blueprint(blueprint1_path)
        blueprint2 = load_blueprint(blueprint2_path)

        # Use new reporting system for diff reports
        from ...reporting.diff import generate_diff_report

        # Generate diff report
        result = generate_diff_report(blueprint1, blueprint2)

        # Use unified rendering system with timestamp-based filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        render_and_output(result.data, format, f"diff_{timestamp}")

    except Exception as e:
        click.echo(f"Error generating diff report: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--platform",
    type=click.Choice(["workfront_fusion", "make_com"]),
    default="workfront_fusion",
    help="Platform for sample report",
)
@click.option(
    "--format", type=click.Choice(["table", "json", "html"]), default="table", help="Output format"
)
def demo(platform, format):
    """Generate sample report for demos and documentation"""
    from ...functions.meta.types import Platform
    from ...reporting.summary.sample import create_sample_report

    # Convert string to enum
    platform_enum = (
        Platform.WORKFRONT_FUSION if platform == "workfront_fusion" else Platform.MAKE_COM
    )

    try:
        # Generate sample report
        result = create_sample_report(platform_enum)

        # Use unified rendering system
        sample_filename = f"Sample_{platform.title()}_Report"
        render_and_output(result.data, format, sample_filename)

    except Exception as e:
        click.echo(f"Error generating sample report: {e}", err=True)
        sys.exit(1)


def main():
    """Main entry point"""
    cli()


if __name__ == "__main__":
    main()
