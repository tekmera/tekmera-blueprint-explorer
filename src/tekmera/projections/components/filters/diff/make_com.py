"""Make.com filter-specific diff analysis."""

from typing import Any, Dict, List
from . import FilterDifference


def analyze_make_com_filter(old_filter: Dict[str, Any], new_filter: Dict[str, Any]) -> List[FilterDifference]:
    """
    Analyze differences between Make.com filters.
    """
    differences = []
    
    # Basic implementation for Make.com filters
    if old_filter != new_filter:
        differences.append(FilterDifference(
            field_path="filter",
            old_value=old_filter,
            new_value=new_filter,
            change_type="modified",
            significance="important",
            description="Filter configuration changed",
            logical_impact="changes_logic"
        ))
    
    return differences