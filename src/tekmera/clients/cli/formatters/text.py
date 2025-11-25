"""Text-based formatters (table and JSON) for CLI output."""

from tekmera.reporting.common.types import BaseReport, ReportFormat, ReportType

from .base import BaseFormatter, register_formatter


@register_formatter(ReportType.SUMMARY, ReportFormat.TABLE)
@register_formatter(ReportType.DIFF, ReportFormat.TABLE)
class TableFormatter(BaseFormatter):
    """Formatter for table/text output - works for any report type."""

    def render(self, report: BaseReport) -> str:
        """Render report as formatted text table."""
        return report.to_text()

    def get_file_extension(self) -> str:
        """Table format goes to stdout, no file extension needed."""
        return ""

    def should_write_to_file(self) -> bool:
        """Table output goes to stdout."""
        return False


@register_formatter(ReportType.SUMMARY, ReportFormat.JSON)
@register_formatter(ReportType.DIFF, ReportFormat.JSON)
class JSONFormatter(BaseFormatter):
    """Formatter for JSON output - works for any report type."""

    def render(self, report: BaseReport) -> str:
        """Render report as JSON."""
        return report.to_json()

    def get_file_extension(self) -> str:
        """JSON format goes to stdout, no file extension needed."""
        return ""

    def should_write_to_file(self) -> bool:
        """JSON output goes to stdout."""
        return False
