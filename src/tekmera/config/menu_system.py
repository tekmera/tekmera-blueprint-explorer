"""
Menu Configuration System for Tekmera Fusion Explorer
Centralized menu definitions with hierarchy and paywall integration
"""

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from ..infra.license import LicenseType, license_manager

logger = logging.getLogger(__name__)


class ExecResult(Enum):
    OK = "ok"
    PREMIUM_REQUIRED = "premium_required"
    NOOP = "noop"


@dataclass
class MenuItem:
    """Single menu item with hierarchy and licensing metadata"""

    id: str
    label: str  # ASCII-only for logs
    display_label: Optional[str] = None  # Rich display with emojis
    description: str = ""
    action: Optional[str] = None  # Method name to call - handlers accept (ctx, item) -> ExecResult
    parent_id: Optional[str] = None
    children: List["MenuItem"] = field(default_factory=list)
    license_required: LicenseType = LicenseType.FREE
    enabled_if: Optional[Callable[[dict], bool]] = None  # Callable predicate for enabling
    visible: bool = True
    separator_after: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    telemetry_id: Optional[str] = None  # Stable analytics ID
    order: int = 0  # Sort order

    def __post_init__(self):
        """Set display_label default to label if not provided"""
        if self.display_label is None:
            self.display_label = self.label

    def add_child(self, child: "MenuItem") -> "MenuItem":
        """Add a child menu item"""
        child.parent_id = self.id
        self.children.append(child)
        return child

    def is_premium(self) -> bool:
        """Check if item requires premium license"""
        return self.license_required == LicenseType.PREMIUM

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "label": self.label,
            "display_label": self.display_label,
            "description": self.description,
            "action": self.action,
            "parent_id": self.parent_id,
            "children": [child.to_dict() for child in self.children],
            "license_required": self.license_required.value,
            "enabled_if": "callable" if self.enabled_if else None,
            "visible": self.visible,
            "separator_after": self.separator_after,
            "metadata": self.metadata,
            "telemetry_id": self.telemetry_id,
            "order": self.order,
        }


class MenuSystem:
    """Centralized menu configuration and navigation system"""

    def __init__(self):
        self.items: Dict[str, MenuItem] = {}
        self.root_items: List[MenuItem] = []
        self._build_menu_structure()

    def _build_menu_structure(self):
        """Build the complete menu hierarchy"""

        # Predicate functions for enabling conditions using ctx
        def openai_api_available(ctx: dict) -> bool:
            return bool(ctx.get("openai_api_available"))

        # 1. Main Menu - ASCII labels with rich display_labels
        main_explore = MenuItem(
            id="main.explore",
            label="Explore Scenario",
            display_label="🔍 Explore Scenario",
            description="Interactive exploration, search, and trace execution flow for a single scenario",
            action="handle_explore_mode",
            order=1,
        )

        main_analyze = MenuItem(
            id="main.analyze",
            label="Analyze All Blueprints",
            display_label="📊 Analyze All Blueprints",
            description="Generate reports and search across all scenarios in the directory",
            action="handle_analyze_all_mode",
            order=2,
        )

        main_diff = MenuItem(
            id="main.diff",
            label="Compare Scenarios",
            display_label="🔄 Compare Scenarios",
            description="Compare two blueprint scenarios to identify functional differences",
            action="handle_diff_mode",
            order=3,
            separator_after=True,
        )

        # 1.1 Explore Scenario Submenu
        explore_modules = MenuItem(
            id="explore.modules",
            label="Explore modules & search within scenario",
            display_label="🔍 Explore modules & search within scenario",
            description="Interactive module exploration with built-in search capabilities",
            action="launch_scenario_explorer",
            order=1,
        )

        explore_walkthrough = MenuItem(
            id="explore.walkthrough",
            label="Live Scenario Walkthrough",
            display_label="🎥 Live Scenario Walkthrough",
            description="Interactive step-by-step walkthrough of scenario execution",
            action="launch_scenario_tracer",
            license_required=LicenseType.PREMIUM,
            order=2,
        )

        explore_ai_process = MenuItem(
            id="explore.ai_process",
            label="Describe Business Process",
            display_label="🤖 Describe Business Process",
            description="AI-powered business process description of the scenario",
            action="describe_business_process",
            license_required=LicenseType.PREMIUM,
            enabled_if=openai_api_available,
            order=3,
        )

        explore_ai_question = MenuItem(
            id="explore.ai_question",
            label="Ask AI Question",
            display_label="🤖 Ask AI Question",
            description="Ask custom questions about this specific scenario",
            action="ask_scenario_ai_question",
            license_required=LicenseType.PREMIUM,
            enabled_if=openai_api_available,
            order=4,
            separator_after=True,
        )

        # 1.2 Analyze All Submenu
        analyze_report = MenuItem(
            id="analyze.report",
            label="Generate static analysis report",
            display_label="📋 Generate static analysis report",
            description="Comprehensive summaries, module counts, and field analysis",
            action="handle_report_mode",
            order=1,
        )

        analyze_search = MenuItem(
            id="analyze.search",
            label="Search across all blueprints",
            display_label="🔎 Search across all blueprints",
            description="Find patterns, fields, and modules across all scenarios",
            action="handle_search_mode",
            license_required=LicenseType.PREMIUM,
            order=2,
        )

        analyze_ai_query = MenuItem(
            id="analyze.ai_query",
            label="Cross-Blueprint AI Query",
            display_label="🤖 Cross-Blueprint AI Query",
            description="Ask AI questions about patterns across all blueprints in this folder",
            action="handle_ai_query_mode",
            license_required=LicenseType.PREMIUM,
            enabled_if=openai_api_available,
            order=3,
            separator_after=True,
        )

        # Build hierarchy
        main_explore.add_child(explore_modules)
        main_explore.add_child(explore_walkthrough)
        main_explore.add_child(explore_ai_process)
        main_explore.add_child(explore_ai_question)

        main_analyze.add_child(analyze_report)
        main_analyze.add_child(analyze_search)
        main_analyze.add_child(analyze_ai_query)

        # Register all items (children are registered recursively)
        self._register_items([main_explore, main_analyze, main_diff])

        # Set root items
        self.root_items = [main_explore, main_analyze, main_diff]

    def _register_items(self, items: List[MenuItem]):
        """Register items in the lookup dictionary with duplicate protection"""
        for item in items:
            # Guard against duplicate IDs
            if item.id in self.items:
                raise ValueError(f"Duplicate menu item ID: {item.id}")

            # Default telemetry_id to id if not set
            if not item.telemetry_id:
                item.telemetry_id = item.id

            self.items[item.id] = item
            for child in item.children:
                self._register_items([child])

    def get_item(self, item_id: str) -> Optional[MenuItem]:
        """Get menu item by ID"""
        return self.items.get(item_id)

    def get_children(self, item_id: str) -> List[MenuItem]:
        """Get child items for a menu item"""
        item = self.get_item(item_id)
        return sorted(item.children, key=lambda x: x.order) if item else []

    def get_root_items(self) -> List[MenuItem]:
        """Get top-level menu items"""
        return sorted(self.root_items, key=lambda x: x.order)

    def can_execute(self, item: MenuItem, ctx: dict) -> bool:
        """Centralized gating logic for menu item execution - public API for testing"""
        # Use license manager for robust license checking
        has_pro = ctx.get("license") in {LicenseType.PREMIUM, LicenseType.PREMIUM.value}

        # Check premium license requirement
        if item.license_required == LicenseType.PREMIUM and not has_pro:
            return False

        # Check conditional enablement
        if item.enabled_if and not item.enabled_if(ctx):
            return False

        return True

    def label_for(self, item: MenuItem, has_premium: bool) -> str:
        """Generate display label with Pro status indicators - public API for testing"""
        # Use display_label for rich rendering, fallback to label
        base_label = item.display_label or item.label

        # Remove existing Pro markers first for idempotency
        label = (
            base_label.replace(" [Pro]", "")
            .replace(" [Pro ✓]", "")
            .replace(" [Pro ❌]", "")
            .replace(" [Pro 🔒]", "")
            .replace(" [dim][Pro][/dim]", "")
            .replace(" \033[90m[Pro]\033[0m", "")
        )

        # Add appropriate Pro indicator based on license status
        if item.is_premium():
            if has_premium:
                label += " [Pro ✓]"  # Unlocked/active premium license
            else:
                label += " [Pro 🔒]"  # Locked/no premium license

        return label

    def to_inquirer_choices(
        self, items: List[MenuItem], has_premium: bool = False
    ) -> List[Union[Dict[str, Any], object]]:
        """Convert menu items to InquirerPy choice format with proper value objects"""
        try:
            from InquirerPy.separator import Separator
        except ImportError:
            # Create a mock separator class for testing
            class Separator:
                def __init__(self):
                    self.type = "separator"

        choices = []
        sorted_items = sorted(items, key=lambda x: x.order)

        for i, item in enumerate(sorted_items):
            if not item.visible:
                continue

            choices.append(
                {
                    "name": self.label_for(item, has_premium),
                    "value": {"id": item.id, "action": item.action},  # Include action hint
                }
            )

            # Deterministic separators - avoid trailing separator
            if item.separator_after and i < len([x for x in sorted_items if x.visible]) - 1:
                choices.append(Separator())

        return choices

    def resolve_and_execute(self, choice_value: dict, ctx: dict, handler_obj=None) -> ExecResult:
        """Execute menu action with centralized gating"""
        item = self.get_item(choice_value["id"])
        if not item:
            raise KeyError(f"Menu item '{choice_value['id']}' not found")

        # Centralized gating - enforce at execution time
        if not self.can_execute(item, ctx):
            # Use license manager for premium prompts
            feature_name = (
                item.label.replace(" [Pro]", "")
                .replace(" [Pro ✓]", "")
                .replace(" [Pro 🔒]", "")
                .replace(" [Pro ❌]", "")
                .replace(" [dim][Pro][/dim]", "")
                .replace(" \033[90m[Pro]\033[0m", "")
            )
            license_manager.show_premium_prompt(feature_name, getattr(handler_obj, "console", None))
            return ExecResult.PREMIUM_REQUIRED

        # Dispatch to handler method with context and item
        if item.action and handler_obj:
            func = getattr(handler_obj, item.action, None)
            if callable(func):
                # Enforce action signature contract
                res = func(ctx=ctx, item=item)
                return res if isinstance(res, ExecResult) else ExecResult.OK
            else:
                raise AttributeError(f"Action '{item.action}' not found on handler")

        return ExecResult.NOOP

    def export_config(self, include_roots: bool = True, include_all: bool = True) -> str:
        """Export menu configuration as JSON with size options"""
        config = {"menu_system": {}}

        if include_roots:
            config["menu_system"]["root_items"] = [item.to_dict() for item in self.get_root_items()]

        if include_all:
            config["menu_system"]["all_items"] = {
                item_id: item.to_dict() for item_id, item in self.items.items()
            }

        return json.dumps(config, indent=2)

    def get_breadcrumb(self, item_id: str, use_labels: bool = True) -> List[str]:
        """Get breadcrumb path for a menu item"""
        item = self.get_item(item_id)
        if not item:
            return []

        # Use ASCII labels for logs, display_labels for UI
        label = (item.display_label if use_labels else item.label) or item.label
        breadcrumb = [label]
        current = item

        while current.parent_id:
            parent = self.get_item(current.parent_id)
            if parent:
                parent_label = (
                    parent.display_label if use_labels else parent.label
                ) or parent.label
                breadcrumb.insert(0, parent_label)
                current = parent
            else:
                break

        return breadcrumb


# Global menu system instance
menu_system = MenuSystem()
