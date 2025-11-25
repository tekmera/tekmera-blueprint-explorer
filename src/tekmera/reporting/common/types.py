"""Base types and interfaces for reporting."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict

from tekmera.functions.meta.types import Platform


class ReportFormat(Enum):
    """Supported report output formats."""

    TEXT = "text"
    JSON = "json"
    HTML = "html"
    TABLE = "table"


class ReportType(Enum):
    """Types of reports that can be generated."""

    SUMMARY = "summary"
    DIFF = "diff"
    ANALYSIS = "analysis"
    COMPARISON = "comparison"


@dataclass
class ReportMetadata:
    """Common metadata for all reports."""

    report_type: ReportType
    platform: Platform
    generated_at: datetime
    version: str = "1.0"


class BaseReport(ABC):
    """Abstract base class for all reports."""

    def __init__(self, metadata: ReportMetadata):
        self.metadata = metadata

    @abstractmethod
    def to_text(self) -> str:
        """Generate formatted text representation."""

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""

    def to_json(self) -> str:
        """Generate JSON representation."""
        import json

        return json.dumps(self.to_dict(), indent=2, default=str)

    def _format_platform(self) -> str:
        """Format platform name for display."""
        if self.metadata.platform == Platform.WORKFRONT_FUSION:
            return "Workfront Fusion"
        elif self.metadata.platform == Platform.MAKE_COM:
            return "Make.com"
        else:
            return self.metadata.platform.value.replace("_", " ").title()
