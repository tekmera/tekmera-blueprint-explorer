#!/usr/bin/env python3
"""
Workfront Fusion Blueprint Analyzer CLI
"""
import click
from pathlib import Path
from interactive_cli import InteractiveCLI


@click.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def analyze(directory):
    """Analyze Workfront Fusion blueprint JSON files in a directory."""
    directory_path = Path(directory)
    
    # Launch interactive mode selection
    interactive_cli = InteractiveCLI()
    interactive_cli.start(directory_path)




if __name__ == '__main__':
    analyze()