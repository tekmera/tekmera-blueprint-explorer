"""Text renderers for diff reports.

This module separates the presentation logic from the data structures,
following the single responsibility principle.
"""

from typing import Any, Dict, List

from .diff import BlueprintDiffReport, ChangeType, ModuleChange


class DiffReportTextRenderer:
    """Renders diff reports to formatted text."""

    def __init__(self, report: BlueprintDiffReport):
        self.report = report

    def render(self) -> str:
        """Generate formatted text diff report."""
        sections = [
            self._render_header(),
            self._render_change_analysis(),
            self._render_component_changes(),
            self._render_footer(),
        ]
        
        return "\n".join(sections)

    def _render_header(self) -> str:
        """Render the report header section."""
        return "\n".join(
            [
                "=" * 60,
                "BLUEPRINT DIFF REPORT",
                "=" * 60,
                "",
                f"Comparing:",
                f"  First: {self.report.blueprint1_name}",
                f"  Second: {self.report.blueprint2_name}",
                f"Platform: {self.report._format_platform()}",
                f"Generated: {self.report.metadata.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
                "",
            ]
        )

    def _render_change_analysis(self) -> str:
        """Render the change analysis section."""
        changed_components = [
            c for c in self.report.module_changes if c.change_type != ChangeType.UNCHANGED
        ]
        component_types = self._get_unique_component_types(changed_components)

        lines = [
            "CHANGE ANALYSIS",
            "=" * 60,
            "",
            f"Change Magnitude: {self.report.summary.change_magnitude:.1%} ({self.report._get_change_scale_description()})",
            f"Total Number of Changes: {len(changed_components)}",
            "",
            "Types of Components Changed:",
        ]

        for comp_type in sorted(component_types):
            lines.append(f"- {comp_type}")

        lines.append("")

        return "\n".join(lines)

    def _render_component_changes(self) -> str:
        """Render the detailed component changes section."""
        changed_components = [
            c for c in self.report.module_changes if c.change_type != ChangeType.UNCHANGED
        ]
        component_types = self._get_unique_component_types(changed_components)

        sections = []
        
        for comp_type in sorted(component_types):
            sections.append(self._render_component_type_section(comp_type, changed_components))

        return "\n\n".join(sections)

    def _render_component_type_section(
        self, comp_type: str, all_changes: List[ModuleChange]
    ) -> str:
        """Render a section for a specific component type."""
        # Get components of this type, ordered by module ID
        type_components = []
        for change in all_changes:
            if self.report._get_component_type(change) == comp_type:
                type_components.append(change)
        
        # Sort by module ID
        type_components.sort(key=self._sort_key)

        lines = [
            f"{comp_type.upper()}",
            "-" * len(comp_type),
        ]

        for change in type_components:
            lines.append(self._render_change_item(change, all_changes))

        return "\n".join(lines)

    def _render_change_item(self, change: ModuleChange, all_changes: List[ModuleChange]) -> str:
        """Render a single change item."""
        if change.change_type == ChangeType.ADDED:
            return f"+ {change.module_name} (Module {change.module_id}): Added"
        elif change.change_type == ChangeType.REMOVED:
            return f"- {change.module_name} (Module {change.module_id}): Removed"
        elif change.change_type == ChangeType.CONFIGURATION_CHANGED:
            config_summary = self._get_configuration_summary(change)
            return f"* {change.module_name} (Module {change.module_id}): {config_summary}"
        elif change.change_type == ChangeType.STRUCTURALLY_MOVED:
            return f"↻ {change.module_name} (Module {change.module_id}): Moved or repositioned"
        else:
            return f"? {change.module_name} (Module {change.module_id}): {change.change_type.value}"

    def _render_footer(self) -> str:
        """Render the report footer."""
        return "\n".join(["", "=" * 60, "End of Report", "=" * 60])

    def _get_unique_component_types(self, changes: List[ModuleChange]) -> set:
        """Get unique component types from changes."""
        component_types = set()
        for change in changes:
            component_type = self.report._get_component_type(change)
            component_types.add(component_type)
        return component_types

    def _sort_key(self, change: ModuleChange):
        """Sort key for module changes."""
        try:
            return (0, int(change.module_id))  # (type, value) tuple for consistent sorting
        except ValueError:
            return (1, change.module_id)  # Strings come after integers

    def _get_configuration_summary(self, change: ModuleChange) -> str:
        """Get a summary of configuration changes."""
        if change.configuration_changes:
            if len(change.configuration_changes) == 1:
                config = change.configuration_changes[0]
                if "filter" in config.get("description", "").lower():
                    return f"Filter updated ({config.get('field', 'unknown field')})"
                return f"Configuration updated ({config.get('field', 'unknown field')})"
            else:
                return f"Configuration updated ({len(change.configuration_changes)} changes)"
        else:
            return "Configuration updated"


class DiffReportJSONRenderer:
    """Renders diff reports to JSON format."""

    def __init__(self, report: BlueprintDiffReport):
        self.report = report

    def render(self) -> Dict[str, Any]:
        """Generate JSON-serializable dict representation."""
        return {
            "blueprint1_name": self.report.blueprint1_name,
            "blueprint2_name": self.report.blueprint2_name,
            "blueprint1_path": self.report.blueprint1_path,
            "blueprint2_path": self.report.blueprint2_path,
            "platform": self.report.metadata.platform.value,
            "generated_at": self.report.metadata.generated_at.isoformat(),
            "summary": {
                "total_changes": self.report.summary.total_changes,
                "change_counts": self.report.summary.change_counts,
                "structural_change_score": self.report.summary.structural_change_score,
                "change_scale": self.report.summary.change_scale.value,
                "change_magnitude": self.report.summary.change_magnitude,
            },
            "module_changes": [
                {
                    "module_id": change.module_id,
                    "module_type": change.module_type,
                    "module_name": change.module_name,
                    "change_type": change.change_type.value,
                    "configuration_changes_count": len(change.configuration_changes),
                    "description": change.description,
                }
                for change in self.report.module_changes
            ],
            "structural_changes": [
                {
                    "description": change.change_description,
                    "affected_modules_count": len(change.affected_modules),
                    "change_type": change.change_type,
                }
                for change in self.report.structural_changes
            ],
            "topology_analysis": self.report.topology_analysis,
            "configuration_analysis": self.report.configuration_analysis,
            "report_text": self.report.to_text(),  # Include formatted text for convenience
        }
