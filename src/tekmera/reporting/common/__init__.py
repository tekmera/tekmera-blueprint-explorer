"""Common reporting functionality shared across report types.

This module contains base types, platform helpers, and shared utilities
used by both summary and diff reporting.
"""

from .types import BaseReport, ReportMetadata, ReportType, ReportFormat
from .platforms import WorkfrontFusionReportingHelper, MakeComReportingHelper

__all__ = [
    "BaseReport",
    "ReportMetadata", 
    "ReportType",
    "ReportFormat",
    "WorkfrontFusionReportingHelper",
    "MakeComReportingHelper"
]