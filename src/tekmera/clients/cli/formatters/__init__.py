"""CLI formatters for different report types and output formats."""

# Import all formatters to ensure they register themselves
from . import html_diff  # noqa: F401
from . import html_summary  # noqa: F401
from . import text  # noqa: F401
from .base import get_formatter, list_supported_formats

# Legacy imports for backward compatibility
from .html_diff import render_report_to_html
from .table import format_result

__all__ = [
    "get_formatter",
    "list_supported_formats",
    "render_report_to_html",  # Legacy
    "format_result",  # Legacy
]
