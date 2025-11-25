"""Graph analysis module for blueprint diff engine.

This module provides platform-agnostic algorithms for comparing topology graphs
and detecting structural changes between blueprint versions.
"""

from .scoring import (
    calculate_change_counts,
    calculate_structural_change_score,
    calculate_structural_similarity,
    classify_change_scope,
)
from .structural import compare_graphs, detect_node_changes

__all__ = [
    "compare_graphs",
    "detect_node_changes",
    "calculate_structural_change_score",
    "classify_change_scope",
    "calculate_change_counts",
    "calculate_structural_similarity",
]
