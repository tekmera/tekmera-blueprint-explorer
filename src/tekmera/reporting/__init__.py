"""Platform-agnostic reporting module for Tekmera.

This module provides platform-independent report generation, formatting,
and presentation capabilities. It consumes data from projections modules
and presents it in various formats (text, JSON, HTML).
"""

from .summary.summary import BlueprintSummaryReport, generate_summary_report
from .diff.diff import BlueprintDiffReport, generate_diff_report
from .common.types import ReportFormat, ReportType

__all__ = [
    "BlueprintSummaryReport",
    "BlueprintDiffReport", 
    "generate_summary_report",
    "generate_diff_report",
    "ReportFormat",
    "ReportType"
]