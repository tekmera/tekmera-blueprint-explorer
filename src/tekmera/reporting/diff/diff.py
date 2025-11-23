"""Diff report generation for blueprint comparisons."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from ..common.types import BaseReport, ReportMetadata, ReportType
from tekmera.functions.meta.types import Platform, ProjectionResult, create_result
from tekmera.functions.meta.platform_detection import detect_platform


class ChangeType(Enum):
    """Types of changes that can occur to modules."""
    UNCHANGED = "unchanged"
    CONFIGURATION_CHANGED = "configuration_changed"
    STRUCTURALLY_MOVED = "structurally_moved"
    ADDED = "added"
    REMOVED = "removed"


class ChangeImpact(Enum):
    """Impact classification for configuration changes."""
    COSMETIC = "cosmetic"           # Names, positions, UI metadata
    CONFIGURATION = "configuration" # Parameter changes
    STRUCTURAL = "structural"       # Position/flow changes  
    FUNCTIONAL = "functional"       # Logic/behavior changes
    ARCHITECTURAL = "architectural" # Major restructuring


class ChangeScale(Enum):
    """Overall magnitude scale for blueprint changes."""
    UNCHANGED = "unchanged"                    # 0% - No detectable structural deltas
    MINOR = "minor"                           # 0-5% - Small localized structural differences
    MODERATE = "moderate"                     # 5-10% - Noticeable differences affecting contained portion
    MAJOR = "major"                          # 10-40% - Significant modification across substantial portion
    EXTENSIVE = "extensive"                   # 40-85% - Large-scale structural divergence
    DIFFERENT_SCENARIOS = "different scenarios"  # 85-100% - Minimal structural similarity


@dataclass
class ModuleChange:
    """Details of changes to a specific module."""
    module_id: str
    module_type: str
    module_name: str
    change_type: ChangeType
    
    # Configuration changes (if applicable)
    configuration_changes: List[Dict[str, Any]] = field(default_factory=list)
    change_impact: Optional[ChangeImpact] = None
    
    # Structural changes (if moved)
    old_position: Optional[Dict[str, Any]] = None
    new_position: Optional[Dict[str, Any]] = None
    
    # Impact description
    impact_description: str = ""
    
    # Component metadata (for filters, routers, etc.)
    component_metadata: Optional[Dict[str, Any]] = None
    
    # Raw component data for content extraction
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    # Before state for updated components (for before/after comparison)
    raw_data_before: Optional[Dict[str, Any]] = None


@dataclass
class StructuralChange:
    """Structural changes to the blueprint topology."""
    change_description: str
    affected_modules: List[str]
    change_type: str  # "edge_added", "edge_removed", "path_changed", etc.
    impact_level: ChangeImpact


@dataclass
class DiffSummary:
    """High-level summary of all changes."""
    total_changes: int
    change_counts: Dict[str, int]  # {added: 2, removed: 1, moved: 3, changed: 5}
    structural_change_score: float  # 0.0 = identical, 1.0 = completely different
    change_scale: ChangeScale
    change_magnitude: float  # Percentage of change (0.0-1.0)


class BlueprintDiffReport(BaseReport):
    """Platform-agnostic diff report for two blueprints."""
    
    def __init__(
        self,
        blueprint1_name: str,
        blueprint2_name: str,
        platform: Platform,
        summary: DiffSummary,
        module_changes: List[ModuleChange],
        structural_changes: List[StructuralChange],
        blueprint1_path: Optional[str] = None,
        blueprint2_path: Optional[str] = None,
        generated_at: Optional[datetime] = None,
        topology_analysis: Optional[Dict[str, Any]] = None,
        configuration_analysis: Optional[Dict[str, Any]] = None
    ):
        """Initialize diff report with data."""
        metadata = ReportMetadata(
            report_type=ReportType.DIFF,
            platform=platform,
            generated_at=generated_at or datetime.now()
        )
        super().__init__(metadata)
        
        # Core data
        self.blueprint1_name = blueprint1_name
        self.blueprint2_name = blueprint2_name
        self.blueprint1_path = blueprint1_path
        self.blueprint2_path = blueprint2_path
        self.summary = summary
        self.module_changes = module_changes
        self.structural_changes = structural_changes
        self.topology_analysis = topology_analysis or {}
        self.configuration_analysis = configuration_analysis or {}
    
    def to_text(self) -> str:
        """Generate formatted text diff report."""
        report_lines = [
            "=" * 60,
            "BLUEPRINT DIFF REPORT", 
            "=" * 60,
            "",
            f"Comparing:",
            f"  First: {self.blueprint1_name}",
            f"  Second: {self.blueprint2_name}",
            f"Platform: {self._format_platform()}",
            f"Generated: {self.metadata.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "CHANGE ANALYSIS",
            "=" * 60,
            "",
            f"Change Magnitude: {self.summary.change_magnitude:.1%} ({self._get_change_scale_description()})",
            f"Total Number of Changes: {len([c for c in self.module_changes if c.change_type != ChangeType.UNCHANGED])}",
            "",
            "Types of Components Changed:",
        ]
        
        # Get unique component types that changed
        changed_components = [c for c in self.module_changes if c.change_type != ChangeType.UNCHANGED]
        component_types = set()
        for change in changed_components:
            component_type = self._get_component_type(change)
            component_types.add(component_type)
        
        # Add component types as a list
        for comp_type in sorted(component_types):
            report_lines.append(f"- {comp_type}")
        
        report_lines.append("")
        
        # Add subsections for each component type
        for comp_type in sorted(component_types):
            # Get components of this type, ordered by module ID
            type_components = []
            for change in changed_components:
                if self._get_component_type(change) == comp_type:
                    type_components.append(change)
            
            # Sort by module ID (convert to int if possible, otherwise string sort)
            def sort_key(change):
                try:
                    return (0, int(change.module_id))  # (type, value) tuple for consistent sorting
                except ValueError:
                    return (1, change.module_id)  # Strings come after integers
            
            type_components.sort(key=sort_key)
            
            if type_components:
                report_lines.extend([
                    f"{comp_type.upper()}",
                    "-" * len(comp_type.upper()),
                    ""
                ])
                
                # Group by change type
                change_groups = {
                    "Added": [],
                    "Updated": [],
                    "Removed": []
                }
                
                for change in type_components:
                    if change.change_type == ChangeType.ADDED:
                        change_groups["Added"].append(change)
                    elif change.change_type == ChangeType.REMOVED:
                        change_groups["Removed"].append(change)
                    else:  # CONFIGURATION_CHANGED, STRUCTURALLY_MOVED, etc.
                        change_groups["Updated"].append(change)
                
                # Add sub-sections for each change type that has items
                for change_type_name, changes in change_groups.items():
                    if changes:
                        report_lines.extend([
                            change_type_name,
                            ""
                        ])
                        
                        for change in changes:
                            # Get basic info
                            basic_info = f"- Module {change.module_id}: {change.module_name}"
                            
                            # Add component-specific details
                            if comp_type == "Filters":
                                # Get filter relationship information
                                filter_relationship = self._get_filter_relationship(change, changed_components)
                                report_lines.append(f"{basic_info} {filter_relationship}")
                                
                                # Show filter text content
                                filter_content = self._get_filter_text_content(change)
                                if filter_content:
                                    report_lines.extend(filter_content)
                            
                            elif comp_type == "Routers":
                                # Get router route count and type
                                router_info = self._get_router_info(change)
                                report_lines.append(f"{basic_info} ({router_info})")
                            
                            elif comp_type == "Modules":
                                # Get service type and operation
                                service_info = self._get_service_info(change)
                                report_lines.append(f"{basic_info} - {service_info}")
                            
                            elif comp_type == "Error Handlers":
                                # Get error handling info
                                error_info = self._get_error_handler_info(change)
                                report_lines.append(f"{basic_info} ({error_info})")
                            
                            else:
                                report_lines.append(basic_info)
                        
                        report_lines.append("")  # Empty line after each change type
                
                report_lines.append("")  # Extra empty line after component type
        
        report_lines.extend([
            "",
            "=" * 60,
            "End of Diff Report",
            "=" * 60
        ])
        
        return "\n".join(report_lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "blueprint1_name": self.blueprint1_name,
            "blueprint2_name": self.blueprint2_name,
            "blueprint1_path": self.blueprint1_path,
            "blueprint2_path": self.blueprint2_path,
            "platform": self.metadata.platform.value,
            "generated_at": self.metadata.generated_at.isoformat(),
            "summary": {
                "total_changes": self.summary.total_changes,
                "change_counts": self.summary.change_counts,
                "structural_change_score": self.summary.structural_change_score,
                "change_scale": self.summary.change_scale.value,
                "change_magnitude": self.summary.change_magnitude
            },
            "module_changes": [
                {
                    "module_id": change.module_id,
                    "module_type": change.module_type,
                    "module_name": change.module_name,
                    "change_type": change.change_type.value,
                    "change_impact": change.change_impact.value if change.change_impact else None,
                    "configuration_changes_count": len(change.configuration_changes),
                    "impact_description": change.impact_description
                }
                for change in self.module_changes
            ],
            "structural_changes": [
                {
                    "description": change.change_description,
                    "affected_modules_count": len(change.affected_modules),
                    "change_type": change.change_type,
                    "impact_level": change.impact_level.value
                }
                for change in self.structural_changes
            ],
            "topology_analysis": self.topology_analysis,
            "configuration_analysis": self.configuration_analysis,
            "report_text": self.to_text()  # Include formatted text for convenience
        }
    
    def _generate_component_changes_summary(self) -> List[str]:
        """Generate a summary of changes by component type."""
        component_counts = {}
        
        # Count changes by component type
        for change in self.module_changes:
            if change.change_type != ChangeType.UNCHANGED:
                component_type = self._get_component_type(change)
                component_counts[component_type] = component_counts.get(component_type, 0) + 1
        
        if not component_counts:
            return []
        
        # Sort by count (descending) then by name
        sorted_components = sorted(component_counts.items(), key=lambda x: (-x[1], x[0]))
        
        # Format as a clean table
        summary_lines = []
        
        # Calculate column widths
        max_type_width = max(len(comp_type) for comp_type, _ in sorted_components)
        type_width = max(max_type_width, 15)  # Minimum width
        
        # Add table rows
        for component_type, count in sorted_components:
            line = f"{component_type:<{type_width}} {count:>3}"
            summary_lines.append(line)
        
        return summary_lines
    
    def _get_component_type(self, change: ModuleChange) -> str:
        """Get the component type for summary display using platform-specific categorization."""
        # Use platform-specific helpers
        if self.metadata.platform == Platform.WORKFRONT_FUSION:
            from ..common.platforms.workfront_fusion import WorkfrontFusionReportingHelper
            return WorkfrontFusionReportingHelper.get_component_type(change)
        elif self.metadata.platform == Platform.MAKE_COM:
            from ..common.platforms.make_com import MakeComReportingHelper
            return MakeComReportingHelper.get_component_type(change)
        else:
            return self._get_generic_component_type(change)
    
    
    def _get_generic_component_type(self, change: ModuleChange) -> str:
        """Get generic component type for unknown platforms."""
        module_type = change.module_type.lower()
        
        if "filter" in module_type:
            return "Filters"
        elif "router" in module_type:
            return "Routers"
        elif "trigger" in module_type or "watch" in module_type:
            return "Triggers"
        elif "error" in module_type:
            return "Error Handlers"
        else:
            return "Modules"
    
    def _get_linked_module_name(self, module_id: str, all_changes: List[ModuleChange]) -> str:
        """Get the name of the module that a filter/router/error handler is linked to."""
        # Look for a module change with the same ID
        for change in all_changes:
            if change.module_id == module_id and not change.module_id.endswith(("_filter", "_router", "_error")):
                return change.module_name
        
        # If no module change found, return a generic name
        return f"Module {module_id}"
    
    def _get_filter_relationship(self, filter_change: ModuleChange, all_changes: List[ModuleChange]) -> str:
        """Get the from:to relationship for a filter based on its raw data."""
        try:
            # Check if the raw_data contains extraction_context with path information
            raw_data = filter_change.raw_data
            extraction_context = raw_data.get('_extraction_context', {})
            path = extraction_context.get('path', '')
            
            # Parse the path to find the source router
            # Path format: "module32.route0" means filter is in route 0 of module 32
            if 'module' in path and '.route' in path:
                parts = path.split('.')
                source_module_id = parts[0].replace('module', '')
                
                # Get the target module ID (remove _filter suffix)
                target_module_id = filter_change.module_id.replace('_filter', '')
                
                # Find the names
                source_name = self._get_linked_module_name(source_module_id, all_changes)
                target_name = self._get_linked_module_name(target_module_id, all_changes)
                
                return f"from Router {source_module_id}: {source_name} to Module {target_module_id}: {target_name}"
            else:
                # Fallback to simple linked format
                target_module_id = filter_change.module_id.replace('_filter', '')
                target_name = self._get_linked_module_name(target_module_id, all_changes)
                return f"linked to Module {target_module_id}: {target_name}"
        except Exception:
            # Fallback if parsing fails
            target_module_id = filter_change.module_id.replace('_filter', '')
            target_name = self._get_linked_module_name(target_module_id, all_changes)
            return f"linked to Module {target_module_id}: {target_name}"
    
    def _get_filter_condition_summary(self, filter_change: ModuleChange) -> str:
        """Get a summary of filter conditions."""
        try:
            raw_data = filter_change.raw_data
            conditions = raw_data.get('conditions', [])
            
            if not conditions:
                return "No conditions"
            
            total_conditions = sum(len(group) if isinstance(group, list) else 1 for group in conditions)
            groups = len(conditions)
            
            if groups == 1 and total_conditions == 1:
                # Single condition - show the actual condition
                condition = conditions[0][0] if isinstance(conditions[0], list) else conditions[0]
                a = condition.get('a', '')
                o = condition.get('o', '')
                b = condition.get('b', '')
                return f"{a} {o} {b}".strip()
            else:
                return f"{total_conditions} condition(s) in {groups} group(s)"
        except Exception:
            return "Complex conditions"
    
    def _get_router_info(self, router_change: ModuleChange) -> str:
        """Get router information."""
        try:
            raw_data = router_change.raw_data
            routes = raw_data.get('routes', [])
            route_count = len(routes) if routes else 0
            
            router_type = "BasicRouter"
            if "BasicRouter" in router_change.module_type:
                router_type = "Basic Router"
            elif "router" in router_change.module_type.lower():
                router_type = "Custom Router"
            
            return f"{router_type}, {route_count} route(s)"
        except Exception:
            return "Router"
    
    def _get_service_info(self, module_change: ModuleChange) -> str:
        """Get service and operation information for modules."""
        try:
            module_type = module_change.module_type
            
            # Parse service and action from module type
            if ':' in module_type:
                service, action = module_type.split(':', 1)
                
                # Clean up service names
                service_names = {
                    'workfront-workfront': 'Workfront',
                    'http': 'HTTP API',
                    'email': 'Email',
                    'csv': 'CSV Processing',
                    'json': 'JSON Processing',
                    'xml': 'XML Processing',
                    'builtin': 'System'
                }
                
                service_display = service_names.get(service, service.title())
                
                # Clean up action names
                action_display = action.replace('v3', '').replace('V3', '').strip()
                
                return f"{service_display}: {action_display}"
            else:
                return module_type
        except Exception:
            return module_change.module_type
    
    def _get_error_handler_info(self, error_change: ModuleChange) -> str:
        """Get error handler information."""
        try:
            raw_data = error_change.raw_data
            # Error handlers might have different structures
            handler_type = raw_data.get('type', 'Error Handler')
            return f"{handler_type}"
        except Exception:
            return "Error Handler"
    
    def _get_filter_text_content(self, filter_change: ModuleChange) -> List[str]:
        """Get filter text content showing the actual filter conditions."""
        content_lines = []
        
        try:
            if filter_change.change_type == ChangeType.ADDED:
                # For new filters, show current content
                filter_content = self._extract_filter_conditions_text(filter_change.raw_data)
                if filter_content:
                    content_lines.append("  Added:")
                    content_lines.extend([f"      {line}" for line in filter_content])
                    
            elif filter_change.change_type == ChangeType.REMOVED:
                # For removed filters, show what was removed
                filter_content = self._extract_filter_conditions_text(filter_change.raw_data)
                if filter_content:
                    content_lines.append("  Removed:")
                    content_lines.extend([f"      {line}" for line in filter_content])
                    
            elif filter_change.change_type in [ChangeType.CONFIGURATION_CHANGED, ChangeType.STRUCTURALLY_MOVED]:
                # For updated filters, show before and after
                if filter_change.raw_data_before:
                    # Show before state
                    before_content = self._extract_filter_conditions_text(filter_change.raw_data_before)
                    if before_content:
                        content_lines.append("  Before:")
                        content_lines.extend([f"      {line}" for line in before_content])
                
                # Show after state
                after_content = self._extract_filter_conditions_text(filter_change.raw_data)
                if after_content:
                    content_lines.append("  After:")
                    content_lines.extend([f"      {line}" for line in after_content])
                    
        except Exception:
            # If extraction fails, don't add content
            pass
            
        return content_lines
    
    def _extract_filter_conditions_text(self, raw_data: Dict[str, Any]) -> List[str]:
        """Extract readable text from filter conditions."""
        text_parts = []
        
        try:
            # Look for filter data - could be nested or direct
            filter_data = raw_data.get('filter', {})
            if not filter_data:
                # Sometimes conditions are directly in raw_data
                filter_data = raw_data
            
            # Extract and format conditions (skip filter name since it's in the main line)
            conditions = filter_data.get('conditions', [])
            if isinstance(conditions, list) and conditions:
                for group_idx, condition_group in enumerate(conditions):
                    if isinstance(condition_group, list):
                        if len(conditions) > 1:
                            text_parts.append(f"--- Group {group_idx + 1} ---")
                        
                        for condition in condition_group:
                            if isinstance(condition, dict):
                                a = condition.get('a', '').strip()
                                o = condition.get('o', '').strip()
                                b = condition.get('b', '').strip()
                                
                                # Format the condition readably
                                if a and o and b:
                                    text_parts.append(f"If {a} {o} {b}")
                                elif a and o:
                                    text_parts.append(f"If {a} {o}")
                                elif a:
                                    text_parts.append(f"Check: {a}")
                                    
        except Exception:
            # If parsing fails, return empty list
            pass
            
        return text_parts
    
    def _get_change_scale_description(self) -> str:
        """Get detailed description for the change scale classification."""
        change_scale = self.summary.change_scale
        
        if change_scale == ChangeScale.UNCHANGED:
            return "No detectable structural deltas. After normalization and canonicalization, the node set, edge set, parameters, and mappings match exactly with zero additions, removals, or modifications."
        
        elif change_scale == ChangeScale.MINOR:
            return "Small localized structural differences relative to the full normalized blueprint. Examples include low-count modifications such as: a few node parameter changes, a small number of added/removed nodes, slight branch or mapping adjustments. Footprint change is present but limited."
        
        elif change_scale == ChangeScale.MODERATE:
            return "Noticeable structural differences affecting a contained portion of the workflow. Changes may involve multiple nodes, parameters, or localized subgraphs. The overall structure remains mostly similar, but the delta is visibly larger than MINOR."
        
        elif change_scale == ChangeScale.MAJOR:
            return "Significant structural modification across a substantial portion of the workflow. Multiple regions, branches, or module clusters differ from the original. This band covers wide, meaningful topological changes without a full rebuild."
        
        elif change_scale == ChangeScale.EXTENSIVE:
            return "Large-scale structural divergence. A majority of the modules, paths, or graph segments differ from the original. The workflows still share some foundational elements, but the footprint overlap is limited."
        
        elif change_scale == ChangeScale.DIFFERENT_SCENARIOS:
            return "The workflows share minimal structural similarity. Most of the normalized graph is different: nodes, edges, parameters, or full branches. At this level, the blueprints are effectively separate workflows with only incidental overlap."
        
        else:
            return change_scale.value.title()

    def _get_filter_relationship(self, filter_change: ModuleChange, all_changes: List[ModuleChange]) -> str:
        """Get the from:to relationship description for a filter."""
        # Extract source router information from component metadata
        source_router_id = None
        target_module_id = filter_change.module_id.replace("_filter", "")
        
        # Look for source router information in the component metadata
        if filter_change.component_metadata:
            source_router_id = filter_change.component_metadata.get('source_router_id')
        
        # Get target module name
        target_module_name = self._get_linked_module_name(target_module_id, all_changes)
        
        # Build relationship description
        if source_router_id:
            source_router_name = self._get_linked_module_name(source_router_id, all_changes)
            return f"(from Router {source_router_id}: {source_router_name} to Module {target_module_id}: {target_module_name})"
        else:
            # Fallback to the old format if we can't determine the source router
            return f"(linked to Module {target_module_id}: {target_module_name})"


def generate_diff_report(blueprint1: Dict[str, Any], blueprint2: Dict[str, Any]) -> ProjectionResult[BlueprintDiffReport]:
    """
    Generate diff report using platform-specific reporting helpers.
    
    This function routes to platform-specific diff generation while maintaining 
    clean separation between analysis (projections) and presentation (reporting).
    """
    # Detect platforms and validate
    platform1 = detect_platform(blueprint1)
    platform2 = detect_platform(blueprint2)
    
    if platform1 != platform2:
        raise ValueError(f"Platform mismatch: {platform1.value} vs {platform2.value}. Cannot compare blueprints from different platforms.")
    
    platform = platform1
    
    # Route to platform-specific diff generation
    if platform == Platform.WORKFRONT_FUSION:
        from ..common.platforms.workfront_fusion import WorkfrontFusionReportingHelper
        return WorkfrontFusionReportingHelper.generate_diff_report(blueprint1, blueprint2)
    elif platform == Platform.MAKE_COM:
        from ..common.platforms.make_com import MakeComReportingHelper
        return MakeComReportingHelper.generate_diff_report(blueprint1, blueprint2)
    else:
        raise ValueError(f"Diff reporting not implemented for platform: {platform}")