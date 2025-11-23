"""Base formatter interfaces and registry for CLI output formatting."""

from abc import ABC, abstractmethod
from typing import Dict, Type, Tuple

from tekmera.reporting.common.types import BaseReport, ReportType, ReportFormat


class BaseFormatter(ABC):
    """Abstract base class for all report formatters."""
    
    @abstractmethod
    def render(self, report: BaseReport) -> str:
        """Render a report to string format.
        
        Args:
            report: The report object to render
            
        Returns:
            Formatted string representation of the report
        """
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """Get the appropriate file extension for this format."""
        pass
    
    @abstractmethod
    def should_write_to_file(self) -> bool:
        """Whether this formatter should write to a file vs stdout."""
        pass


class FormatterRegistry:
    """Registry for managing formatters by report type and format combination."""
    
    def __init__(self):
        self._formatters: Dict[Tuple[ReportType, ReportFormat], Type[BaseFormatter]] = {}
    
    def register(self, report_type: ReportType, format_type: ReportFormat, formatter_class: Type[BaseFormatter]):
        """Register a formatter for a specific report type and format combination.
        
        Args:
            report_type: The type of report (SUMMARY, DIFF, etc.)
            format_type: The output format (HTML, TABLE, JSON)
            formatter_class: The formatter class to handle this combination
        """
        key = (report_type, format_type)
        self._formatters[key] = formatter_class
    
    def get_formatter(self, report_type: ReportType, format_type: ReportFormat) -> BaseFormatter:
        """Get the appropriate formatter for a report type and format.
        
        Args:
            report_type: The type of report
            format_type: The desired output format
            
        Returns:
            Instantiated formatter object
            
        Raises:
            ValueError: If no formatter is registered for the combination
        """
        key = (report_type, format_type)
        
        if key not in self._formatters:
            available = list(self._formatters.keys())
            raise ValueError(
                f"No formatter registered for {report_type.value} reports in {format_type.value} format. "
                f"Available combinations: {available}"
            )
        
        formatter_class = self._formatters[key]
        return formatter_class()
    
    def list_supported_combinations(self) -> Dict[str, Dict[str, bool]]:
        """Get a map of supported report type + format combinations.
        
        Returns:
            Nested dict: {report_type: {format: True}}
        """
        result = {}
        for (report_type, format_type) in self._formatters.keys():
            if report_type.value not in result:
                result[report_type.value] = {}
            result[report_type.value][format_type.value] = True
        return result


# Global formatter registry instance
_registry = FormatterRegistry()


def register_formatter(report_type: ReportType, format_type: ReportFormat):
    """Decorator for registering formatters.
    
    Usage:
        @register_formatter(ReportType.SUMMARY, ReportFormat.HTML)
        class HTMLSummaryFormatter(BaseFormatter):
            ...
    """
    def decorator(formatter_class: Type[BaseFormatter]):
        _registry.register(report_type, format_type, formatter_class)
        return formatter_class
    return decorator


def get_formatter(report_type: ReportType, format_type: ReportFormat) -> BaseFormatter:
    """Get the appropriate formatter for a report type and format.
    
    This is the main entry point for CLI code to get formatters.
    """
    return _registry.get_formatter(report_type, format_type)


def list_supported_formats() -> Dict[str, Dict[str, bool]]:
    """Get all supported report type and format combinations."""
    return _registry.list_supported_combinations()