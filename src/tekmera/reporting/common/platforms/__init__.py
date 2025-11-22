"""Platform-specific reporting functionality.

This module contains platform-specific logic for report generation
while keeping the common reporting interface clean and platform-agnostic.
"""

from .workfront_fusion import WorkfrontFusionReportingHelper
from .make_com import MakeComReportingHelper

__all__ = [
    "WorkfrontFusionReportingHelper",
    "MakeComReportingHelper"
]