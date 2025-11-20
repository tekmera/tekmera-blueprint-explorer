"""
Blueprint diff report type definitions.

This module defines the structured data types for blueprint comparison reports.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from ...meta.types import Platform


class ChangeType(Enum):
    """Types of changes that can occur to modules."""
    UNCHANGED = "unchanged"
    CONFIGURATION_CHANGED = "configuration_changed"
    STRUCTURALLY_MOVED = "structurally_moved"
    ADDED = "added"
    REMOVED = "removed"


class ChangeSeverity(Enum):
    """Severity classification for configuration changes."""
    COSMETIC = "cosmetic"        # Names, positions, UI metadata
    MINOR = "minor"              # Non-critical parameter changes
    MODERATE = "moderate"        # Significant config changes
    MAJOR = "major"             # Flow logic changes
    CRITICAL = "critical"       # Breaking changes


class RiskLevel(Enum):
    """Overall risk assessment for the diff."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ModuleChange:
    """Details of changes to a specific module."""
    module_id: str
    module_type: str
    module_name: str
    change_type: ChangeType
    
    # Configuration changes (if applicable)
    configuration_changes: List[Dict[str, Any]] = field(default_factory=list)
    change_severity: Optional[ChangeSeverity] = None
    
    # Structural changes (if moved)
    old_position: Optional[Dict[str, Any]] = None
    new_position: Optional[Dict[str, Any]] = None
    
    # Impact description
    impact_description: str = ""


@dataclass
class StructuralChange:
    """Structural changes to the blueprint topology."""
    change_description: str
    affected_modules: List[str]
    change_type: str  # "edge_added", "edge_removed", "path_changed", etc.
    impact_level: ChangeSeverity


@dataclass
class DiffSummary:
    """High-level summary of all changes."""
    total_changes: int
    change_counts: Dict[str, int]  # {added: 2, removed: 1, moved: 3, changed: 5}
    structural_change_score: float  # 0.0 = identical, 1.0 = completely different
    risk_level: RiskLevel
    breaking_changes_count: int


@dataclass
class BlueprintDiffReport:
    """
    Comprehensive diff report between two blueprints.
    
    This report contains structured data about differences that can be
    rendered in multiple formats (text, PDF, JSON, etc.).
    """
    # Basic metadata
    blueprint1_name: str
    blueprint2_name: str
    blueprint1_path: Optional[str] = None
    blueprint2_path: Optional[str] = None
    platform: Platform = Platform.WORKFRONT_FUSION
    generated_at: datetime = field(default_factory=datetime.now)
    
    # High-level summary
    summary: DiffSummary = field(default_factory=lambda: DiffSummary(
        total_changes=0,
        change_counts={},
        structural_change_score=0.0,
        risk_level=RiskLevel.LOW,
        breaking_changes_count=0
    ))
    
    # Detailed analysis
    module_changes: List[ModuleChange] = field(default_factory=list)
    structural_changes: List[StructuralChange] = field(default_factory=list)
    
    # Future sections (stubs for now)
    topology_analysis: Dict[str, Any] = field(default_factory=dict)
    configuration_analysis: Dict[str, Any] = field(default_factory=dict)
    
    def to_text(self) -> str:
        """Generate formatted text diff report."""
        report_lines = [
            "=" * 60,
            "BLUEPRINT DIFF REPORT", 
            "=" * 60,
            "",
            f"Comparing:",
            f"  Before: {self.blueprint1_name}",
            f"  After:  {self.blueprint2_name}",
            f"Platform: {self._format_platform()}",
            f"Generated: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "SUMMARY",
            "-" * 30,
            f"Total Changes: {self.summary.total_changes}",
            f"Risk Level: {self.summary.risk_level.value.title()}",
            f"Structural Change Score: {self.summary.structural_change_score:.2f}",
            "",
        ]
        
        # Add change breakdown
        if self.summary.change_counts:
            report_lines.append("Change Breakdown:")
            for change_type, count in self.summary.change_counts.items():
                if count > 0:
                    report_lines.append(f"  • {change_type.replace('_', ' ').title()}: {count}")
            report_lines.append("")
        
        # Add module changes
        if self.module_changes:
            report_lines.extend([
                "MODULE CHANGES",
                "-" * 30,
            ])
            
            for change in self.module_changes:
                report_lines.append(f"• {change.module_name} ({change.module_type})")
                report_lines.append(f"  Status: {change.change_type.value.replace('_', ' ').title()}")
                
                if change.change_severity:
                    report_lines.append(f"  Severity: {change.change_severity.value.title()}")
                
                if change.impact_description:
                    report_lines.append(f"  Impact: {change.impact_description}")
                
                if change.configuration_changes:
                    report_lines.append(f"  Config Changes: {len(change.configuration_changes)} fields modified")
                
                report_lines.append("")
        
        # Add structural changes
        if self.structural_changes:
            report_lines.extend([
                "STRUCTURAL CHANGES",
                "-" * 30,
            ])
            
            for change in self.structural_changes:
                report_lines.append(f"• {change.change_description}")
                report_lines.append(f"  Impact Level: {change.impact_level.value.title()}")
                if change.affected_modules:
                    report_lines.append(f"  Affected Modules: {', '.join(change.affected_modules[:3])}")
                    if len(change.affected_modules) > 3:
                        report_lines.append(f"    ... and {len(change.affected_modules) - 3} more")
                report_lines.append("")
        
        # Add recommendations or insights
        report_lines.extend([
            "RECOMMENDATIONS",
            "-" * 30,
        ])
        
        if self.summary.risk_level == RiskLevel.LOW:
            report_lines.append("• Low risk changes - safe to deploy with standard testing")
        elif self.summary.risk_level == RiskLevel.MEDIUM:
            report_lines.append("• Medium risk changes - consider additional testing")
        elif self.summary.risk_level == RiskLevel.HIGH:
            report_lines.append("• High risk changes - extensive testing recommended")
        else:
            report_lines.append("• Critical changes - thorough review and testing required")
        
        if self.summary.breaking_changes_count > 0:
            report_lines.append(f"• {self.summary.breaking_changes_count} breaking changes detected")
        
        if self.summary.structural_change_score > 0.5:
            report_lines.append("• Significant structural changes - verify flow logic carefully")
        
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
            "platform": self.platform.value,
            "generated_at": self.generated_at.isoformat(),
            "summary": {
                "total_changes": self.summary.total_changes,
                "change_counts": self.summary.change_counts,
                "structural_change_score": self.summary.structural_change_score,
                "risk_level": self.summary.risk_level.value,
                "breaking_changes_count": self.summary.breaking_changes_count
            },
            "module_changes": [
                {
                    "module_id": change.module_id,
                    "module_type": change.module_type,
                    "module_name": change.module_name,
                    "change_type": change.change_type.value,
                    "change_severity": change.change_severity.value if change.change_severity else None,
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
    
    def _format_platform(self) -> str:
        """Format platform name for display."""
        if self.platform == Platform.WORKFRONT_FUSION:
            return "Workfront Fusion"
        elif self.platform == Platform.MAKE_COM:
            return "Make.com"
        else:
            return self.platform.value.replace('_', ' ').title()