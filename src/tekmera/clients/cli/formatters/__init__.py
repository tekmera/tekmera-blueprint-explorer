"""CLI formatters for different report types and output formats."""

# Import all formatters to ensure they register themselves
from .base import get_formatter, list_supported_formats
from . import text  # TableFormatter, JSONFormatter
from . import html_summary  # HTMLSummaryFormatter  
from . import html_diff  # HTMLDiffFormatter

# Legacy imports for backward compatibility
from .html_diff import render_report_to_html
from .table import format_result

__all__ = [
    'get_formatter',
    'list_supported_formats', 
    'render_report_to_html',  # Legacy
    'format_result',  # Legacy
]
