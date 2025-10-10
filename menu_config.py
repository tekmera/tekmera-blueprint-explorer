"""
Menu Configuration System for Tekmera Fusion Explorer
Centralized menu definitions with hierarchy, licensing, and paywall integration
"""
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import sys
import logging


logger = logging.getLogger(__name__)


class LicenseType(Enum):
    FREE = "free"
    PREMIUM = "premium"


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
    children: List['MenuItem'] = field(default_factory=list)
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

    def add_child(self, child: 'MenuItem') -> 'MenuItem':
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
            'id': self.id,
            'label': self.label,
            'display_label': self.display_label,
            'description': self.description,
            'action': self.action,
            'parent_id': self.parent_id,
            'children': [child.to_dict() for child in self.children],
            'license_required': self.license_required.value,
            'enabled_if': 'callable' if self.enabled_if else None,
            'visible': self.visible,
            'separator_after': self.separator_after,
            'metadata': self.metadata,
            'telemetry_id': self.telemetry_id,
            'order': self.order
        }


class MenuSystem:
    """Centralized menu configuration and navigation system"""
    
    def __init__(self):
        self.items: Dict[str, MenuItem] = {}
        self.root_items: List[MenuItem] = []
        self._governance_warned = False  # Track if we've warned about inference
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
            order=1
        )
        
        main_analyze = MenuItem(
            id="main.analyze", 
            label="Analyze All Blueprints",
            display_label="📊 Analyze All Blueprints",
            description="Generate reports and search across all scenarios in the directory", 
            action="handle_analyze_all_mode",
            order=2
        )
        
        main_governance = MenuItem(
            id="main.governance",
            label="Governance Audit",
            display_label="⚖️ Governance Audit",
            description="Audit scenarios for compliance with governance rules",
            action="handle_governance_mode",
            order=3
        )
        
        main_diff = MenuItem(
            id="main.diff",
            label="Compare Scenarios",
            display_label="🔄 Compare Scenarios", 
            description="Compare two blueprint scenarios to identify functional differences",
            action="handle_diff_mode",
            order=4,
            separator_after=True
        )
        
        # 1.1 Explore Scenario Submenu
        explore_modules = MenuItem(
            id="explore.modules",
            label="Explore modules & search within scenario",
            display_label="🔍 Explore modules & search within scenario",
            description="Interactive module exploration with built-in search capabilities",
            action="launch_scenario_explorer",
            order=1
        )
        
        explore_walkthrough = MenuItem(
            id="explore.walkthrough", 
            label="Live Scenario Walkthrough",
            display_label="🎥 Live Scenario Walkthrough",
            description="Interactive step-by-step walkthrough of scenario execution",
            action="launch_scenario_tracer",
            license_required=LicenseType.PREMIUM,
            order=2
        )
        
        explore_ai_process = MenuItem(
            id="explore.ai_process",
            label="Describe Business Process",
            display_label="📝 Describe Business Process", 
            description="AI-powered business process description of the scenario",
            action="describe_business_process",
            license_required=LicenseType.PREMIUM,
            enabled_if=openai_api_available,
            order=3,
            separator_after=True
        )
        
        # 1.2 Analyze All Submenu
        analyze_report = MenuItem(
            id="analyze.report",
            label="Generate static analysis report",
            display_label="📋 Generate static analysis report",
            description="Comprehensive summaries, module counts, and field analysis", 
            action="handle_report_mode",
            order=1
        )
        
        analyze_search = MenuItem(
            id="analyze.search",
            label="Search across all blueprints",
            display_label="🔎 Search across all blueprints",
            description="Find patterns, fields, and modules across all scenarios",
            action="handle_search_mode",
            license_required=LicenseType.PREMIUM,
            order=2,
            separator_after=True
        )
        
        # Build hierarchy
        main_explore.add_child(explore_modules)
        main_explore.add_child(explore_walkthrough) 
        main_explore.add_child(explore_ai_process)
        
        main_analyze.add_child(analyze_report)
        main_analyze.add_child(analyze_search)
        
        # Register all items (children are registered recursively)
        self._register_items([
            main_explore, main_analyze, main_governance, main_diff
        ])
        
        # Set root items
        self.root_items = [main_explore, main_analyze, main_governance, main_diff]

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
        # Robust license check - accept both enum and string
        has_pro = ctx.get("license") in {LicenseType.PREMIUM, LicenseType.PREMIUM.value}
        
        # Check premium license requirement
        if item.license_required == LicenseType.PREMIUM and not has_pro:
            return False
            
        # Check conditional enablement
        if item.enabled_if and not item.enabled_if(ctx):
            return False
            
        return True

    def label_for(self, item: MenuItem, has_premium: bool) -> str:
        """Generate display label with Pro marking - public API for testing"""
        # Use display_label for rich rendering, fallback to label
        base_label = item.display_label or item.label
        # Remove existing [Pro] markers first for idempotency
        label = base_label.replace(" [Pro]", "")
        if item.is_premium() and not has_premium:
            label += " [Pro]"
        return label

    def add_governance_checks(self, governance_checker):
        """Dynamically add governance check items"""
        governance_item = self.get_item("main.governance")
        if not governance_item:
            return
            
        available_checks = governance_checker.get_available_checks()
        
        for check_data in available_checks:
            # Prefer explicit boolean from checker, keep fallback with warning
            if len(check_data) == 3:
                check_id, check_name, is_premium = check_data
            else:
                check_id, check_name = check_data
                # Warn once about inference
                if not self._governance_warned:
                    logger.warning("Governance checker doesn't provide premium flags, inferring from check ID")
                    self._governance_warned = True
                # Safe check for premium status - avoid int() conversion
                is_premium = str(check_id) in ['6', '7', '8', '9', '10', '11']
            
            # Safe order calculation
            order = int(check_id) if str(check_id).isdigit() else 999
            
            check_item = MenuItem(
                id=f"governance.check_{check_id}",
                label=f"{check_id}. {check_name}",
                description=check_name,
                action="run_governance_check",
                license_required=LicenseType.PREMIUM if is_premium else LicenseType.FREE,
                metadata={"check_id": check_id, "check_name": check_name},
                order=order
            )
            
            governance_item.add_child(check_item)
            self.items[check_item.id] = check_item

    def to_inquirer_choices(self, items: List[MenuItem], has_premium: bool = False) -> List[Union[Dict[str, Any], object]]:
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
                
            choices.append({
                "name": self.label_for(item, has_premium),
                "value": {"id": item.id, "action": item.action}  # Include action hint
            })
            
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
            prompt_result = self.show_premium_prompt(item, ctx, handler_obj)
            return ExecResult.PREMIUM_REQUIRED if prompt_result else ExecResult.NOOP
            
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

    def show_premium_prompt(self, item: MenuItem, ctx: dict, handler_obj=None) -> bool:
        """Show upgrade prompt for premium features - non-interactive safe"""
        if handler_obj and hasattr(handler_obj, 'console'):
            console = handler_obj.console
            console.print(f"\n[yellow]🔒 Premium Feature Required[/yellow]")
            console.print(f"[bold]{item.label.replace(' [Pro]', '')}[/bold] requires Tekmera Pro.")
            console.print("Upgrade to unlock advanced governance intelligence and AI features.")
            console.print("\n[dim]Press Enter to continue...[/dim]")
            
            # Guard for TTY and handle EOFError gracefully
            if sys.stdin.isatty():
                try:
                    input()
                except EOFError:
                    pass
        return True

    def export_config(self, include_roots: bool = True, include_all: bool = True) -> str:
        """Export menu configuration as JSON with size options"""
        config = {"menu_system": {}}
        
        if include_roots:
            config["menu_system"]["root_items"] = [item.to_dict() for item in self.get_root_items()]
            
        if include_all:
            config["menu_system"]["all_items"] = {item_id: item.to_dict() for item_id, item in self.items.items()}
            
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
                parent_label = (parent.display_label if use_labels else parent.label) or parent.label
                breadcrumb.insert(0, parent_label)
                current = parent
            else:
                break
                
        return breadcrumb


# Global menu system instance
menu_system = MenuSystem()