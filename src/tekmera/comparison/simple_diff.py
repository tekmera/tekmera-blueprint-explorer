#!/usr/bin/env python3

import json
import sys
from pathlib import Path
import difflib

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

def normalize_for_comparison(obj):
    """Normalize object for comparison by removing UI-related fields"""
    if isinstance(obj, dict):
        normalized = {}
        skip_keys = {'x', 'y', 'restore'}
        for key, value in obj.items():
            if key not in skip_keys:
                normalized[key] = normalize_for_comparison(value)
        return normalized
    elif isinstance(obj, list):
        return [normalize_for_comparison(item) for item in obj]
    else:
        return obj

def print_json_diff(obj1, obj2, title):
    """Print a JSON diff between two objects"""
    json1 = json.dumps(normalize_for_comparison(obj1), indent=2, sort_keys=True)
    json2 = json.dumps(normalize_for_comparison(obj2), indent=2, sort_keys=True)
    
    diff = list(difflib.unified_diff(
        json1.splitlines(),
        json2.splitlines(),
        fromfile='v17',
        tofile='v18',
        lineterm=''
    ))
    
    if diff:
        print(f"\n{title}:")
        print("=" * len(title))
        for line in diff:
            print(line)
    else:
        print(f"\n{title}: No functional differences found")

def compare_specific_fields(module1, module2, module_id):
    """Compare specific fields between modules"""
    print(f"\nField-by-field comparison for Module ID {module_id}:")
    print("-" * 50)
    
    # Get all unique keys from both modules
    all_keys = set()
    if module1:
        all_keys.update(module1.keys())
    if module2:
        all_keys.update(module2.keys())
    
    # Remove UI-related keys
    skip_keys = {'x', 'y', 'restore'}
    functional_keys = all_keys - skip_keys
    
    for key in sorted(functional_keys):
        val1 = normalize_for_comparison(module1.get(key)) if module1 else None
        val2 = normalize_for_comparison(module2.get(key)) if module2 else None
        
        if val1 != val2:
            print(f"\nField '{key}' differs:")
            print(f"  v17: {json.dumps(val1, indent=4)[:200]}...")
            print(f"  v18: {json.dumps(val2, indent=4)[:200]}...")

def main():
    v17_path = Path("blueprints/diff/blueprint-25635-v17.json")
    v18_path = Path("blueprints/diff/blueprint-25635-v18.json")
    
    if not v17_path.exists() or not v18_path.exists():
        print("Blueprint files not found!")
        return
    
    # Load blueprints
    bp_v17 = load_blueprint(v17_path)
    bp_v18 = load_blueprint(v18_path)
    
    print("DETAILED DIFF ANALYSIS")
    print("=" * 50)
    
    # Find the router (ID: 82) and the email module (ID: 81)
    router_v17 = find_module_by_id(bp_v17['flow'], 82)
    router_v18 = find_module_by_id(bp_v18['flow'], 82)
    
    email_module_v17 = find_module_by_id(bp_v17['flow'], 81)
    email_module_v18 = find_module_by_id(bp_v18['flow'], 81)
    
    # 1. Compare the email module directly
    print("\n1. DIRECT EMAIL MODULE COMPARISON (ID: 81)")
    if email_module_v17 and email_module_v18:
        print_json_diff(email_module_v17, email_module_v18, "Email Module Diff")
        compare_specific_fields(email_module_v17, email_module_v18, 81)
    else:
        print("Email module not found in one or both versions")
    
    # 2. Compare the router module
    print("\n\n2. ROUTER MODULE COMPARISON (ID: 82)")
    if router_v17 and router_v18:
        print_json_diff(router_v17, router_v18, "Router Module Diff")
        compare_specific_fields(router_v17, router_v18, 82)
    else:
        print("Router module not found in one or both versions")
    
    # 3. Look for the email module within router routes
    print("\n\n3. EMAIL MODULE WITHIN ROUTER ROUTES")
    if router_v17 and router_v18:
        routes_v17 = get_router_routes(router_v17)
        routes_v18 = get_router_routes(router_v18)
        
        route_idx_v17, email_in_route_v17 = find_module_in_routes(routes_v17, 81)
        route_idx_v18, email_in_route_v18 = find_module_in_routes(routes_v18, 81)
        
        print(f"Email module in routes:")
        print(f"  v17: Route {route_idx_v17}")
        print(f"  v18: Route {route_idx_v18}")
        
        if email_in_route_v17 and email_in_route_v18:
            print_json_diff(email_in_route_v17, email_in_route_v18, "Email Module in Router Routes")
            compare_specific_fields(email_in_route_v17, email_in_route_v18, 81)

if __name__ == "__main__":
    main()