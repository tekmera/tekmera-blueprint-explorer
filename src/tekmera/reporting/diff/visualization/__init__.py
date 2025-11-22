"""Diff visualization module for enhanced reporting.

This module provides visual representations of blueprint changes including
topology graphs, module change cards, and enhanced summary statistics.
"""

from .graph import render_topology_comparison, render_topology_ascii
from .cards import generate_change_cards, format_module_change_card
from .summary import generate_enhanced_summary, format_topology_comparison

__all__ = [
    "render_topology_comparison",
    "render_topology_ascii", 
    "generate_change_cards",
    "format_module_change_card",
    "generate_enhanced_summary",
    "format_topology_comparison"
]