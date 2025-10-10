"""
Interactive Live Scenario Walkthrough for Workfront Fusion blueprint flow analysis
"""
from pathlib import Path
from typing import Dict, List, Any
from InquirerPy import inquirer
from InquirerPy.separator import Separator
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from parser import BlueprintParser
from flow_walker import FlowWalker


class TraceInterface:
    """Interactive interface for live scenario walkthroughs."""
    
    def __init__(self):
        self.console = Console()
        self.parser = BlueprintParser()
        self.walker = FlowWalker()
        self.blueprints = {}
        self.loaded = False
    
    def start(self, directory: Path, specific_scenario: str = None):
        """Start the interactive live scenario walkthrough session.
        
        Args:
            directory: Path to directory containing blueprints
            specific_scenario: If provided, walk through this specific scenario directly
        """
        self.console.print("\n🎥 [bold blue]Live Scenario Walkthrough[/bold blue]")
        self.console.print("Interactive step-by-step exploration of scenario execution paths.\n")
        
        # Load blueprints
        self._load_blueprints(directory)
        
        if not self.blueprints:
            self.console.print("[red]No valid blueprint files found.[/red]")
            return
        
        # If specific scenario provided, walk through it directly
        if specific_scenario and specific_scenario in self.blueprints:
            self._walk_specific_scenario(specific_scenario)
            return
        
        # Main menu loop for multi-scenario mode
        while True:
            try:
                action = self._main_menu()
                if action == "quit":
                    break
                elif action == "walk_scenario":
                    self._walk_scenario()
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Goodbye![/yellow]")
                break
    
    def _load_blueprints(self, directory: Path):
        """Load all blueprint files from directory and subfolders."""
        self.blueprints = {}
        # Recursively find all JSON files
        json_files = list(directory.rglob('*.json'))
        
        for json_file in json_files:
            try:
                blueprint_data = self.parser.load_blueprint(json_file)
                
                # Extract scenario name correctly for both structures
                if 'blueprint' in blueprint_data:
                    scenario_name = blueprint_data['blueprint'].get('name', json_file.stem)
                else:
                    scenario_name = blueprint_data.get('name', json_file.stem)
                
                # Create a unique key that includes relative path
                relative_path = json_file.relative_to(directory)
                blueprint_key = str(relative_path.with_suffix(''))  # Remove .json extension
                
                self.blueprints[blueprint_key] = {
                    'filename': json_file.stem,
                    'scenario_name': scenario_name,
                    'file_path': json_file,
                    'relative_path': relative_path,
                    'data': blueprint_data
                }
            except Exception as e:
                self.console.print(f"[red]Warning: Could not load {json_file.name}: {e}[/red]")
    
    def _main_menu(self) -> str:
        """Display main live walkthrough menu."""
        choices = [
            {"name": "🎥 Start live scenario walkthrough", "value": "walk_scenario"},
            Separator(),
            {"name": "❌ Quit", "value": "quit"}
        ]
        
        return inquirer.select(
            message="What would you like to do?",
            choices=choices
        ).execute()
    
    def _walk_scenario(self):
        """Interactive live scenario walkthrough (multi-scenario mode)."""
        # Select scenario
        scenario_choices = []
        for key, blueprint in self.blueprints.items():
            scenario_name = blueprint['scenario_name']
            filename = blueprint['filename']
            scenario_choices.append({
                "name": f"{scenario_name} ({filename}.json)",
                "value": key
            })
        
        scenario_choices.append(Separator())
        scenario_choices.append({"name": "← Back", "value": "back"})
        
        selected_scenario = inquirer.select(
            message="Select a scenario for live walkthrough:",
            choices=scenario_choices
        ).execute()
        
        if selected_scenario == "back":
            return
        
        self._walk_specific_scenario(selected_scenario)
    
    def _walk_specific_scenario(self, scenario_key: str):
        """Start live walkthrough for a specific scenario."""
        blueprint_data = self.blueprints[scenario_key]['data']
        
        # Start the interactive live walkthrough
        self.walker.start_walkthrough(blueprint_data)