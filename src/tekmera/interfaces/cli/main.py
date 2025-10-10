#!/usr/bin/env python3
"""
Main CLI entry point for Tekmera Fusion Explorer
"""
import click
from pathlib import Path

from .interactive import InteractiveCLI


@click.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--premium', is_flag=True, help='Enable premium features')
@click.version_option(version='0.1.0', prog_name='tekmera-fusion-explorer')
def main(directory: str, premium: bool):
    """
    Tekmera Fusion Explorer - Diagnostic CLI for Fusion blueprints
    
    Analyze exported Workfront Fusion blueprint JSON files with interactive
    exploration, governance auditing, and AI-powered insights.
    
    DIRECTORY: Path to directory containing blueprint JSON files
    """
    directory_path = Path(directory)
    
    # Launch interactive CLI
    cli = InteractiveCLI(premium_license=premium)
    cli.start(directory_path)


if __name__ == '__main__':
    main()