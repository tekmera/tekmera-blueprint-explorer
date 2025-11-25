"""Common reporting functionality shared across report types.

This module contains base types, platform helpers, and shared utilities
used by both summary and diff reporting.
"""

from .platforms import MakeComReportingHelper, WorkfrontFusionReportingHelper
from .types import BaseReport, ReportFormat, ReportMetadata, ReportType

__all__ = [
    "BaseReport",
    "ReportMetadata",
    "ReportType",
    "ReportFormat",
    "WorkfrontFusionReportingHelper",
    "MakeComReportingHelper",
]
