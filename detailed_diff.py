#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
import difflib

console = Console()

def load_blueprint(file_path):
    """Load and extract blueprint data from JSON file"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Handle wrapped format
    if 'blueprint' in data:
        return data['blueprint']
    return data

def find_module_by_id(modules, module_id):
    """Find module by ID in the modules list"""
    for module in modules:
        if module.get('id') == module_id:
            return module
    return None

def get_router_routes(router_module):
    """Extract routes from a router module"""
    routes = []
    if 'routes' in router_module:
        for route in router_module['routes']:
            routes.append({
                'flow': route.get('flow', []),
                'filter': route.get('filter', {})
            })
    return routes

def find_module_in_routes(routes, target_id):
    """Find a module within router routes by ID"""
    for route_idx, route in enumerate(routes):
        for flow_item in route.get('flow', []):
            if flow_item.get('id') == target_id:
                return route_idx, flow_item
    return None, None

def compare_modules_detailed(module1, module2, module_id):
    """Compare two modules and show detailed differences"""
    console.print(f"\n[bold blue]Detailed Comparison for Module ID {module_id}[/bold blue]")
    
    if not module1 and not module2:
        console.print("[red]Both modules not found![/red]")
        return
    
    if not module1:
        console.print("[red]Module only exists in v18![/red]")
        return
    
    if not module2:
        console.print("[red]Module only exists in v17![/red]")
        return
    
    # Convert to JSON strings for comparison
    json1 = json.dumps(module1, indent=2, sort_keys=True)
    json2 = json.dumps(module2, indent=2, sort_keys=True)
    
    # Generate unified diff
    diff = list(difflib.unified_diff(
        json2.splitlines(keepends=True),
        json1.splitlines(keepends=True),
        fromfile=f'v17 (Module {module_id})',
        tofile=f'v18 (Module {module_id})',
        lineterm=''
    ))
    
    if diff:
        console.print("\n[bold yellow]JSON Diff:[/bold yellow]")
        diff_text = ''.join(diff)
        syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=True)
        console.print(syntax)
    else:
        console.print("[green]No differences found in the modules themselves.[/green]")
    
    # Compare specific fields
    fields_to_compare = ['type', 'parameters', 'mapper', 'metadata']
    
    table = Table(title=f"Field Comparison for Module {module_id}")
    table.add_column("Field", style="cyan")
    table.add_column("v17", style="magenta")
    table.add_column("v18", style="green")
    table.add_column("Status", style="yellow")
    
    for field in fields_to_compare:
        val1 = module1.get(field, "Not present")
        val2 = module2.get(field, "Not present")
        
        if val1 != val2:
            # Truncate long values for display
            val1_str = str(val1)[:100] + "..." if len(str(val1)) > 100 else str(val1)
            val2_str = str(val2)[:100] + "..." if len(str(val2)) > 100 else str(val2)
            
            table.add_row(field, val1_str, val2_str, "DIFFERENT")
        else:
            table.add_row(field, "Same", "Same", "SAME")
    
    console.print(table)

def main():
    v17_path = Path("blueprints/diff/blueprint-25635-v17.json")
    v18_path = Path("blueprints/diff/blueprint-25635-v18.json")
    
    if not v17_path.exists() or not v18_path.exists():
        console.print("[red]Blueprint files not found![/red]")
        return
    
    # Load blueprints
    bp_v17 = load_blueprint(v17_path)
    bp_v18 = load_blueprint(v18_path)
    
    # Find the router (ID: 82) and the email module (ID: 81)
    router_v17 = find_module_by_id(bp_v17['modules'], 82)
    router_v18 = find_module_by_id(bp_v18['modules'], 82)
    
    email_module_v17 = find_module_by_id(bp_v17['modules'], 81)
    email_module_v18 = find_module_by_id(bp_v18['modules'], 81)
    
    console.print("[bold green]Analysis of Router-Module Change[/bold green]")
    
    # Compare the email module directly
    console.print("\n[bold]1. Direct Module Comparison (ID: 81)[/bold]")
    compare_modules_detailed(email_module_v17, email_module_v18, 81)
    
    # Compare the router module
    console.print("\n[bold]2. Router Module Comparison (ID: 82)[/bold]")
    compare_modules_detailed(router_v17, router_v18, 82)
    
    # Look for the email module within router routes
    console.print("\n[bold]3. Email Module within Router Routes[/bold]")
    
    if router_v17 and router_v18:
        routes_v17 = get_router_routes(router_v17)
        routes_v18 = get_router_routes(router_v18)
        
        route_idx_v17, email_in_route_v17 = find_module_in_routes(routes_v17, 81)
        route_idx_v18, email_in_route_v18 = find_module_in_routes(routes_v18, 81)
        
        if email_in_route_v17 or email_in_route_v18:
            console.print(f"Email module found in routes:")
            console.print(f"  v17: Route {route_idx_v17}, Module present: {email_in_route_v17 is not None}")
            console.print(f"  v18: Route {route_idx_v18}, Module present: {email_in_route_v18 is not None}")
            
            if email_in_route_v17 and email_in_route_v18:
                console.print("\n[bold]Comparing email module within router routes:[/bold]")
                compare_modules_detailed(email_in_route_v17, email_in_route_v18, 81)

if __name__ == "__main__":
    main()