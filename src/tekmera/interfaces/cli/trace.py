"""
Interactive Live Scenario Walkthrough for Workfront Fusion blueprint flow analysis
"""

from pathlib import Path

from InquirerPy import inquirer
from InquirerPy.separator import Separator

from ...analysis.flow_walker import FlowWalker
from ...utils.base_cli import InteractiveCLIBase


class TraceInterface(InteractiveCLIBase):
    """Interactive interface for live scenario walkthroughs."""

    def __init__(self):
        super().__init__(enable_search_display=False)  # Trace doesn't need search display
        self.walker = FlowWalker()

    def start(self, directory: Path, specific_scenario: str = None):
        """Start the interactive live scenario walkthrough session.

        Args:
            directory: Path to directory containing blueprints
            specific_scenario: If provided, walk through this specific scenario directly
        """
        self.display_welcome(
            "Live Scenario Walkthrough",
            "Interactive step-by-step exploration of scenario execution paths.",
        )

        # Load blueprints
        self.load_blueprints(directory, include_modules=True)

        if not self.blueprints:
            self.show_error("No valid blueprint files found")
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
                self.handle_keyboard_interrupt()
                break

    def _main_menu(self) -> str:
        """Display main live walkthrough menu."""
        choices = [
            {"name": "🎥 Start live scenario walkthrough", "value": "walk_scenario"},
            Separator(),
            {"name": "❌ Quit", "value": "quit"},
        ]

        return inquirer.select(message="What would you like to do?", choices=choices).execute()

    def _walk_scenario(self):
        """Interactive live scenario walkthrough (multi-scenario mode)."""
        # Select scenario
        scenario_choices = []
        for key, blueprint in self.blueprints.items():
            scenario_name = blueprint["scenario_name"]
            filename = blueprint["filename"]
            scenario_choices.append({"name": f"{scenario_name} ({filename}.json)", "value": key})

        scenario_choices.append(Separator())
        scenario_choices.append({"name": "← Back", "value": "back"})

        selected_scenario = inquirer.select(
            message="Select a scenario for live walkthrough:", choices=scenario_choices
        ).execute()

        if selected_scenario == "back":
            return

        self._walk_specific_scenario(selected_scenario)

    def _walk_specific_scenario(self, scenario_key: str):
        """Start live walkthrough for a specific scenario."""
        blueprint_data = self.blueprints[scenario_key]["data"]

        # Start the interactive live walkthrough
        self.walker.start_walkthrough(blueprint_data)
