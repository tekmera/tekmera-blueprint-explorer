"""
Interactive CLI interface for Tekmera Explorer
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from InquirerPy import inquirer
from InquirerPy.separator import Separator
from rich.panel import Panel
from rich.text import Text

from ...config.menu_system import ExecResult, menu_system
from ...infra.license import license_manager
from ...reporting.reporter import Reporter
from ...services.openai_service import get_openai_service
from ...utils.base_cli import InteractiveCLIBase
from .explorer import BlueprintExplorer
from .search import SearchInterface
from .trace import TraceInterface


class InteractiveCLI(InteractiveCLIBase):
    """Main interactive CLI interface for the Blueprint Analyzer."""

    def __init__(self):
        super().__init__(enable_search_display=False)  # Interactive doesn't need search display
        self.directory_path = None

        # License is automatically detected from ~/.tekmera/license.json on startup
        # No manual override needed - users activate licenses with 'tekmera license activate'
        self.context = license_manager.get_context()

    def start(self, directory: Path):
        """Start the interactive CLI session."""
        self.directory_path = directory

        # Display welcome banner
        self._display_welcome()

        # Load blueprints
        self.load_blueprints(directory, include_modules=True)

        if not self.blueprints:
            self.show_error("No valid blueprint files found in the specified directory")
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
                self.handle_keyboard_interrupt()
                break

    def _display_welcome(self):
        """Display welcome banner and directory info."""
        welcome_text = Text()
        welcome_text.append("🔍 ", style="blue")
        welcome_text.append("Tekmera Fusion Explorer", style="bold blue")

        # Get detailed license information
        license_info = license_manager.get_license_info()
        if license_info["status"] == "active":
            if license_info.get("is_evaluation", False):
                license_text = f"Evaluation"
                if license_info.get("days_remaining") is not None:
                    days = license_info["days_remaining"]
                    license_text += f" - {days} day{'s' if days != 1 else ''} remaining"
            else:
                license_text = "Paid"
        elif license_info["status"] == "expired":
            if license_info.get("is_evaluation", False):
                license_text = "Free (evaluation expired)"
            else:
                license_text = "Free (license expired)"
        else:
            license_text = "Free"

        info_text = f"Directory: {self.directory_path}\nLicense: {license_text}"

        panel = Panel(
            f"{welcome_text}\n\n{info_text}", title="Welcome", expand=False, border_style="blue"
        )

        self.console.print("\n")
        self.console.print(panel)
        self.console.print()

    def _select_mode(self) -> Optional[Dict[str, str]]:
        """Present mode selection menu using menu system."""
        has_premium = license_manager.has_premium()
        root_items = menu_system.get_root_items()
        choices = menu_system.to_inquirer_choices(root_items, has_premium)

        # Add exit option
        choices.append({"name": "❌ Exit", "value": {"id": "exit"}})

        return inquirer.select(message="What would you like to do?", choices=choices).execute()

    # Handler methods for menu system actions - must accept (ctx, item) and return ExecResult

    def handle_explore_mode(self, ctx: dict, item) -> ExecResult:
        """Handle single scenario exploration with all capabilities."""
        self._handle_explore_mode()
        return ExecResult.OK

    def handle_analyze_all_mode(self, ctx: dict, item) -> ExecResult:
        """Handle analysis across all blueprints."""
        self._handle_analyze_all_mode()
        return ExecResult.OK

    def handle_diff_mode(self, ctx: dict, item) -> ExecResult:
        """Handle blueprint comparison mode."""
        self._handle_diff_mode()
        return ExecResult.OK

    def launch_scenario_explorer(self, ctx: dict, item) -> ExecResult:
        """Launch explorer for a specific scenario."""
        # Use pre-selected scenario if available, otherwise prompt for selection
        scenario_key = getattr(self, "_selected_scenario_key", None) or self._select_scenario(
            "exploration"
        )
        if scenario_key:
            self._launch_scenario_explorer(scenario_key)
        return ExecResult.OK

    def launch_scenario_tracer(self, ctx: dict, item) -> ExecResult:
        """Launch live walkthrough for a specific scenario."""
        # Use pre-selected scenario if available, otherwise prompt for selection
        scenario_key = getattr(self, "_selected_scenario_key", None) or self._select_scenario(
            "walkthrough"
        )
        if scenario_key:
            self._launch_scenario_tracer(scenario_key)
        return ExecResult.OK

    def describe_business_process(self, ctx: dict, item) -> ExecResult:
        """Describe the business process for the selected scenario using OpenAI."""
        # Use pre-selected scenario if available, otherwise prompt for selection
        scenario_key = getattr(self, "_selected_scenario_key", None) or self._select_scenario(
            "business process description"
        )
        if scenario_key:
            self._describe_business_process(scenario_key)
        return ExecResult.OK

    def ask_scenario_ai_question(self, ctx: dict, item) -> ExecResult:
        """Ask custom AI questions about the selected scenario."""
        # Use pre-selected scenario if available, otherwise prompt for selection
        scenario_key = getattr(self, "_selected_scenario_key", None) or self._select_scenario(
            "AI question"
        )
        if scenario_key:
            self._ask_scenario_ai_question(scenario_key)
        return ExecResult.OK

    def handle_report_mode(self, ctx: dict, item) -> ExecResult:
        """Handle static report generation."""
        self._handle_report_mode()
        return ExecResult.OK

    def handle_search_mode(self, ctx: dict, item) -> ExecResult:
        """Handle cross-blueprint search mode."""
        self._handle_search_mode()
        return ExecResult.OK

    def handle_ai_query_mode(self, ctx: dict, item) -> ExecResult:
        """Handle AI landscape analysis mode."""
        self._handle_ai_query_mode()
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
        # Map actions to menu item IDs
        action_to_menu_id = {
            "explore_modules": "explore.modules",
            "trace_flow": "explore.walkthrough",
            "describe_process": "explore.ai_process",
            "ask_ai_question": "explore.ai_question",
        }

        menu_id = action_to_menu_id.get(action)
        if not menu_id:
            return False

        # Store scenario key for handlers to use
        self._selected_scenario_key = scenario_key

        try:
            # Use menu system for license enforcement and execution
            choice_value = {"id": menu_id}
            result = menu_system.resolve_and_execute(choice_value, self.context, self)
            return result == ExecResult.OK
        finally:
            # Clean up the selected scenario key
            self._selected_scenario_key = None

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
        # Map actions to menu item IDs
        action_to_menu_id = {
            "static_report": "analyze.report",
            "cross_search": "analyze.search",
            "ai_query": "analyze.ai_query",
        }

        menu_id = action_to_menu_id.get(action)
        if not menu_id:
            return False

        # Use menu system for license enforcement and execution
        choice_value = {"id": menu_id}
        result = menu_system.resolve_and_execute(choice_value, self.context, self)

        return result == ExecResult.OK

    def _handle_search_mode(self):
        """Handle cross-blueprint search mode."""
        # Launch search interface which handles all scenarios
        search_interface = SearchInterface()
        search_interface.start(self.directory_path)

    def _handle_report_mode(self):
        """Handle static report generation."""
        # Generate static analysis report using the Reporter and Analyzer
        reporter = Reporter()

        # Analyze each blueprint to get the correct format
        analysis_results = []
        for key, blueprint in self.blueprints.items():
            # Use the analyzer to get proper format with module_count, etc.
            result = self.analyzer.analyze_blueprint(
                blueprint["data"], blueprint.get("filename", key), self.parser
            )
            analysis_results.append(result)

        # Generate and display report (returns None, prints directly)
        reporter.generate_report(analysis_results)

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
                if item_data.get("type") == "folder":
                    folder_count = self._count_scenarios_in_folder(item_data)
                    choices.append(
                        {
                            "name": f"📁 {item_name}/ ({folder_count} scenarios)",
                            "value": f"folder:{item_name}",
                        }
                    )

            # Add scenarios
            scenario_items = [
                (name, data)
                for name, data in current_items.items()
                if data.get("type") == "scenario"
            ]

            if scenario_items:
                if any(item_data.get("type") == "folder" for item_data in current_items.values()):
                    choices.append(Separator())

                for item_name, item_data in sorted(scenario_items):
                    blueprint = self.blueprints[item_data["key"]]
                    scenario_name = blueprint["scenario_name"]
                    module_count = blueprint["module_count"]
                    display_name = f"📄 {scenario_name}"
                    if scenario_name != item_name:
                        display_name += f" ({item_name})"
                    display_name += f" - {module_count} modules"

                    choices.append({"name": display_name, "value": item_data["key"]})

            # Add navigation options
            choices.extend([Separator(), {"name": "← Back", "value": "back"}])

            # Show current path in message
            path_display = f"/{current_path}" if current_path else "/"
            message = f"Select a scenario for {purpose} (current: {path_display}):"

            selection = inquirer.select(message=message, choices=choices).execute()

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
            file_path = blueprint["file_path"]
            relative_path = file_path.relative_to(self.directory_path)
            path_parts = relative_path.parts[:-1]  # Exclude filename
            filename = relative_path.stem

            # Navigate/create folder structure
            current_level = structure
            for part in path_parts:
                if part not in current_level:
                    current_level[part] = {"type": "folder", "children": {}}
                current_level = current_level[part]["children"]

            # Add the scenario file
            current_level[filename] = {"type": "scenario", "key": key}

        return structure

    def _get_current_folder_items(self, structure: dict, path: str) -> dict:
        """Get items in the current folder."""
        if not path:
            return structure

        current_level = structure
        for part in path.split("/"):
            if part in current_level and current_level[part].get("type") == "folder":
                current_level = current_level[part]["children"]
            else:
                return {}

        return current_level

    def _count_scenarios_in_folder(self, folder_data: dict) -> int:
        """Count total scenarios in a folder (including subfolders)."""
        count = 0
        children = folder_data.get("children", {})

        for item_data in children.values():
            if item_data.get("type") == "scenario":
                count += 1
            elif item_data.get("type") == "folder":
                count += self._count_scenarios_in_folder(item_data)

        return count

    def _select_scenario_action(self, scenario_key: str) -> str:
        """Present action menu for a selected scenario."""
        blueprint = self.blueprints[scenario_key]
        scenario_name = blueprint["scenario_name"]
        module_count = blueprint["module_count"]

        self.console.print(
            f"\n🎯 [bold]Selected Scenario:[/bold] {scenario_name} ({module_count} modules)\n"
        )

        # Use menu system to get proper Pro labels
        has_premium = license_manager.has_premium()
        explore_children = menu_system.get_children("main.explore")

        # Map menu items to action values
        action_map = {
            "explore.modules": "explore_modules",
            "explore.walkthrough": "trace_flow",
            "explore.ai_process": "describe_process",
            "explore.ai_question": "ask_ai_question",
        }

        choices = []
        for item in sorted(explore_children, key=lambda x: x.order):
            if item.id in action_map:
                choices.append(
                    {
                        "name": menu_system.label_for(item, has_premium),
                        "value": action_map[item.id],
                        "description": item.description,
                    }
                )

        choices.extend([Separator(), {"name": "← Back", "value": "back"}])

        return inquirer.select(
            message="What would you like to do with this scenario?", choices=choices
        ).execute()

    def _select_analysis_action(self) -> str:
        """Present analysis options for all blueprints."""
        self.console.print(
            f"\n📊 [bold]Analyzing All Blueprints:[/bold] {len(self.blueprints)} scenarios loaded\n"
        )

        # Use menu system to get proper Pro labels
        has_premium = license_manager.has_premium()
        analyze_children = menu_system.get_children("main.analyze")

        # Map menu items to action values
        action_map = {
            "analyze.report": "static_report",
            "analyze.search": "cross_search",
            "analyze.ai_query": "ai_query",
        }

        choices = []
        for item in sorted(analyze_children, key=lambda x: x.order):
            if item.id in action_map:
                choices.append(
                    {
                        "name": menu_system.label_for(item, has_premium),
                        "value": action_map[item.id],
                        "description": item.description,
                    }
                )

        choices.extend([Separator(), {"name": "← Back", "value": "back"}])

        return inquirer.select(
            message="What type of analysis would you like to perform?", choices=choices
        ).execute()

    def _launch_scenario_explorer(self, scenario_key: str):
        """Launch explorer for a specific scenario."""
        explorer = BlueprintExplorer()

        # Temporarily create a directory with just the selected scenario
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            blueprint = self.blueprints[scenario_key]

            # Write the selected blueprint to temp directory with correct structure
            temp_file = temp_path / f"{blueprint['filename']}.json"

            # Normalize the data structure - unwrap blueprint if present
            data_to_write = blueprint["data"]
            if "blueprint" in data_to_write:
                # For diff blueprints, extract the inner blueprint data and add name at root level
                inner_data = data_to_write["blueprint"].copy()
                # Ensure the name is at the root level for consistency
                if "name" not in inner_data:
                    inner_data["name"] = blueprint["scenario_name"]
                data_to_write = inner_data

            with open(temp_file, "w") as f:
                json.dump(data_to_write, f, indent=2)

            # Launch explorer
            explorer.start(temp_path)

    def _launch_scenario_tracer(self, scenario_key: str):
        """Launch live walkthrough for a specific scenario."""
        trace_interface = TraceInterface()

        # Temporarily create a directory with just the selected scenario
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            blueprint = self.blueprints[scenario_key]

            # Write the selected blueprint to temp directory with correct structure
            temp_file = temp_path / f"{blueprint['filename']}.json"

            # Normalize the data structure - unwrap blueprint if present
            data_to_write = blueprint["data"]
            if "blueprint" in data_to_write:
                # For diff blueprints, extract the inner blueprint data and add name at root level
                inner_data = data_to_write["blueprint"].copy()
                # Ensure the name is at the root level for consistency
                if "name" not in inner_data:
                    inner_data["name"] = blueprint["scenario_name"]
                data_to_write = inner_data

            with open(temp_file, "w") as f:
                json.dump(data_to_write, f, indent=2)

            # Launch tracer with specific scenario context - use filename for temp file lookup
            trace_interface.start(temp_path, specific_scenario=blueprint["filename"])

    def _describe_business_process(self, scenario_key: str):
        """Describe the business process for the selected scenario using OpenAI."""
        blueprint = self.blueprints[scenario_key]
        scenario_name = blueprint["scenario_name"]

        self.console.print(f"\n📝 [bold]Business Process Description for:[/bold] {scenario_name}\n")

        try:
            # Get OpenAI service
            openai_service = get_openai_service()

            if not openai_service.is_available():
                self.console.print(
                    "[red]❌ OpenAI API key not found. Please run 'tekmera init' to configure your API key.[/red]"
                )
                input("\nPress Enter to continue...")
                return

            # Show loading message
            with self.console.status("[bold green]Analyzing business process with AI..."):

                # Get the blueprint JSON data and summarize it for AI
                blueprint_json = blueprint["data"]

                # Use existing summarization method to stay under token limits
                self.console.print("🔍 [blue]Summarizing scenario data for AI analysis...[/blue]")
                scenario_summary = self._summarize_scenario_for_ai(blueprint_json, scenario_name)

                # Call OpenAI service for business analysis
                self.console.print("🤖 [blue]Generating business process description...[/blue]")
                business_description = openai_service.create_business_analysis(
                    scenario_summary, scenario_name
                )

                if not business_description:
                    self.console.print(
                        "[red]❌ Failed to generate business description. Please try again.[/red]"
                    )
                    input("\nPress Enter to continue...")
                    return

                from rich.markdown import Markdown
                from rich.panel import Panel

                # Display the business process description
                markdown_content = Markdown(business_description)
                panel = Panel(
                    markdown_content,
                    title=f"🏢 Business Process Analysis: {scenario_name}",
                    expand=False,
                    border_style="green",
                )

                self.console.print(panel)

        except Exception as e:
            error_msg = str(e)
            if "rate_limit_exceeded" in error_msg:
                self.console.print(
                    f"[red]❌ OpenAI rate limit exceeded. Please try again in a few minutes.[/red]"
                )
                if "tokens" in error_msg:
                    self.console.print(
                        f"[yellow]💡 The scenario was summarized to reduce token usage, but may still be large.[/yellow]"
                    )
            else:
                self.console.print(f"[red]❌ Error analyzing business process: {error_msg}[/red]")

        input("\nPress Enter to continue...")

    def _ask_scenario_ai_question(self, scenario_key: str):
        """Chat with AI about the selected scenario with conversation history."""
        blueprint = self.blueprints[scenario_key]
        scenario_name = blueprint["scenario_name"]
        blueprint["filename"]

        self.console.print(f"\n💬 [bold]Chat About Scenario:[/bold] {scenario_name}\n")

        # Check for existing conversations
        existing_conversations = self._get_existing_conversations(scenario_name)

        if existing_conversations:
            conversation_choice = self._show_conversation_menu(existing_conversations)
            if conversation_choice == "exit":
                return
            elif conversation_choice.startswith("continue_"):
                # Load and continue existing conversation
                conv_file = conversation_choice.replace("continue_", "")
                conversation_history = self._load_conversation(scenario_name, conv_file)
                if conversation_history:
                    self.console.print("[dim]Continuing previous conversation...[/dim]\n")
                    self._continue_chat(scenario_key, conversation_history, conv_file)
                    return
            # If "new", fall through to start new conversation

        self.console.print(
            "[dim]Starting new conversation! Ask follow-up questions, dive deeper, explore the scenario.[/dim]"
        )
        self.console.print("[dim]Type 'exit' to end the chat.[/dim]\n")

        self._start_new_chat(scenario_key)

    def _get_existing_conversations(self, scenario_name: str) -> List[Dict]:
        """Get list of existing conversations for this scenario"""

        # Sanitize scenario name for filesystem
        safe_name = "".join(
            c for c in scenario_name if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        safe_name = safe_name.replace(" ", "_")[:100]  # Limit length
        chat_dir = Path.home() / ".tekmera" / "chats" / safe_name
        if not chat_dir.exists():
            return []

        conversations = []
        corrupted_files = []

        for conv_file in chat_dir.glob("conversation_*.json"):
            try:
                with open(conv_file, "r") as f:
                    conv_data = json.load(f)

                # Validate required fields
                if not all(
                    key in conv_data
                    for key in ["scenario_name", "exchange_count", "conversation_history"]
                ):
                    raise ValueError("Missing required conversation data fields")

                # Add file info for reference
                conv_data["filename"] = conv_file.name
                conv_data["file_path"] = conv_file
                conversations.append(conv_data)

            except Exception as e:
                print(f"Warning: Could not load conversation {conv_file}: {e}")
                corrupted_files.append(conv_file)

        # Clean up corrupted files
        for corrupted_file in corrupted_files:
            try:
                # Move to backup location instead of deleting
                backup_dir = chat_dir / "corrupted"
                backup_dir.mkdir(exist_ok=True)
                backup_file = backup_dir / corrupted_file.name
                corrupted_file.rename(backup_file)
                print(f"Moved corrupted conversation to: {backup_file}")
            except Exception:
                # If move fails, just delete it
                try:
                    corrupted_file.unlink()
                    print(f"Deleted corrupted conversation: {corrupted_file}")
                except Exception:
                    pass  # Give up

        # Sort by last_updated, newest first
        conversations.sort(key=lambda x: x.get("last_updated", ""), reverse=True)
        return conversations[:10]  # Keep only last 10

    def _show_conversation_menu(self, conversations: List[Dict]) -> str:
        """Show menu to select conversation action"""
        choices = [{"name": "🆕 Start new conversation", "value": "new"}]

        if conversations:
            choices.append(Separator("Recent conversations:"))

            for conv in conversations:
                # Format timestamp
                try:
                    from datetime import datetime

                    last_updated = datetime.fromisoformat(
                        conv["last_updated"].replace("Z", "+00:00")
                    )
                    if last_updated.date() == datetime.now().date():
                        time_str = f"Today {last_updated.strftime('%I:%M %p')}"
                    elif (datetime.now() - last_updated).days == 1:
                        time_str = f"Yesterday {last_updated.strftime('%I:%M %p')}"
                    else:
                        time_str = last_updated.strftime("%b %d, %I:%M %p")
                except Exception:
                    time_str = "Unknown time"

                # Get scenario name (short version)
                scenario_name = conv.get("scenario_name", "Unknown")
                if len(scenario_name) > 30:
                    # Try to abbreviate intelligently
                    if "|" in scenario_name:
                        # Format like "FUS008 | PROD | Something" -> "FUS008 | Something"
                        parts = [p.strip() for p in scenario_name.split("|")]
                        if len(parts) >= 3:
                            scenario_short = f"{parts[0]} | {parts[-1]}"
                        else:
                            scenario_short = scenario_name
                    else:
                        scenario_short = scenario_name[:27] + "..."
                else:
                    scenario_short = scenario_name

                # Get preview of last question
                last_q = conv.get("last_question", "No question")
                if len(last_q) > 35:  # Shorter to make room for scenario name
                    last_q = last_q[:35] + "..."

                choice_label = (
                    f"🔄 {time_str} - {conv.get('exchange_count', 0)}x - {scenario_short}"
                )
                if last_q != "No question":
                    choice_label += f' - "{last_q}"'

                choices.append({"name": choice_label, "value": f"continue_{conv['filename']}"})

        choices.append(Separator())
        choices.append({"name": "← Back", "value": "exit"})

        return inquirer.select(message="Choose an option:", choices=choices).execute()

    def _load_conversation(self, scenario_name: str, conv_filename: str) -> Optional[List[Dict]]:
        """Load an existing conversation"""
        try:
            # Sanitize scenario name for filesystem
            safe_name = "".join(
                c for c in scenario_name if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            safe_name = safe_name.replace(" ", "_")[:100]  # Limit length
            chat_dir = Path.home() / ".tekmera" / "chats" / safe_name
            conv_file = chat_dir / conv_filename

            with open(conv_file, "r") as f:
                conv_data = json.load(f)

            return conv_data.get("conversation_history", [])
        except Exception as e:
            self.console.print(f"[red]❌ Could not load conversation: {e}[/red]")
            return None

    def _save_conversation(
        self,
        scenario_name: str,
        conversation_history: List[Dict],
        question_count: int,
        existing_conv_file: str = None,
    ):
        """Save conversation to file"""
        try:
            from datetime import datetime

            # Create chat directory with sanitized scenario name
            safe_name = "".join(
                c for c in scenario_name if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            safe_name = safe_name.replace(" ", "_")[:100]  # Limit length
            chat_dir = Path.home() / ".tekmera" / "chats" / safe_name
            chat_dir.mkdir(parents=True, exist_ok=True)

            # Use existing file if provided, otherwise create new one
            if existing_conv_file:
                conv_file = chat_dir / existing_conv_file
            else:
                # Generate filename with timestamp for new conversations
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                conv_file = chat_dir / f"conversation_{timestamp}.json"

            # Extract last question from conversation
            last_question = "No question"
            for msg in reversed(conversation_history):
                if msg["role"] == "user":
                    content = msg["content"]
                    if "User Question: " in content:
                        last_question = content.split("User Question: ")[-1]
                    else:
                        last_question = content
                    break

            # Prepare conversation data
            conv_data = {
                "scenario_name": scenario_name,
                "started_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "exchange_count": question_count,
                "last_question": last_question,
                "conversation_history": conversation_history,
            }

            # Save to temporary file first, then move (atomic operation)
            temp_file = conv_file.with_suffix(".tmp")
            try:
                with open(temp_file, "w") as f:
                    json.dump(conv_data, f, indent=2)

                # Move temp file to final location (atomic on most filesystems)
                temp_file.replace(conv_file)

                # Clean up old conversations (keep only 10)
                self._cleanup_old_conversations(chat_dir)

            except Exception as save_error:
                # Clean up temp file if save failed
                if temp_file.exists():
                    temp_file.unlink()
                raise save_error

        except Exception as e:
            print(f"Warning: Could not save conversation: {e}")

    def _cleanup_old_conversations(self, chat_dir: Path):
        """Remove old conversation files based on count (10) and age (30 days)"""
        try:
            from datetime import datetime, timedelta

            conv_files = list(chat_dir.glob("conversation_*.json"))
            if not conv_files:
                return

            # Remove files older than 30 days
            cutoff_date = datetime.now() - timedelta(days=30)

            for conv_file in conv_files[:]:  # Use slice copy to modify during iteration
                try:
                    file_mtime = datetime.fromtimestamp(conv_file.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        conv_file.unlink()
                        conv_files.remove(conv_file)
                except Exception:
                    continue  # Skip files with issues

            # Keep only the most recent 10 (after age cleanup)
            if len(conv_files) > 10:
                # Sort by modification time, newest first
                conv_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

                # Remove oldest files beyond 10
                for old_file in conv_files[10:]:
                    old_file.unlink()

        except Exception as e:
            print(f"Warning: Could not cleanup old conversations: {e}")

    def _start_new_chat(self, scenario_key: str):
        """Start a new chat conversation"""
        conversation_history = []
        self._run_chat_loop(scenario_key, conversation_history)

    def _continue_chat(self, scenario_key: str, conversation_history: List[Dict], conv_file: str):
        """Continue an existing chat conversation"""
        # Extract question count from history
        question_count = sum(1 for msg in conversation_history if msg["role"] == "user")
        self.console.print(
            f"[dim]Resuming conversation with {question_count} previous exchanges...[/dim]"
        )

        self._run_chat_loop(scenario_key, conversation_history, conv_file)

    def _run_chat_loop(
        self, scenario_key: str, conversation_history: List[Dict], existing_conv_file: str = None
    ):
        """Main chat loop logic"""
        blueprint = self.blueprints[scenario_key]
        scenario_name = blueprint["scenario_name"]
        blueprint["filename"]

        # Track the conversation file for this session
        current_conv_file = existing_conv_file

        # Prepare scenario data once - will be included in every message
        blueprint_json = blueprint["data"]
        summarized_data = self._summarize_scenario_for_ai(blueprint_json, scenario_name)

        # Add system prompt if this is a new conversation
        if not conversation_history:
            system_prompt = f"""You are a Workfront Fusion expert. You MUST use search tools to find detailed information.

MANDATORY SEARCH USAGE:
When users ask about ANY specific topic, you MUST search for it first. Do NOT give vague answers.

SEARCH TOOLS (USE THESE ACTIVELY):
- search_text: Find specific text/strings in the scenario
- search_module_types: Find specific types of modules
- search_workfront_fields: Find Workfront DE fields and custom fields

EXAMPLES OF REQUIRED SEARCHES:
- "Does this use proofing?" → MUST run search_text("proof") AND search_module_types("proof")
- "How does it use X?" → MUST run search_text("X") to find specifics
- "Any filters/conditions?" → MUST run search_text("filter") AND search_text("condition")
- "What modules do Y?" → MUST run search_module_types("Y")

RESPONSE RULES:
- ALWAYS search first, then answer based on search results
- Include specific details from search results (module IDs, parameter values, etc.)
- If search finds nothing, say "Search found no matches for [term]"
- Never say "details not provided" - search for them!
- Keep responses under 300 words but be specific

You must be an active investigator, not a passive summarizer."""

            conversation_history.append({"role": "system", "content": system_prompt})

        # Calculate starting question count
        question_count = sum(1 for msg in conversation_history if msg["role"] == "user")

        while True:
            # Get user message first, then increment count only if valid
            temp_count = question_count + 1
            prompt_prefix = f"[{temp_count}] " if temp_count > 1 else ""

            question = inquirer.text(
                message=f"{prompt_prefix}You:",
                instruction="(or 'exit' to end chat)",
            ).execute()

            if not question or question.lower().strip() in ["exit", "quit", "back"]:
                break

            # Only increment if we have a real question
            question_count += 1

            # Add user message to conversation WITH scenario context
            user_message_with_context = f"""Scenario: {scenario_name}

Scenario Data:
{summarized_data}

User Question: {question}"""

            conversation_history.append({"role": "user", "content": user_message_with_context})

            try:
                ai_response = self._get_ai_response(conversation_history, scenario_key)

                # Display the response with chat formatting
                self.console.print(f"[{question_count}] [bold blue]AI:[/bold blue] {ai_response}")

                # Save conversation after each exchange
                self._save_conversation(
                    scenario_name, conversation_history, question_count, current_conv_file
                )

                # If this was a new conversation, get the filename for future saves
                if current_conv_file is None:
                    # Find the most recent conversation file to continue using it
                    safe_name = "".join(
                        c for c in scenario_name if c.isalnum() or c in (" ", "-", "_")
                    ).rstrip()
                    safe_name = safe_name.replace(" ", "_")[:100]
                    chat_dir = Path.home() / ".tekmera" / "chats" / safe_name
                    conv_files = list(chat_dir.glob("conversation_*.json"))
                    if conv_files:
                        # Get the most recent file
                        latest_file = max(conv_files, key=lambda x: x.stat().st_mtime)
                        current_conv_file = latest_file.name

            except Exception as e:
                self.console.print(f"[red]❌ Error during AI chat: {str(e)}[/red]")
                # Don't add failed message to history
                conversation_history.pop()  # Remove the user message we just added

        self.console.print(
            f"\n[dim]Chat ended. Had {question_count} exchanges about {scenario_name}[/dim]"
        )

    def _get_ai_response(self, conversation_history: List[Dict], scenario_key: str) -> str:
        """Get AI response with tool support"""
        # Get OpenAI service
        openai_service = get_openai_service()

        if not openai_service.is_available():
            raise ValueError(
                "OpenAI API key not found. Please run 'tekmera init' to configure your API key."
            )

        # Show loading message
        with self.console.status("[bold green]AI thinking..."):

            # Define search tools for AI to use
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "search_text",
                        "description": "Search for specific text strings across the scenario (case-insensitive by default)",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "search_text": {
                                    "type": "string",
                                    "description": "Text to search for (e.g., 'approved', 'rejected', 'status')",
                                },
                                "case_sensitive": {
                                    "type": "boolean",
                                    "description": "Whether to use case-sensitive search",
                                    "default": False,
                                },
                            },
                            "required": ["search_text"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "search_module_types",
                        "description": "Search for specific module types in the scenario",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "type_pattern": {
                                    "type": "string",
                                    "description": "Module type to search for (e.g., 'workfront-proof', 'router')",
                                },
                                "exact_match": {
                                    "type": "boolean",
                                    "description": "Whether to require exact match",
                                    "default": False,
                                },
                            },
                            "required": ["type_pattern"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "search_workfront_fields",
                        "description": "Search for Workfront DE fields in the scenario",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "field_pattern": {
                                    "type": "string",
                                    "description": "Field pattern to search for (e.g., 'DE:status', 'proof')",
                                },
                                "exact_match": {
                                    "type": "boolean",
                                    "description": "Whether to require exact match",
                                    "default": False,
                                },
                            },
                            "required": ["field_pattern"],
                        },
                    },
                },
            ]

            # Force the AI to use tools for any question about specifics
            user_question = conversation_history[-1]["content"]
            question_lower = user_question.lower()

            # Detect if question needs search tools
            search_triggers = [
                "proof",
                "does this",
                "how does",
                "what",
                "any",
                "which",
                "find",
                "look",
                "search",
                "detail",
                "specific",
            ]
            needs_search = any(trigger in question_lower for trigger in search_triggers)

            # Call OpenAI API with tool support - FORCE tool use if needed
            response = openai_service.create_completion(
                messages=conversation_history,
                task_type="analysis",
                tools=tools,
                tool_choice="required" if needs_search else "auto",  # Force tool use
                max_tokens=400,
                temperature=0.2,
            )

            # Handle tool calls and AI response
            message = response.choices[0].message

            if message.tool_calls:
                # AI wants to use search tools
                tool_responses = []

                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Execute the search function
                    tool_result = self._execute_search_tool(
                        function_name, function_args, scenario_key
                    )
                    tool_responses.append(f"Search '{function_name}': {tool_result}")

                # Add tool results to conversation (convert tool_calls to serializable format)
                serializable_tool_calls = []
                for tool_call in message.tool_calls:
                    serializable_tool_calls.append(
                        {
                            "id": tool_call.id,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            },
                            "type": tool_call.type,
                        }
                    )

                conversation_history.append(
                    {
                        "role": "assistant",
                        "content": f"I'll search for that information.",
                        "tool_calls": serializable_tool_calls,
                    }
                )

                for i, tool_call in enumerate(message.tool_calls):
                    conversation_history.append(
                        {"role": "tool", "tool_call_id": tool_call.id, "content": tool_responses[i]}
                    )

                # Get AI's final response using search results
                final_response = openai_service.create_completion(
                    messages=conversation_history,
                    task_type="analysis",
                    max_tokens=400,
                    temperature=0.2,
                )

                ai_response = final_response.choices[0].message.content
            else:
                # Regular response without tools
                ai_response = message.content or "No response generated."

            # Add AI response to conversation history
            conversation_history.append({"role": "assistant", "content": ai_response})
            return ai_response

    def _execute_search_tool(
        self, function_name: str, function_args: dict, scenario_key: str
    ) -> str:
        """Execute search tool functions and return formatted results"""
        try:
            # Create a single-scenario corpus analyzer
            import tempfile
            from pathlib import Path

            from ...analysis.corpus_analyzer import CorpusAnalyzer

            # Create temporary directory with just this scenario
            blueprint = self.blueprints[scenario_key]

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Write the scenario to temp file
                temp_file = temp_path / f"{blueprint['filename']}.json"
                data_to_write = blueprint["data"]

                # Normalize data structure
                if "blueprint" in data_to_write:
                    inner_data = data_to_write["blueprint"].copy()
                    if "name" not in inner_data:
                        inner_data["name"] = blueprint["scenario_name"]
                    data_to_write = inner_data

                with open(temp_file, "w") as f:
                    json.dump(data_to_write, f, indent=2)

                # Initialize analyzer and load just this scenario
                analyzer = CorpusAnalyzer()
                analyzer.load_corpus(temp_path)

                # Execute the requested search function
                if function_name == "search_text":
                    results = analyzer.search_text(
                        function_args["search_text"], function_args.get("case_sensitive", False)
                    )
                elif function_name == "search_module_types":
                    results = analyzer.search_module_types(
                        function_args["type_pattern"], function_args.get("exact_match", False)
                    )
                elif function_name == "search_workfront_fields":
                    results = analyzer.search_de_fields(
                        function_args["field_pattern"], function_args.get("exact_match", False)
                    )
                else:
                    return f"Unknown search function: {function_name}"

                # Format results for AI
                if not results:
                    return f"No results found for {function_args}"

                formatted_results = []
                for result in results[:10]:  # Limit to 10 results
                    module_info = {
                        "module_id": result.get("module_id", "unknown"),
                        "module_type": result.get("module_type", "unknown"),
                        "context": result.get("context", ""),
                        "match_type": result.get("match_type", ""),
                    }

                    if "match_details" in result:
                        module_info["match_details"] = result["match_details"]

                    formatted_results.append(module_info)

                return json.dumps(formatted_results, indent=2)

        except Exception as e:
            return f"Search error: {str(e)}"

    def _summarize_scenario_for_ai(self, blueprint_data: dict, scenario_name: str) -> str:
        """Summarize scenario data for AI analysis while staying under token limits"""
        try:
            # Extract key information using existing parser
            from ...core.parser import BlueprintParser

            parser = BlueprintParser()

            # Get all modules
            modules = parser.get_modules(blueprint_data, include_orphans=True)

            summary = {"scenario_name": scenario_name, "total_modules": len(modules), "modules": []}

            # Adaptive module limit based on scenario size to manage token usage
            total_modules = len(modules)
            if total_modules > 100:
                module_limit = 20  # Very large scenarios: show fewer modules
            elif total_modules > 50:
                module_limit = 30  # Large scenarios: moderate detail
            else:
                module_limit = 50  # Normal scenarios: full detail

            # Process each module with appropriate detail level
            for i, module in enumerate(modules[:module_limit]):
                module_summary = {
                    "id": module.get("id", "unknown"),
                    "type": module.get("module", "unknown"),
                    "label": (module.get("metadata", {}).get("label", "") or "")[:100],
                }

                # Add ALL parameters with smart truncation - don't filter out important stuff
                params = module.get("parameters", {})
                if isinstance(params, dict):
                    truncated_params = {}
                    for key, value in params.items():
                        # Include all parameters but truncate smartly
                        if isinstance(value, dict):
                            # For nested objects, include more detail for filters/conditions
                            if any(
                                filter_key in str(key).lower()
                                for filter_key in ["filter", "condition", "where", "criteria"]
                            ):
                                truncated_params[key] = value  # Keep full filter details
                            else:
                                keys_preview = list(value.keys())[:5]
                                ellipsis = "..." if len(value.keys()) > 5 else ""
                                truncated_params[key] = (
                                    f"nested object with keys: {keys_preview}{ellipsis}"
                                )
                        elif isinstance(value, list):
                            # For arrays, show count and first few items
                            if len(value) > 3:
                                truncated_params[key] = f"[{len(value)} items: {value[:3]}...]"
                            else:
                                truncated_params[key] = value
                        elif isinstance(value, str):
                            # Keep filter-related strings longer, truncate others
                            if any(
                                filter_word in value.lower()
                                for filter_word in [
                                    "approved",
                                    "rejected",
                                    "decision",
                                    "status",
                                    "filter",
                                ]
                            ):
                                truncated_params[key] = value[:200] + (
                                    "..." if len(value) > 200 else ""
                                )
                            elif len(value) > 100:
                                truncated_params[key] = value[:100] + "..."
                            else:
                                truncated_params[key] = value
                        else:
                            truncated_params[key] = value

                    if truncated_params:
                        module_summary["parameters"] = truncated_params

                # IMPORTANT: Add detailed route and filter information
                routes = module.get("routes", [])
                if routes:
                    route_details = []
                    for j, route in enumerate(routes[:3]):  # Show first 3 routes
                        route_info = {"route_index": j}

                        # Capture route filters - this is where approved/rejected filters often live
                        if route.get("filter"):
                            route_info["filter"] = route["filter"]

                        # Capture route flow module count
                        route_flow = route.get("flow", [])
                        if route_flow:
                            route_info["modules_in_route"] = len(route_flow)

                        route_details.append(route_info)

                    module_summary["routes"] = route_details
                    if len(routes) > 3:
                        module_summary["additional_routes"] = len(routes) - 3

                # Add error handler details too
                onerror = module.get("onerror", [])
                if onerror:
                    module_summary["error_handlers"] = len(onerror)

                # Add connection info
                connection = module.get("connection")
                if connection:
                    module_summary["connection"] = str(connection)[:30]

                summary["modules"].append(module_summary)

            # Add scenario-level metadata
            if "metadata" in blueprint_data:
                metadata = blueprint_data["metadata"]
                if "designer" in metadata and "orphans" in metadata["designer"]:
                    orphan_count = len(metadata["designer"]["orphans"])
                    if orphan_count > 0:
                        summary["orphaned_modules"] = orphan_count

            # Add truncation notice for large scenarios
            if total_modules > module_limit:
                summary["note"] = (
                    f"Showing first {module_limit} of {total_modules} modules for token efficiency"
                )

            return json.dumps(summary, indent=2)

        except Exception as e:
            # Fallback to basic info
            return f"""{{
    "scenario_name": "{scenario_name}",
    "error": "Could not parse scenario details: {str(e)[:100]}",
    "raw_data_available": true
}}"""

    def _handle_diff_mode(self):
        """Handle blueprint comparison mode."""
        from ...comparison.diff_engine import BlueprintDiff

        diff_tool = BlueprintDiff()
        diff_tool.run(self.directory_path)

    def _handle_ai_query_mode(self):
        """Handle AI landscape analysis for cross-blueprint business queries."""
        self.console.print("\n🤖 [bold blue]Cross-Blueprint AI Analysis[/bold blue]")
        self.console.print(
            "Ask AI about patterns, usage, and business impact across all scenarios in this folder."
        )
        self.console.print(
            "[dim]The AI will actively search across all scenarios to provide detailed, specific answers.[/dim]\n"
        )

        # Show some example questions
        self.console.print("[dim]Example questions:[/dim]")
        self.console.print(
            "[dim]• Which scenarios use Workfront Proof and how do they use it?[/dim]"
        )
        self.console.print(
            "[dim]• What would be the impact of changing the 'status' field name?[/dim]"
        )
        self.console.print("[dim]• Which integrations connect Salesforce to other systems?[/dim]")
        self.console.print(
            "[dim]• How many scenarios would be affected by disabling Slack notifications?[/dim]"
        )

        while True:
            self.console.print()

            # Get user question
            question = inquirer.text(
                message="Enter your question about this blueprint collection:",
                instruction="(or 'exit' to return to main menu)",
            ).execute()

            if not question or question.lower().strip() in ["exit", "quit", "back"]:
                break

            try:
                # Ask user for detail level to ensure completeness
                detail_choice = inquirer.select(
                    message="How much detail should I include in the analysis?",
                    choices=[
                        {
                            "name": "🔍 Detailed - Maximum context (slower, more thorough)",
                            "value": "detailed",
                        },
                        {
                            "name": "⚖️ Balanced - Good detail/speed balance (recommended)",
                            "value": "balanced",
                        },
                        {
                            "name": "⚡ Minimal - Fast analysis for large datasets",
                            "value": "minimal",
                        },
                    ],
                    default="balanced",
                ).execute()

                # Ask for AI model preference
                model_choice = inquirer.select(
                    message="Which AI reasoning approach should I use?",
                    choices=[
                        {
                            "name": "🤖 Auto-Select - Let me choose the best model (recommended)",
                            "value": "auto",
                        },
                        {
                            "name": "🚀 Fast - Quick responses for simple questions (GPT-4o-mini)",
                            "value": "fast",
                        },
                        {"name": "⚖️ Standard - Balanced reasoning (GPT-4o)", "value": "standard"},
                        {
                            "name": "🧠 Deep Thinking - Complex multi-step analysis (GPT-4)",
                            "value": "thinking",
                        },
                    ],
                    default="auto",
                ).execute()

                # Import and use the landscape analyzer with chosen settings
                from ...analysis.ai_landscape import AILandscapeAnalyzer

                analyzer = AILandscapeAnalyzer(
                    self.blueprints, detail_level=detail_choice, model_type=model_choice
                )
                response = analyzer.analyze_with_ai(question, self.console)

                # Display the response in a nice panel
                from rich.markdown import Markdown
                from rich.panel import Panel

                markdown_content = Markdown(response)
                panel = Panel(
                    markdown_content,
                    title=f"🤖 AI Analysis Results",
                    subtitle=f"Question: {question[:60]}{'...' if len(question) > 60 else ''}",
                    expand=False,
                    border_style="blue",
                )

                self.console.print(panel)

            except ValueError as ve:
                self.console.print(f"[red]❌ {str(ve)}[/red]")
            except Exception as e:
                self.console.print(f"[red]❌ Error during AI analysis: {str(e)}[/red]")

            # Ask if they want to ask another question
            self.console.print()
            continue_choice = inquirer.confirm(
                message="Ask another question?", default=True
            ).execute()

            if not continue_choice:
                break
