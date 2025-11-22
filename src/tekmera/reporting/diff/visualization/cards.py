"""Module change cards for enhanced diff reporting.

This module provides rich formatting for individual module changes
with before/after context and visual indicators.
"""

from typing import List
from ..diff import ModuleChange, ChangeType, ChangeImpact


def generate_change_cards(module_changes: List[ModuleChange], max_cards: int = 20) -> List[str]:
    """
    Generate formatted change cards for multiple module changes.
    
    Creates visually appealing cards showing the details of each
    module change with appropriate formatting and context.
    
    Args:
        module_changes: List of module changes to format
        max_cards: Maximum number of cards to generate
        
    Returns:
        List of formatted change card strings
    """
    cards = []
    
    # Sort changes by severity and type for better organization
    sorted_changes = sorted(
        module_changes, 
        key=lambda c: (_get_change_priority(c), c.module_name)
    )
    
    for i, change in enumerate(sorted_changes[:max_cards]):
        if i > 0:
            cards.append("")  # Add spacing between cards
        
        card = format_module_change_card(change, card_number=i + 1)
        cards.append(card)
    
    if len(module_changes) > max_cards:
        cards.append("")
        cards.append(f"... and {len(module_changes) - max_cards} more changes")
    
    return cards


def format_module_change_card(change: ModuleChange, card_number: int = None) -> str:
    """
    Format a single module change into a rich change card.
    
    Creates a detailed card showing the module change with visual
    indicators, severity information, and impact description.
    
    Args:
        change: Module change to format
        card_number: Optional card number for numbering
        
    Returns:
        Formatted change card string
    """
    lines = []
    
    # Card header with visual indicators
    icon = _get_change_icon(change.change_type)
    severity_indicator = _get_severity_indicator(change.change_impact)
    
    header_prefix = f"[{card_number}] " if card_number else ""
    lines.append(f"{header_prefix}{icon} {change.module_name}")
    
    # Module type and ID
    lines.append(f"    Type: {change.module_type}")
    if change.module_id:
        lines.append(f"    ID: {change.module_id}")
    
    # Change status with severity
    status_line = f"    Status: {_format_change_type(change.change_type)}"
    if change.change_impact:
        status_line += f" {severity_indicator}"
    lines.append(status_line)
    
    # Impact description
    if change.impact_description:
        lines.append(f"    Impact: {change.impact_description}")
    
    # Configuration changes details
    if change.configuration_changes:
        lines.append(f"    Config Changes: {len(change.configuration_changes)} field(s) modified")
        for config_change in change.configuration_changes[:3]:  # Show first 3
            field = config_change.get("field", "unknown")
            old_val = str(config_change.get("old_value", ""))
            new_val = str(config_change.get("new_value", ""))
            
            # Smart truncation - try to preserve meaningful differences
            old_val, new_val = _smart_truncate_values(old_val, new_val)
            
            lines.append(f"      • {field}: {old_val} → {new_val}")
        
        if len(change.configuration_changes) > 3:
            remaining = len(change.configuration_changes) - 3
            lines.append(f"      ... and {remaining} more field(s)")
    
    # Position changes for moved modules
    if change.change_type == ChangeType.STRUCTURALLY_MOVED:
        if change.old_position and change.new_position:
            old_path = change.old_position.get("path", "unknown")
            new_path = change.new_position.get("path", "unknown")
            lines.append(f"    Position: {old_path} → {new_path}")
    
    # Additional context based on change type
    context_lines = _generate_change_context(change)
    if context_lines:
        lines.extend(context_lines)
    
    return "\n".join(lines)


def _get_change_priority(change: ModuleChange) -> int:
    """Get priority for sorting changes (lower number = higher priority)."""
    priority_map = {
        ChangeType.REMOVED: 1,
        ChangeType.ADDED: 2,
        ChangeType.STRUCTURALLY_MOVED: 3,
        ChangeType.CONFIGURATION_CHANGED: 4,
        ChangeType.UNCHANGED: 5
    }
    
    type_priority = priority_map.get(change.change_type, 6)
    
    # Boost priority for severe changes
    if change.change_impact in [ChangeImpact.ARCHITECTURAL, ChangeImpact.FUNCTIONAL]:
        type_priority -= 0.5
    
    return type_priority


def _get_change_icon(change_type: ChangeType) -> str:
    """Get a visual icon for the change type."""
    icon_map = {
        ChangeType.ADDED: "✓",       # Check mark for additions
        ChangeType.REMOVED: "✗",     # X for removals  
        ChangeType.STRUCTURALLY_MOVED: "↔",  # Arrow for moves
        ChangeType.CONFIGURATION_CHANGED: "~",  # Tilde for modifications
        ChangeType.UNCHANGED: "○"    # Circle for unchanged
    }
    return icon_map.get(change_type, "?")


def _get_severity_indicator(impact: ChangeImpact) -> str:
    """Get a visual indicator for change impact."""
    if not impact:
        return ""
    
    indicator_map = {
        ChangeImpact.ARCHITECTURAL: "🔴",
        ChangeImpact.FUNCTIONAL: "🟠", 
        ChangeImpact.STRUCTURAL: "🟡",
        ChangeImpact.CONFIGURATION: "🟢",
        ChangeImpact.COSMETIC: "⚪"
    }
    return indicator_map.get(impact, "")


def _format_change_type(change_type: ChangeType) -> str:
    """Format change type for display."""
    type_map = {
        ChangeType.ADDED: "Added",
        ChangeType.REMOVED: "Removed",
        ChangeType.STRUCTURALLY_MOVED: "Moved",
        ChangeType.CONFIGURATION_CHANGED: "Modified",
        ChangeType.UNCHANGED: "Unchanged"
    }
    return type_map.get(change_type, str(change_type.value))


def _generate_change_context(change: ModuleChange) -> List[str]:
    """Generate additional context lines for specific change types."""
    context = []
    
    # Special handling for different module types
    module_type_lower = change.module_type.lower()
    
    if change.change_type == ChangeType.REMOVED:
        if "trigger" in module_type_lower or change.module_type.startswith("workfront-workfront:watch"):
            context.append("    ⚠️  WARNING: Trigger removal may break workflow automation")
        elif "router" in module_type_lower or "BasicRouter" in change.module_type:
            context.append("    ⚠️  WARNING: Router removal may affect flow logic")
    
    elif change.change_type == ChangeType.ADDED:
        if "error" in module_type_lower or "onerror" in str(change.module_type):
            context.append("    ✓ Added error handling improves workflow reliability")
        elif "filter" in module_type_lower:
            context.append("    ✓ New filter adds conditional logic to workflow")
    
    elif change.change_type == ChangeType.STRUCTURALLY_MOVED:
        if change.change_impact in [ChangeImpact.FUNCTIONAL, ChangeImpact.ARCHITECTURAL]:
            context.append("    ⚠️  Structural change may affect dependent modules")
    
    return context


def _smart_truncate_values(old_val: str, new_val: str, max_length: int = 60) -> tuple[str, str]:
    """
    Intelligently truncate values while preserving meaningful differences.
    
    This function tries to find the actual differences between values and
    preserve them while truncating less important parts.
    """
    # If both values are short, don't truncate
    if len(old_val) <= max_length and len(new_val) <= max_length:
        return f"'{old_val}'", f"'{new_val}'"
    
    # Try to find differences for intelligent truncation
    if old_val == new_val:
        # Values are identical, just show truncated version
        if len(old_val) > max_length:
            return f"'{old_val[:max_length-3]}...'", f"'{new_val[:max_length-3]}...'"
        return f"'{old_val}'", f"'{new_val}'"
    
    # For different values, try to find the key differences
    old_lines = old_val.split('\n')
    new_lines = new_val.split('\n')
    
    # If it's structured data (dict/list), try to extract key parts
    if old_val.startswith('{') and new_val.startswith('{'):
        return _truncate_structured_data(old_val, new_val, max_length)
    
    # For simple string differences, find the differing parts
    if len(old_val) <= max_length * 2 and len(new_val) <= max_length * 2:
        # If reasonably sized, show more context
        old_truncated = old_val[:max_length-3] + "..." if len(old_val) > max_length else old_val
        new_truncated = new_val[:max_length-3] + "..." if len(new_val) > max_length else new_val
        return f"'{old_truncated}'", f"'{new_truncated}'"
    
    # For very long values, show beginning and try to find key differences
    old_start = old_val[:max_length//2]
    new_start = new_val[:max_length//2]
    
    return f"'{old_start}...'", f"'{new_start}...'"


def _truncate_structured_data(old_val: str, new_val: str, max_length: int) -> tuple[str, str]:
    """Truncate structured data (JSON-like) while preserving key differences."""
    try:
        import re
        import json
        
        # Try to parse as JSON first for better analysis
        try:
            old_data = eval(old_val) if old_val.startswith('{') else None
            new_data = eval(new_val) if new_val.startswith('{') else None
            
            if old_data and new_data and isinstance(old_data, dict) and isinstance(new_data, dict):
                return _compare_dict_structures(old_data, new_data, max_length)
        except:
            pass
        
        # Extract key-value pairs using regex as fallback
        old_keys = re.findall(r"'([^']+)':\s*['\"]([^'\"]+)['\"]", old_val)
        new_keys = re.findall(r"'([^']+)':\s*['\"]([^'\"]+)['\"]", new_val)
        
        old_dict = dict(old_keys) if old_keys else {}
        new_dict = dict(new_keys) if new_keys else {}
        
        # Find changed keys
        changed_keys = []
        for key in set(old_dict.keys()) | set(new_dict.keys()):
            if old_dict.get(key) != new_dict.get(key):
                changed_keys.append(key)
        
        if changed_keys and len(changed_keys) <= 3:
            # Show just the changed parts
            old_parts = []
            new_parts = []
            for key in changed_keys[:2]:  # Show max 2 key changes
                old_val_for_key = old_dict.get(key, 'missing')
                new_val_for_key = new_dict.get(key, 'missing')
                old_parts.append(f"'{key}': '{old_val_for_key}'")
                new_parts.append(f"'{key}': '{new_val_for_key}'")
            
            old_result = "{" + ", ".join(old_parts) + ("..." if len(changed_keys) > 2 else "") + "}"
            new_result = "{" + ", ".join(new_parts) + ("..." if len(changed_keys) > 2 else "") + "}"
            return old_result, new_result
    
    except Exception:
        pass
    
    # Fallback to simple truncation
    old_truncated = old_val[:max_length-3] + "..." if len(old_val) > max_length else old_val
    new_truncated = new_val[:max_length-3] + "..." if len(new_val) > max_length else new_val
    return f"'{old_truncated}'", f"'{new_truncated}'"


def _compare_dict_structures(old_data: dict, new_data: dict, max_length: int) -> tuple[str, str]:
    """Compare dictionary structures and extract key differences."""
    differences = []
    
    def find_differences(old_dict, new_dict, prefix=""):
        for key in set(old_dict.keys()) | set(new_dict.keys()):
            old_val = old_dict.get(key)
            new_val = new_dict.get(key)
            
            if old_val != new_val:
                key_path = f"{prefix}.{key}" if prefix else key
                
                if isinstance(old_val, dict) and isinstance(new_val, dict):
                    find_differences(old_val, new_val, key_path)
                else:
                    differences.append((key_path, old_val, new_val))
    
    find_differences(old_data, new_data)
    
    if differences and len(differences) <= 3:
        # Show the key differences
        old_parts = []
        new_parts = []
        
        for key_path, old_val, new_val in differences[:2]:
            old_parts.append(f"{key_path}: '{old_val}'")
            new_parts.append(f"{key_path}: '{new_val}'")
        
        old_result = "{" + ", ".join(old_parts) + ("..." if len(differences) > 2 else "") + "}"
        new_result = "{" + ", ".join(new_parts) + ("..." if len(differences) > 2 else "") + "}"
        return old_result, new_result
    
    # Fallback if too many changes
    return str(old_data)[:max_length-3] + "...", str(new_data)[:max_length-3] + "..."


def generate_change_summary_card(module_changes: List[ModuleChange]) -> str:
    """
    Generate a summary card showing overall change statistics.
    
    Creates a high-level overview of all changes with counts,
    severity distribution, and risk indicators.
    
    Args:
        module_changes: List of all module changes
        
    Returns:
        Formatted summary card string
    """
    lines = []
    
    lines.append("📊 CHANGE SUMMARY")
    lines.append("=" * 50)
    
    # Count changes by type
    change_counts = {}
    severity_counts = {}
    
    for change in module_changes:
        change_type = change.change_type
        change_counts[change_type] = change_counts.get(change_type, 0) + 1
        
        if change.change_impact:
            severity_counts[change.change_impact] = severity_counts.get(change.change_impact, 0) + 1
    
    # Show change type distribution
    lines.append("")
    lines.append("Change Types:")
    for change_type, count in change_counts.items():
        if count > 0:
            icon = _get_change_icon(change_type)
            lines.append(f"  {icon} {_format_change_type(change_type)}: {count}")
    
    # Show severity distribution
    if severity_counts:
        lines.append("")
        lines.append("Severity Levels:")
        severity_order = [ChangeImpact.ARCHITECTURAL, ChangeImpact.FUNCTIONAL, ChangeImpact.STRUCTURAL, 
                         ChangeImpact.CONFIGURATION, ChangeImpact.COSMETIC]
        
        for severity in severity_order:
            if severity in severity_counts:
                indicator = _get_severity_indicator(severity)
                lines.append(f"  {indicator} {severity.value.title()}: {severity_counts[severity]}")
    
    # Risk assessment
    critical_count = severity_counts.get(ChangeImpact.ARCHITECTURAL, 0)
    major_count = severity_counts.get(ChangeImpact.FUNCTIONAL, 0)
    removed_count = change_counts.get(ChangeType.REMOVED, 0)
    
    lines.append("")
    if critical_count > 0 or removed_count > 2:
        lines.append("⚠️  HIGH RISK: Critical changes detected")
    elif major_count > 1 or removed_count > 0:
        lines.append("🔶 MEDIUM RISK: Significant changes present") 
    else:
        lines.append("✅ LOW RISK: Changes appear safe")
    
    return "\n".join(lines)