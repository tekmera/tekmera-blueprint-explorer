"""Diff reporting for blueprint comparison analysis.

This module provides diff report generation with topology analysis,
change detection, business impact assessment, and visualization.
"""

from .diff import BlueprintDiffReport, generate_diff_report
from .diff import ChangeType, ChangeImpact, ChangeScale, ModuleChange, StructuralChange, DiffSummary

__all__ = [
    "BlueprintDiffReport", 
    "generate_diff_report",
    "ChangeType",
    "ChangeImpact", 
    "ChangeScale",
    "ModuleChange",
    "StructuralChange",
    "DiffSummary"
]