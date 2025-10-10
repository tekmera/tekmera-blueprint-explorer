"""
Interactive CLI interface for Tekmera Fusion Explorer
"""
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from InquirerPy import inquirer
from InquirerPy.separator import Separator
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown

from ...core.parser import BlueprintParser
from ...core.analyzer import BlueprintAnalyzer
from ...reporting.reporter import Reporter
from ...governance import GovernanceChecker
from ...config.menu_system import menu_system, ExecResult
from ...infra.license import LicenseType, license_manager
from ...infra.licensing_utils import FeatureRegistry, execute_with_license_check
from .explorer import BlueprintExplorer
from .search import SearchInterface
from .trace import TraceInterface
from ...comparison.diff_engine import FusionDiff


class InteractiveCLI:
    """Main interactive CLI interface for the Fusion Blueprint Analyzer."""
    
    def __init__(self):
        self.console = Console()
        self.parser = BlueprintParser()
        self.analyzer = BlueprintAnalyzer()
        self.blueprints = {}
        self.directory_path = None
        
        # License is automatically detected from ~/.tekmera/license.json on startup
        # No manual override needed - users activate licenses with 'tekmera license activate'
        self.context = license_manager.get_context()
        
        # Initialize governance checks in menu system
        governance_checker = GovernanceChecker()
        menu_system.add_governance_checks(governance_checker)
    
    def start(self, directory: Path):
        """Start the interactive CLI session."""
        self.directory_path = directory
        
        # Display welcome banner
        self._display_welcome()
        
        # Load blueprints
        self._load_blueprints()
        
        if not self.blueprints:
            self.console.print("[red]❌ No valid blueprint files found in the specified directory.[/red]")
            return
        
        # Main interaction loop
        while True:
            try:
                choice = self._select_mode()
                if choice and choice.get("id") == "exit":
                    self.console.print("\n[yellow]👋 Goodbye![/yellow]")
                    break
                elif choice:
                    # Use menu system to resolve and execute
                    result = menu_system.resolve_and_execute(choice, self.context, self)
                    if result == ExecResult.PREMIUM_REQUIRED:
                        continue  # Premium prompt already shown, continue loop
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]👋 Goodbye![/yellow]")
                break
    
    def _display_welcome(self):
        """Display welcome banner and directory info."""
        welcome_text = Text()
        welcome_text.append("🔍 ", style="blue")
        welcome_text.append("Tekmera Fusion Explorer", style="bold blue")
        
        # Get detailed license information
        license_info = license_manager.get_license_info()
        if license_info['status'] == 'active':
            license_text = f"Pro ({license_info['edition']})"
            if license_info.get('days_remaining') is not None:
                days = license_info['days_remaining']
                if days <= 30:
                    license_text += f" - {days} days left"
        else:
            license_text = "Free"
        
        info_text = f"Directory: {self.directory_path}\nLicense: {license_text}"
        
        panel = Panel(
            f"{welcome_text}\n\n{info_text}",
            title="Welcome",
            expand=False,
            border_style="blue"
        )
        
        self.console.print("\n")
        self.console.print(panel)
        self.console.print()
    
    def _load_blueprints(self):
        """Load all blueprint files from the directory and subfolders."""
        self.blueprints = {}
        
        # Recursively find all JSON files
        json_files = list(self.directory_path.rglob('*.json'))
        
        if not json_files:
            return
        
        self.console.print("📂 Loading blueprints (including subfolders)...")
        
        for json_file in json_files:
            try:
                blueprint_data = self.parser.load_blueprint(json_file)
                
                # Extract scenario name correctly for both structures
                if 'blueprint' in blueprint_data:
                    # Diff blueprint structure: name is in blueprint.name
                    scenario_name = blueprint_data['blueprint'].get('name', json_file.stem)
                    data = blueprint_data['blueprint']
                else:
                    # Regular blueprint structure: name is at root level
                    scenario_name = blueprint_data.get('name', json_file.stem)
                    data = blueprint_data
                
                # Get module count using recursive parsing
                modules = self.parser.get_modules(data)
                
                # Create a unique key that includes relative path
                relative_path = json_file.relative_to(self.directory_path)
                blueprint_key = str(relative_path.with_suffix(''))  # Remove .json extension
                
                self.blueprints[blueprint_key] = {
                    'filename': json_file.stem,
                    'scenario_name': scenario_name,
                    'file_path': json_file,
                    'relative_path': relative_path,
                    'data': blueprint_data,
                    'module_count': len(modules)
                }
                
            except Exception as e:
                self.console.print(f"[yellow]⚠️  Could not load {json_file.name}: {e}[/yellow]")
        
        self.console.print(f"✅ Loaded {len(self.blueprints)} blueprint(s) from directory tree\n")
    
    def _select_mode(self) -> Optional[Dict[str, str]]:
        """Present mode selection menu using menu system."""
        has_premium = license_manager.has_premium()
        root_items = menu_system.get_root_items()
        choices = menu_system.to_inquirer_choices(root_items, has_premium)
        
        # Add exit option
        choices.append({"name": "❌ Exit", "value": {"id": "exit"}})
        
        return inquirer.select(
            message="What would you like to do?",
            choices=choices
        ).execute()
    
    # Handler methods for menu system actions - must accept (ctx, item) and return ExecResult
    
    def handle_explore_mode(self, ctx: dict, item) -> ExecResult:
        """Handle single scenario exploration with all capabilities."""
        self._handle_explore_mode()
        return ExecResult.OK
    
    def handle_analyze_all_mode(self, ctx: dict, item) -> ExecResult:
        """Handle analysis across all blueprints."""
        self._handle_analyze_all_mode()
        return ExecResult.OK
    
    def handle_governance_mode(self, ctx: dict, item) -> ExecResult:
        """Handle governance checking mode."""
        self._handle_governance_mode()
        return ExecResult.OK
    
    def handle_diff_mode(self, ctx: dict, item) -> ExecResult:
        """Handle blueprint comparison mode."""
        self._handle_diff_mode()
        return ExecResult.OK
    
    def launch_scenario_explorer(self, ctx: dict, item) -> ExecResult:
        """Launch explorer for a specific scenario."""
        # This would need scenario selection logic
        scenario_key = self._select_scenario("exploration")
        if scenario_key:
            self._launch_scenario_explorer(scenario_key)
        return ExecResult.OK
    
    def launch_scenario_tracer(self, ctx: dict, item) -> ExecResult:
        """Launch live walkthrough for a specific scenario."""
        scenario_key = self._select_scenario("walkthrough")
        if scenario_key:
            self._launch_scenario_tracer(scenario_key)
        return ExecResult.OK
    
    def describe_business_process(self, ctx: dict, item) -> ExecResult:
        """Describe the business process for the selected scenario using OpenAI."""
        scenario_key = self._select_scenario("business process description")
        if scenario_key:
            self._describe_business_process(scenario_key)
        return ExecResult.OK
    
    def handle_report_mode(self, ctx: dict, item) -> ExecResult:
        """Handle static report generation."""
        self._handle_report_mode()
        return ExecResult.OK
    
    def handle_search_mode(self, ctx: dict, item) -> ExecResult:
        """Handle cross-blueprint search mode."""
        self._handle_search_mode()
        return ExecResult.OK
    
    def run_governance_check(self, ctx: dict, item) -> ExecResult:
        """Run a specific governance check using stored scenario context."""
        check_id = item.metadata.get("check_id")
        check_name = item.metadata.get("check_name")
        
        # Use stored scenario context instead of re-selecting
        scenario_key = getattr(self, '_current_governance_scenario', None)
        if not scenario_key:
            # Fallback to selection if no stored context
            scenario_key = self._select_scenario_for_governance()
            if not scenario_key:
                return ExecResult.NOOP
            
        blueprint = self.blueprints[scenario_key]
        scenario_name = blueprint['scenario_name']
        blueprint_data = blueprint['data']
        
        # Initialize governance checker and run the specific check
        governance_checker = GovernanceChecker()
        try:
            violations = governance_checker.run_check(check_id, blueprint_data, scenario_name)
            self._display_governance_results(violations)
            
            return ExecResult.OK
                
        except Exception as e:
            self.console.print(f"[red]Error running governance check: {e}[/red]")
            input("\nPress Enter to continue...")
            
        return ExecResult.OK
    
    def _handle_explore_mode(self):
        """Handle single scenario exploration with all capabilities."""
        scenario_key = self._select_scenario("exploration")
        if not scenario_key:
            return
        
        # Present scenario-specific options
        while True:
            try:
                action = self._select_scenario_action(scenario_key)
                if action == "back":
                    break
                
                # Use menu system for centralized enforcement
                if not self._execute_scenario_action(action, scenario_key):
                    continue  # Premium prompt was shown, continue loop
                    
            except KeyboardInterrupt:
                break
    
    def _execute_scenario_action(self, action: str, scenario_key: str) -> bool:
        """Execute scenario action with centralized license enforcement."""
        # Define execution functions
        action_executors = {
            "explore_modules": lambda: self._launch_scenario_explorer(scenario_key),
            "trace_flow": lambda: self._launch_scenario_tracer(scenario_key),
            "describe_process": lambda: self._describe_business_process(scenario_key)
        }
        
        executor = action_executors.get(action)
        if not executor:
            return False
        
        # Use centralized license checking
        return execute_with_license_check(action, self.context, executor, self.console)
    
    def _handle_analyze_all_mode(self):
        """Handle analysis across all blueprints."""
        while True:
            try:
                action = self._select_analysis_action()
                if action == "back":
                    break
                
                # Use menu system for centralized enforcement
                if not self._execute_analysis_action(action):
                    continue  # Premium prompt was shown, continue loop
                    
            except KeyboardInterrupt:
                break
    
    def _execute_analysis_action(self, action: str) -> bool:
        """Execute analysis action with centralized license enforcement."""
        # Define execution functions
        action_executors = {
            "static_report": lambda: self._handle_report_mode(),
            "cross_search": lambda: self._handle_search_mode()
        }
        
        executor = action_executors.get(action)
        if not executor:
            return False
        
        # Use centralized license checking
        return execute_with_license_check(action, self.context, executor, self.console)
    
    def _handle_search_mode(self):
        """Handle cross-blueprint search mode."""
        # Launch search interface which handles all scenarios
        search_interface = SearchInterface()
        search_interface.start(self.directory_path)
    
    def _select_scenario(self, purpose: str = "analysis") -> Optional[str]:
        """Present scenario selection menu with hierarchical folder navigation."""
        if len(self.blueprints) == 1:
            # Only one scenario, auto-select it
            return list(self.blueprints.keys())[0]
        
        return self._navigate_scenario_folders(purpose)
    
    def _navigate_scenario_folders(self, purpose: str, current_path: str = "") -> Optional[str]:
        """Navigate through folder structure to select a scenario."""
        # Build folder structure from blueprints
        folder_structure = self._build_folder_structure()
        
        # Navigate to current path
        current_items = self._get_current_folder_items(folder_structure, current_path)
        
        while True:
            choices = []
            
            # Add parent directory option if not at root
            if current_path:
                choices.append({"name": "📁 .. (parent directory)", "value": "parent"})
                choices.append(Separator())
            
            # Add folders first
            for item_name, item_data in sorted(current_items.items()):
                if item_data.get('type') == 'folder':
                    folder_count = self._count_scenarios_in_folder(item_data)
                    choices.append({
                        "name": f"📁 {item_name}/ ({folder_count} scenarios)",
                        "value": f"folder:{item_name}"
                    })
            
            # Add scenarios
            scenario_items = [(name, data) for name, data in current_items.items() 
                             if data.get('type') == 'scenario']
            
            if scenario_items:
                if any(item_data.get('type') == 'folder' for item_data in current_items.values()):
                    choices.append(Separator())
                
                for item_name, item_data in sorted(scenario_items):
                    blueprint = self.blueprints[item_data['key']]
                    scenario_name = blueprint['scenario_name']
                    module_count = blueprint['module_count']
                    display_name = f"📄 {scenario_name}"
                    if scenario_name != item_name:
                        display_name += f" ({item_name})"
                    display_name += f" - {module_count} modules"
                    
                    choices.append({
                        "name": display_name,
                        "value": item_data['key']
                    })
            
            # Add navigation options
            choices.extend([
                Separator(),
                {"name": "← Back", "value": "back"}
            ])
            
            # Show current path in message
            path_display = f"/{current_path}" if current_path else "/"
            message = f"Select a scenario for {purpose} (current: {path_display}):"
            
            selection = inquirer.select(
                message=message,
                choices=choices
            ).execute()
            
            if selection == "back":
                return None
            elif selection == "parent":
                # Go to parent directory
                if "/" in current_path:
                    current_path = "/".join(current_path.split("/")[:-1])
                else:
                    current_path = ""
                current_items = self._get_current_folder_items(folder_structure, current_path)
            elif selection.startswith("folder:"):
                # Navigate into folder
                folder_name = selection[7:]  # Remove "folder:" prefix
                if current_path:
                    current_path = f"{current_path}/{folder_name}"
                else:
                    current_path = folder_name
                current_items = self._get_current_folder_items(folder_structure, current_path)
            else:
                # Selected a scenario
                return selection
    
    def _build_folder_structure(self) -> dict:
        """Build hierarchical folder structure from blueprint paths."""
        structure = {}
        
        for key, blueprint in self.blueprints.items():
            relative_path = blueprint['relative_path']
            path_parts = relative_path.parts[:-1]  # Exclude filename
            filename = relative_path.stem
            
            # Navigate/create folder structure
            current_level = structure
            for part in path_parts:
                if part not in current_level:
                    current_level[part] = {'type': 'folder', 'children': {}}
                current_level = current_level[part]['children']
            
            # Add the scenario file
            current_level[filename] = {
                'type': 'scenario',
                'key': key
            }
        
        return structure
    
    def _get_current_folder_items(self, structure: dict, path: str) -> dict:
        """Get items in the current folder."""
        if not path:
            return structure
        
        current_level = structure
        for part in path.split("/"):
            if part in current_level and current_level[part].get('type') == 'folder':
                current_level = current_level[part]['children']
            else:
                return {}
        
        return current_level
    
    def _count_scenarios_in_folder(self, folder_data: dict) -> int:
        """Count total scenarios in a folder (including subfolders)."""
        count = 0
        children = folder_data.get('children', {})
        
        for item_data in children.values():
            if item_data.get('type') == 'scenario':
                count += 1
            elif item_data.get('type') == 'folder':
                count += self._count_scenarios_in_folder(item_data)
        
        return count
    
    def _select_scenario_action(self, scenario_key: str) -> str:
        """Present action menu for a selected scenario."""
        blueprint = self.blueprints[scenario_key]
        scenario_name = blueprint['scenario_name']
        module_count = blueprint['module_count']
        
        self.console.print(f"\n🎯 [bold]Selected Scenario:[/bold] {scenario_name} ({module_count} modules)\n")
        
        # Use menu system to get proper Pro labels
        has_premium = license_manager.has_premium()
        explore_children = menu_system.get_children('main.explore')
        
        # Map menu items to action values
        action_map = {
            'explore.modules': 'explore_modules',
            'explore.walkthrough': 'trace_flow',
            'explore.ai_process': 'describe_process'
        }
        
        choices = []
        for item in sorted(explore_children, key=lambda x: x.order):
            if item.id in action_map:
                choices.append({
                    "name": menu_system.label_for(item, has_premium),
                    "value": action_map[item.id],
                    "description": item.description
                })
        
        choices.extend([
            Separator(),
            {
                "name": "← Back",
                "value": "back"
            }
        ])
        
        return inquirer.select(
            message="What would you like to do with this scenario?",
            choices=choices
        ).execute()
    
    def _select_analysis_action(self) -> str:
        """Present analysis options for all blueprints."""
        self.console.print(f"\n📊 [bold]Analyzing All Blueprints:[/bold] {len(self.blueprints)} scenarios loaded\n")
        
        # Use menu system to get proper Pro labels
        has_premium = license_manager.has_premium()
        analyze_children = menu_system.get_children('main.analyze')
        
        # Map menu items to action values
        action_map = {
            'analyze.report': 'static_report',
            'analyze.search': 'cross_search'
        }
        
        choices = []
        for item in sorted(analyze_children, key=lambda x: x.order):
            if item.id in action_map:
                choices.append({
                    "name": menu_system.label_for(item, has_premium),
                    "value": action_map[item.id],
                    "description": item.description
                })
        
        choices.extend([
            Separator(),
            {
                "name": "← Back",
                "value": "back"
            }
        ])
        
        return inquirer.select(
            message="What type of analysis would you like to perform?",
            choices=choices
        ).execute()
    
    def _launch_scenario_explorer(self, scenario_key: str):
        """Launch explorer for a specific scenario."""
        explorer = BlueprintExplorer()
        
        # Temporarily create a directory with just the selected scenario
        import tempfile
        import json
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            blueprint = self.blueprints[scenario_key]
            
            # Write the selected blueprint to temp directory with correct structure
            temp_file = temp_path / f"{blueprint['filename']}.json"
            
            # Normalize the data structure - unwrap blueprint if present
            data_to_write = blueprint['data']
            if 'blueprint' in data_to_write:
                # For diff blueprints, extract the inner blueprint data and add name at root level
                inner_data = data_to_write['blueprint'].copy()
                # Ensure the name is at the root level for consistency
                if 'name' not in inner_data:
                    inner_data['name'] = blueprint['scenario_name']
                data_to_write = inner_data
            
            with open(temp_file, 'w') as f:
                json.dump(data_to_write, f, indent=2)
            
            # Launch explorer
            explorer.start(temp_path)
    
    def _launch_scenario_tracer(self, scenario_key: str):
        """Launch live walkthrough for a specific scenario."""
        trace_interface = TraceInterface()
        
        # Temporarily create a directory with just the selected scenario
        import tempfile
        import json
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            blueprint = self.blueprints[scenario_key] 
            
            # Write the selected blueprint to temp directory with correct structure
            temp_file = temp_path / f"{blueprint['filename']}.json"
            
            # Normalize the data structure - unwrap blueprint if present
            data_to_write = blueprint['data']
            if 'blueprint' in data_to_write:
                # For diff blueprints, extract the inner blueprint data and add name at root level
                inner_data = data_to_write['blueprint'].copy()
                # Ensure the name is at the root level for consistency
                if 'name' not in inner_data:
                    inner_data['name'] = blueprint['scenario_name']
                data_to_write = inner_data
            
            with open(temp_file, 'w') as f:
                json.dump(data_to_write, f, indent=2)
            
            # Launch tracer with specific scenario context - use filename for temp file lookup
            trace_interface.start(temp_path, specific_scenario=blueprint['filename'])
    
    def _describe_business_process(self, scenario_key: str):
        """Describe the business process for the selected scenario using OpenAI."""
        blueprint = self.blueprints[scenario_key]
        scenario_name = blueprint['scenario_name']
        
        self.console.print(f"\n📝 [bold]Business Process Description for:[/bold] {scenario_name}\n")
        
        try:
            # Get OpenAI API key
            import os
            api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                self.console.print("[red]❌ OpenAI API key not found. Please set OPENAI_API_KEY environment variable.[/red]")
                input("\nPress Enter to continue...")
                return
            
            # Import OpenAI client
            try:
                from openai import OpenAI
            except ImportError:
                self.console.print("[red]❌ OpenAI library not installed. Run: pip install openai[/red]")
                input("\nPress Enter to continue...")
                return
            
            # Show loading message
            with self.console.status("[bold green]Analyzing business process with AI..."):
                client = OpenAI(api_key=api_key)
                
                # Prepare the prompt
                system_prompt = """You are a business process analyst.
You receive a JSON blueprint exported from Workfront Fusion or Make.com.
Your task is to interpret the automation as a business process, not a technical flow.

Guidelines:

Ignore IDs, variable names, connection names, module UIDs, and field mappings.

Focus only on what happens in business terms: who or what triggers it, what decisions occur, what data or documents move, and what outcomes are produced.

Use plain business language (no API or platform references).

Abstract automation steps into actions, decisions, and outcomes.

If loops or routers exist, express them as business branching logic ("If an order is pending approval, route to manager").

Present output as a structured narrative or numbered steps describing the process as a human workflow.

Example Output Format:

Business Process Summary:
1. The process starts when a new customer order is received.
2. The system checks whether the order exceeds the customer's credit limit.
3. If it does, an approval request is sent to Finance.
4. Approved orders are confirmed with the customer and passed to fulfillment.
5. Rejected orders are logged and a notification is sent.

Key Business Outcome:
Ensures all customer orders are validated and approved before fulfillment.

Your Output: A concise business-process description for a non-technical business owner."""
                
                # Get the blueprint JSON data
                blueprint_json = blueprint['data']
                
                # Format user prompt
                user_prompt = f"Your Input: {json.dumps(blueprint_json, indent=2)}"
                
                # Call OpenAI API
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=1500,
                    temperature=0.7
                )
                
                # Display the response
                business_description = response.choices[0].message.content
                
                from rich.panel import Panel
                from rich.markdown import Markdown
                
                # Display the business process description
                markdown_content = Markdown(business_description)
                panel = Panel(
                    markdown_content,
                    title=f"🏢 Business Process Analysis: {scenario_name}",
                    expand=False,
                    border_style="green"
                )
                
                self.console.print(panel)
                
        except Exception as e:
            self.console.print(f"[red]❌ Error analyzing business process: {str(e)}[/red]")
        
        input("\nPress Enter to continue...")
    
    def _handle_governance_mode(self):
        """Handle governance checking mode."""
        while True:
            try:
                # Step 1: List all scenarios
                scenario_key = self._select_scenario_for_governance()
                if not scenario_key:
                    break
                
                # Step 2: Run governance checks for selected scenario
                continue_with_scenario = True
                while continue_with_scenario:
                    action = self._run_governance_checks(scenario_key)
                    if action == "different_scenario":
                        continue_with_scenario = False
                    elif action == "main_menu":
                        return
                    # If action == "another_check", continue the loop
                    
            except KeyboardInterrupt:
                break
    
    def _select_scenario_for_governance(self) -> Optional[str]:
        """Select a scenario for governance checking."""
        self.console.print("\n⚖️ [bold blue]Governance Check[/bold blue]")
        self.console.print("Select a scenario to audit for compliance with governance rules.\n")
        
        if len(self.blueprints) == 1:
            # Only one scenario, auto-select it
            return list(self.blueprints.keys())[0]
        
        return self._navigate_scenario_folders("governance checking")
    
    def _run_governance_checks(self, scenario_key: str) -> str:
        """Run governance checks on a scenario using standardized menu system."""
        blueprint = self.blueprints[scenario_key]
        scenario_name = blueprint['scenario_name']
        
        # Store scenario context for the handlers
        self._current_governance_scenario = scenario_key
        
        while True:
            # Step 2: List available governance checks using menu system
            self.console.print(f"\n⚖️ [bold]Governance Checks for: {scenario_name}[/bold]\n")
            
            governance_item = menu_system.get_item("main.governance")
            if not governance_item or not governance_item.children:
                self.console.print("[red]No governance checks available[/red]")
                return "main_menu"
                
            has_premium = license_manager.has_premium()
            governance_children = sorted(governance_item.children, key=lambda x: x.order)
            choices = menu_system.to_inquirer_choices(governance_children, has_premium)
            
            # Add navigation options
            choices.extend([
                Separator(),
                {"name": "← Select different scenario", "value": {"id": "different_scenario"}},
                {"name": "← Return to main menu", "value": {"id": "main_menu"}}
            ])
            
            selection = inquirer.select(
                message="Which check would you like to run?",
                choices=choices
            ).execute()
            
            if selection.get("id") in ["different_scenario", "main_menu"]:
                return selection["id"]
            
            # Use menu system for standardized execution and enforcement
            try:
                result = menu_system.resolve_and_execute(selection, self.context, self)
                if result == ExecResult.PREMIUM_REQUIRED:
                    continue  # Premium prompt shown, go back to selection
                    
                # After running check, ask for next action
                next_action = self._get_governance_next_action()
                if next_action == "another_check":
                    continue
                elif next_action == "different_scenario":
                    return "different_scenario"
                elif next_action == "main_menu":
                    return "main_menu"
                    
            except Exception as e:
                self.console.print(f"[red]Error running governance check: {e}[/red]")
                input("\nPress Enter to continue...")
    
    def _display_governance_results(self, violations: List):
        """Display governance check results."""
        self.console.print()
        
        if not violations:
            self.console.print("✅ [bold green]No results returned![/bold green]")
            self.console.print("[green]This check did not return any results.[/green]")
        else:
            # Separate violations from informational results
            actual_violations = [v for v in violations if getattr(v, 'is_violation', True)]
            informational_results = [v for v in violations if not getattr(v, 'is_violation', True)]
            
            # Display informational results first
            for result in informational_results:
                self.console.print(f"[bold]Rule ID:[/bold] {result.rule_id}")
                self.console.print(f"[bold]Rule Title:[/bold] {result.rule_title}")
                if hasattr(result, 'rule_description') and result.rule_description:
                    self.console.print(f"[bold]How it works:[/bold] {result.rule_description}")
                    self.console.print()  # Add line break
                self.console.print(f"[bold]Result:[/bold] {result.message}")
                self.console.print(f"[bold]Status:[/bold] {result.suggested_fix}")
                if hasattr(result, 'module_id') and result.module_id:
                    self.console.print(f"[dim]Module ID: {result.module_id}[/dim]")
                self.console.print()
            
            # Display violations
            if actual_violations:
                if informational_results:
                    self.console.print(f"❌ [bold red]{len(actual_violations)} violation(s) also found:[/bold red]\n")
                else:
                    self.console.print(f"❌ [bold red]{len(actual_violations)} violation(s) found:[/bold red]\n")
                
                for violation in actual_violations:
                    self.console.print(f"[bold]Rule ID:[/bold] {violation.rule_id}")
                    self.console.print(f"[bold]Rule Title:[/bold] {violation.rule_title}")
                    if hasattr(violation, 'rule_description') and violation.rule_description:
                        self.console.print(f"[bold]How it works:[/bold] {violation.rule_description}")
                        self.console.print()  # Add line break
                    self.console.print(f"[bold]Result:[/bold] {violation.message}")
                    self.console.print(f"[bold]Suggested fix:[/bold] {violation.suggested_fix}")
                    if hasattr(violation, 'module_id') and violation.module_id:
                        self.console.print(f"[dim]Module ID: {violation.module_id}[/dim]")
                    self.console.print()
        
        input("Press Enter to continue...")
    
    def _handle_diff_mode(self):
        """Handle blueprint comparison mode."""
        from ...comparison.diff_engine import FusionDiff
        
        diff_tool = FusionDiff()
        diff_tool.run(self.directory_path)
    
    def _get_governance_next_action(self) -> str:
        """Get next action after showing governance results."""
        choices = [
            {"name": "1. Run another check on this scenario", "value": "another_check"},
            {"name": "2. Select a different scenario", "value": "different_scenario"},
            {"name": "3. Return to the main menu", "value": "main_menu"}
        ]
        
        return inquirer.select(
            message="Would you like to:",
            choices=choices
        ).execute()
    
