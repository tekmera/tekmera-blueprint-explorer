"""
Centralized blueprint loading utility for consistent loading across all CLI modules
"""

from pathlib import Path
from typing import Any, Dict

from rich.console import Console

from ..core.parser import BlueprintParser


class BlueprintLoader:
    """Centralized utility for loading and processing Fusion blueprint JSON files."""

    def __init__(self, console: Console = None):
        self.parser = BlueprintParser()
        self.console = console or Console()

    def load_blueprints(
        self, directory: Path, include_modules: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """
        Load all blueprint files from the specified directory and subfolders.

        Args:
            directory: Directory path to search for blueprint JSON files
            include_modules: Whether to parse and include module information

        Returns:
            Dictionary mapping blueprint keys to blueprint data containing:
            - filename: Base filename without extension
            - scenario_name: Extracted scenario name from blueprint
            - file_path: Full path to the JSON file
            - data: Parsed blueprint data
            - modules: List of modules (if include_modules=True)
            - module_count: Number of modules (if include_modules=True)
        """
        blueprints = {}

        # Recursively find all JSON files
        json_files = list(directory.rglob("*.json"))

        if not json_files:
            return blueprints

        self.console.print("📂 Loading blueprints (including subfolders)...")

        for json_file in json_files:
            try:
                blueprint_data = self.parser.load_blueprint(json_file)

                # Extract scenario name correctly for both structures
                if "blueprint" in blueprint_data:
                    # Diff blueprint structure: name is in blueprint.name
                    scenario_name = blueprint_data["blueprint"].get("name", json_file.stem)
                    data = blueprint_data["blueprint"]
                else:
                    # Regular blueprint structure: name is at root level
                    scenario_name = blueprint_data.get("name", json_file.stem)
                    data = blueprint_data

                # Create blueprint info dictionary
                blueprint_info = {
                    "filename": json_file.stem,
                    "scenario_name": scenario_name,
                    "file_path": json_file,
                    "data": data,
                }

                # Add module information if requested
                if include_modules:
                    modules = self.parser.get_modules(data)
                    blueprint_info["modules"] = modules
                    blueprint_info["module_count"] = len(modules)

                # Create a unique key that includes relative path
                relative_path = json_file.relative_to(directory)
                key = str(relative_path.with_suffix(""))

                blueprints[key] = blueprint_info

            except Exception as e:
                self.console.print(
                    f"[yellow]Warning: Could not load {json_file.name}: {e}[/yellow]"
                )
                continue

        self.console.print(f"✅ Loaded {len(blueprints)} blueprints")
        return blueprints

    def load_single_blueprint(self, file_path: Path) -> Dict[str, Any]:
        """
        Load a single blueprint file and return its processed information.

        Args:
            file_path: Path to the blueprint JSON file

        Returns:
            Dictionary containing blueprint information

        Raises:
            Exception: If the blueprint cannot be loaded or parsed
        """
        blueprint_data = self.parser.load_blueprint(file_path)

        # Extract scenario name correctly for both structures
        if "blueprint" in blueprint_data:
            # Diff blueprint structure: name is in blueprint.name
            scenario_name = blueprint_data["blueprint"].get("name", file_path.stem)
            data = blueprint_data["blueprint"]
        else:
            # Regular blueprint structure: name is at root level
            scenario_name = blueprint_data.get("name", file_path.stem)
            data = blueprint_data

        # Get module information
        modules = self.parser.get_modules(data)

        return {
            "filename": file_path.stem,
            "scenario_name": scenario_name,
            "file_path": file_path,
            "data": data,
            "modules": modules,
            "module_count": len(modules),
        }

    def get_scenario_summary(self, blueprints: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of loaded blueprints.

        Args:
            blueprints: Dictionary of loaded blueprints from load_blueprints()

        Returns:
            Dictionary containing summary statistics
        """
        total_blueprints = len(blueprints)
        total_modules = sum(bp.get("module_count", 0) for bp in blueprints.values())

        scenarios_by_name = {}
        for bp in blueprints.values():
            name = bp["scenario_name"]
            if name not in scenarios_by_name:
                scenarios_by_name[name] = 0
            scenarios_by_name[name] += 1

        return {
            "total_blueprints": total_blueprints,
            "total_modules": total_modules,
            "unique_scenario_names": len(scenarios_by_name),
            "scenarios_by_name": scenarios_by_name,
            "avg_modules_per_blueprint": (
                total_modules / total_blueprints if total_blueprints > 0 else 0
            ),
        }
