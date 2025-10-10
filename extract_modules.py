#!/usr/bin/env python3

import json
import difflib

def find_module_recursively(data, target_id):
    """Recursively find a module by ID in the blueprint structure"""
    if isinstance(data, dict):
        if data.get('id') == target_id:
            return data
        for key, value in data.items():
            result = find_module_recursively(value, target_id)
            if result:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_module_recursively(item, target_id)
            if result:
                return result
    return None

def normalize_for_diff(obj):
    """Remove UI positioning and restore data for meaningful comparison"""
    if isinstance(obj, dict):
        return {k: normalize_for_diff(v) for k, v in obj.items() 
                if k not in ['x', 'y', 'restore']}
    elif isinstance(obj, list):
        return [normalize_for_diff(item) for item in obj]
    else:
        return obj

def main():
    # Load both blueprints
    with open('blueprints/diff/blueprint-25635-v17.json', 'r') as f:
        bp_v17 = json.load(f)['blueprint']
    
    with open('blueprints/diff/blueprint-25635-v18.json', 'r') as f:
        bp_v18 = json.load(f)['blueprint']
    
    # Find modules 81 and 82 in both versions
    module_81_v17 = find_module_recursively(bp_v17, 81)
    module_81_v18 = find_module_recursively(bp_v18, 81)
    
    module_82_v17 = find_module_recursively(bp_v17, 82)
    module_82_v18 = find_module_recursively(bp_v18, 82)
    
    print("DETAILED COMPARISON OF MODULES 81 AND 82")
    print("=" * 60)
    
    # Compare Module 81 (microsoft-email:createAndSendAMessage)
    print("\nMODULE 81 COMPARISON (microsoft-email:createAndSendAMessage)")
    print("-" * 60)
    
    if module_81_v17 and module_81_v18:
        # Normalize and compare
        norm_81_v17 = normalize_for_diff(module_81_v17)
        norm_81_v18 = normalize_for_diff(module_81_v18)
        
        if norm_81_v17 != norm_81_v18:
            # Show JSON diff
            json_v17 = json.dumps(norm_81_v17, indent=2, sort_keys=True)
            json_v18 = json.dumps(norm_81_v18, indent=2, sort_keys=True)
            
            diff = list(difflib.unified_diff(
                json_v17.splitlines(),
                json_v18.splitlines(),
                fromfile='v17 (Module 81)',
                tofile='v18 (Module 81)',
                lineterm='',
                n=3
            ))
            
            print("JSON DIFF:")
            for line in diff:
                print(line)
                
            # Show key differences
            print("\nKEY DIFFERENCES:")
            for key in set(norm_81_v17.keys()) | set(norm_81_v18.keys()):
                val_v17 = norm_81_v17.get(key)
                val_v18 = norm_81_v18.get(key)
                if val_v17 != val_v18:
                    print(f"  {key}:")
                    print(f"    v17: {json.dumps(val_v17)[:100]}...")
                    print(f"    v18: {json.dumps(val_v18)[:100]}...")
        else:
            print("No functional differences found in Module 81")
    
    # Compare Module 82 (Router)
    print("\n\nMODULE 82 COMPARISON (Router)")
    print("-" * 60)
    
    if module_82_v17 and module_82_v18:
        # Normalize and compare
        norm_82_v17 = normalize_for_diff(module_82_v17)
        norm_82_v18 = normalize_for_diff(module_82_v18)
        
        if norm_82_v17 != norm_82_v18:
            # Focus on routes comparison
            routes_v17 = norm_82_v17.get('routes', [])
            routes_v18 = norm_82_v18.get('routes', [])
            
            print(f"Route count - v17: {len(routes_v17)}, v18: {len(routes_v18)}")
            
            # Compare each route
            for i, (route_v17, route_v18) in enumerate(zip(routes_v17, routes_v18)):
                if route_v17 != route_v18:
                    print(f"\nROUTE {i} DIFFERS:")
                    
                    # Check if module 81 is in this route
                    flow_v17 = route_v17.get('flow', [])
                    flow_v18 = route_v18.get('flow', [])
                    
                    ids_v17 = [m.get('id') for m in flow_v17 if isinstance(m, dict)]
                    ids_v18 = [m.get('id') for m in flow_v18 if isinstance(m, dict)]
                    
                    if 81 in ids_v17 or 81 in ids_v18:
                        print(f"  Contains Module 81")
                        print(f"  Flow IDs v17: {ids_v17}")
                        print(f"  Flow IDs v18: {ids_v18}")
                        
                        # Find and compare module 81 within this route
                        mod_81_route_v17 = next((m for m in flow_v17 if m.get('id') == 81), None)
                        mod_81_route_v18 = next((m for m in flow_v18 if m.get('id') == 81), None)
                        
                        if mod_81_route_v17 and mod_81_route_v18:
                            if mod_81_route_v17 != mod_81_route_v18:
                                print("  MODULE 81 WITHIN ROUTE DIFFERS:")
                                
                                # Show specific differences
                                for key in set(mod_81_route_v17.keys()) | set(mod_81_route_v18.keys()):
                                    val_v17 = mod_81_route_v17.get(key)
                                    val_v18 = mod_81_route_v18.get(key)
                                    if val_v17 != val_v18:
                                        print(f"    {key}:")
                                        if len(str(val_v17)) < 200 and len(str(val_v18)) < 200:
                                            print(f"      v17: {val_v17}")
                                            print(f"      v18: {val_v18}")
                                        else:
                                            print(f"      v17: {json.dumps(val_v17)[:100]}...")
                                            print(f"      v18: {json.dumps(val_v18)[:100]}...")
        else:
            print("No functional differences found in Module 82")

if __name__ == "__main__":
    main()