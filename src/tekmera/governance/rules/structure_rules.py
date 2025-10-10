"""
Structure-related governance rules.
"""
from typing import Dict, List, Any
from ..models import GovernanceViolation


def check_router_default_branch(blueprint_data: Dict[str, Any], scenario_name: str) -> List[GovernanceViolation]:
    """Check 3: Router Without Default Branch (GOV-STRUC-001)"""
    violations = []
    
    def check_modules_recursive(modules: List[Dict], depth: int = 0):
        for module in modules:
            module_type = module.get('module', '').lower()
            module_id = module.get('id', 'unknown')
            
            # Get module name
            metadata = module.get('metadata', {})
            designer = metadata.get('designer', {})
            module_name = designer.get('name', f"Module {module_id}")
            
            # Check if this is a router
            if 'router' in module_type or 'routes' in module:
                routes = module.get('routes', [])
                
                # Check if any route has no filter (default branch)
                has_default = False
                for route in routes:
                    # A route without a filter is a default branch
                    if not route.get('filter') or route.get('filter') == '':
                        has_default = True
                        break
                
                if not has_default:
                    violations.append(GovernanceViolation(
                        rule_id="GOV-STRUC-001",
                        rule_title="Router Without Default Branch",
                        message=f"❌ NO DEFAULT BRANCH: Router '{module_name}' has no default/fallback branch.",
                        suggested_fix="Add a fallback route to this router.",
                        rule_description="Ensures routers have fallback branches to handle unexpected conditions. "
                                        "Routers without default branches can cause scenarios to fail when no route conditions are met, "
                                        "leading to incomplete processing and data loss. Default branches provide error handling and ensure "
                                        "graceful processing of edge cases.",
                        module_id=str(module_id),
                        module_name=module_name,
                        is_violation=True
                    ))
                
                # Recursively check routes
                for route in routes:
                    route_flow = route.get('flow', [])
                    check_modules_recursive(route_flow, depth + 1)
            
            # Check error handlers
            if 'onerror' in module:
                check_modules_recursive(module['onerror'], depth + 1)
    
    main_flow = blueprint_data.get('flow', [])
    check_modules_recursive(main_flow)
    
    return violations


def check_orphan_modules(blueprint_data: Dict[str, Any], scenario_name: str) -> List[GovernanceViolation]:
    """Check 4: Orphan Module (GOV-STRUC-002)
    
    Uses metadata.designer.orphans to identify orphan modules in the blueprint.
    """
    violations = []
    
    # Check for orphans in the blueprint metadata
    metadata = blueprint_data.get('metadata', {})
    designer = metadata.get('designer', {})
    orphans = designer.get('orphans', [])
    
    if orphans:
        # Extract module names and IDs from orphan data
        orphan_details = []
        for orphan in orphans:
            module_name = orphan.get('name', 'Unknown Module')
            module_id = orphan.get('id', 'unknown')
            orphan_details.append(f"{module_name} (ID: {module_id})")
        
        violations.append(GovernanceViolation(
            rule_id="GOV-STRUC-002",
            rule_title="Orphan Module",
            message=f"❌ ORPHAN MODULES: {len(orphans)} orphan module(s) found: {', '.join(orphan_details)}.",
            suggested_fix="Remove or reconnect these modules to the main flow.",
            rule_description="Identifies modules marked as orphans in the blueprint metadata. "
                            "Orphan modules are not connected to the main execution flow and indicate incomplete scenario design, "
                            "unused components, or broken connections. They can cause confusion during maintenance and may contain "
                            "outdated logic that could accidentally be reconnected later.",
            is_violation=True
        ))
    else:
        violations.append(GovernanceViolation(
            rule_id="GOV-STRUC-002",
            rule_title="Orphan Module",
            message="✅ NO ORPHAN MODULES: Blueprint metadata shows no orphan modules.",
            suggested_fix="Module connectivity is properly maintained.",
            rule_description="Identifies modules marked as orphans in the blueprint metadata. "
                            "Orphan modules are not connected to the main execution flow and indicate incomplete scenario design, "
                            "unused components, or broken connections. They can cause confusion during maintenance and may contain "
                            "outdated logic that could accidentally be reconnected later.",
            is_violation=False
        ))
    
    return violations


