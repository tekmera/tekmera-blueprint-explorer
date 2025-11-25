"""Diff reporting for blueprint comparison analysis.

This module provides diff report generation with topology analysis,
change detection, business impact assessment, and visualization.
"""

from .diff import (
    BlueprintDiffReport,
    ChangeScale,
    ChangeType,
    DiffSummary,
    ModuleChange,
    StructuralChange,
    generate_diff_report,
)

__all__ = [
    "BlueprintDiffReport",
    "generate_diff_report",
    "ChangeType",
    "ChangeScale",
    "ModuleChange",
    "StructuralChange",
    "DiffSummary",
]
