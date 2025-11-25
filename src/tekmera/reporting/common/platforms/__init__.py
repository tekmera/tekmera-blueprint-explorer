"""Platform-specific reporting functionality.

This module contains platform-specific logic for report generation
while keeping the common reporting interface clean and platform-agnostic.
"""

from .make_com import MakeComReportingHelper
from .workfront_fusion import WorkfrontFusionReportingHelper

__all__ = ["WorkfrontFusionReportingHelper", "MakeComReportingHelper"]
