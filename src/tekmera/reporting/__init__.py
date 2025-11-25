"""Platform-agnostic reporting module for Tekmera.

This module provides platform-independent report generation, formatting,
and presentation capabilities. It consumes data from functions modules
and presents it in various formats (text, JSON, HTML).
"""

from .common.types import ReportFormat, ReportType
from .diff.diff import BlueprintDiffReport, generate_diff_report
from .summary.summary import BlueprintSummaryReport, generate_summary_report

__all__ = [
    "BlueprintSummaryReport",
    "BlueprintDiffReport",
    "generate_summary_report",
    "generate_diff_report",
    "ReportFormat",
    "ReportType",
]
