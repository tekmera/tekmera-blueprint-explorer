"""
Connection-related governance rules.
"""
from typing import Dict, List, Any
from rich.console import Console
from ..models import GovernanceViolation
from ...analysis.connections import display_connection_table, classify_connection_environment, ConnectionAnalyzer


def check_dev_connection_in_prod(blueprint_data: Dict[str, Any], scenario_name: str) -> List[GovernanceViolation]:
    """Check 5: Dev Connection in Prod (GOV-CONN-001)"""
    violations = []
    
    # Assume production scenarios start with SA_ or don't have DEV_ prefix
    is_production = not scenario_name.startswith("DEV_")
    
    if not is_production:
        violations.append(GovernanceViolation(
            rule_id="GOV-CONN-001",
            rule_title="Dev Connection in Prod",
            message="✅ SKIPPED: Non-production scenario (DEV_ prefix detected).",
            suggested_fix="Check is only applicable to production scenarios.",
            rule_description="Prevents production scenarios from using development or testing connections. "
                            "Using dev connections in production can cause data integrity issues, security vulnerabilities, "
                            "performance problems, and service disruptions. Production scenarios should only connect to "
                            "production-grade systems with appropriate security and reliability controls.",
            is_violation=False
        ))
        return violations
    
    # Use centralized connection analyzer
    analyzer = ConnectionAnalyzer()
    connection_analysis = analyzer.analyze_blueprint_connections(blueprint_data, scenario_name)
    
    connection_labels = connection_analysis['connection_labels']
    connections_for_table = connection_analysis['connections']
    found_connections = []
    
    # Convert analysis results to expected format for backward compatibility
    for conn_id, usages in connections_for_table.items():
        for usage in usages:
            found_connections.append((conn_id, usage['context']))
    
    # Development connection keywords (including Workfront-specific patterns)
    dev_keywords = ['dev', 'sandbox', 'test', 'staging', 'demo', 'preview', 'sb01', 'sb02', 'sb03', 'sb04', 'sb05']
    dev_connections_found = []
    
    # Check all found connections for dev keywords, but only record each connection once
    processed_connections = set()
    for connection_id, context in found_connections:
        # Skip if we've already processed this connection
        if connection_id in processed_connections:
            continue
            
        connection_label = connection_labels.get(connection_id, f"Connection {connection_id}")
        connection_lower = connection_label.lower()
        
        # Check if connection label contains development keywords
        for keyword in dev_keywords:
            if keyword in connection_lower:
                is_orphan = 'orphan' in context.lower()
                
                # Collect all contexts where this connection appears
                all_contexts = [ctx for conn_id, ctx in found_connections if conn_id == connection_id]
                
                dev_connections_found.append({
                    'id': connection_id,
                    'label': connection_label,
                    'contexts': all_contexts,  # Store all contexts
                    'keyword': keyword,
                    'is_orphan': any('orphan' in ctx.lower() for ctx in all_contexts)
                })
                processed_connections.add(connection_id)
                break
    
    # Generate violations for each dev connection found (only once per connection)
    for dev_conn in dev_connections_found:
        # Extract module locations for troubleshooting
        contexts = dev_conn.get('contexts', [])
        module_locations = []
        for context in contexts:
            if 'flow[' in context:
                import re
                match = re.search(r'flow\[(\d+)\]', context)
                if match:
                    module_locations.append(f"Module {int(match.group(1))+1}")
            elif 'orphan' in context.lower():
                module_locations.append("Orphan module")
        
        location_text = ", ".join(set(module_locations)) if module_locations else "Unknown location"
        
        violations.append(GovernanceViolation(
            rule_id="GOV-CONN-001",
            rule_title="Dev Connection in Prod",
            message=f"❌ DEV CONNECTION IN PROD: Production scenario uses development connection '{dev_conn['label']}' (keyword: '{dev_conn['keyword']}') found in: {location_text}.",
            suggested_fix="Replace with a production-grade connection.",
            rule_description="Prevents production scenarios from using development or testing connections. "
                            "Using dev connections in production can cause data integrity issues, security vulnerabilities, "
                            "performance problems, and service disruptions. Production scenarios should only connect to "
                            "production-grade systems with appropriate security and reliability controls.",
            is_violation=True
        ))
    
    # Use the connection data from the analyzer (already has proper types and environment classification)
    connection_types = connection_analysis['connection_types']
    
    # Display connection table
    console = Console()
    console.print(f"\n[bold blue]Connection Analysis for {scenario_name}:[/bold blue]")
    display_connection_table(
        console=console,
        connections=connections_for_table, 
        connection_labels=connection_labels,
        title=f"Connections in {scenario_name}",
        show_labels=True,
        show_environment=True
    )
    
    # Add summary result
    if not violations:
        total_connections = len(connection_labels)
        
        violations.append(GovernanceViolation(
            rule_id="GOV-CONN-001",
            rule_title="Dev Connection in Prod",
            message=f"✅ NO DEV CONNECTIONS: {total_connections} connection(s) analyzed, none contain development keywords.",
            suggested_fix="Connection hygiene is properly maintained.",
            rule_description="Prevents production scenarios from using development or testing connections. "
                            "Using dev connections in production can cause data integrity issues, security vulnerabilities, "
                            "performance problems, and service disruptions. Production scenarios should only connect to "
                            "production-grade systems with appropriate security and reliability controls.",
            is_violation=False
        ))
    
    return violations

