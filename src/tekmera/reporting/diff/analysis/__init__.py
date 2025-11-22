"""Graph analysis module for blueprint diff engine.

This module provides platform-agnostic algorithms for comparing topology graphs
and detecting structural changes between blueprint versions.
"""

from .structural import compare_graphs, detect_node_changes
from .scoring import calculate_structural_change_score, classify_change_magnitude, calculate_change_counts, calculate_structural_similarity

__all__ = [
    "compare_graphs",
    "detect_node_changes", 
    "calculate_structural_change_score",
    "classify_change_magnitude",
    "calculate_change_counts",
    "calculate_structural_similarity"
]