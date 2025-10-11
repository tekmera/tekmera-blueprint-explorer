"""
Data models for governance checking.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class GovernanceViolation:
    """Represents a governance rule violation or result."""

    rule_id: str
    rule_title: str
    message: str
    suggested_fix: str
    rule_description: str = ""
    module_id: Optional[str] = None
    module_name: Optional[str] = None
    is_violation: bool = True  # False for informational results
