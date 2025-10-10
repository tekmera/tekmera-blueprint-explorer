"""
Complexity-related governance rules for advanced structural analysis.
"""
from typing import Dict, List, Any
from ..models import GovernanceViolation


def check_flow_complexity_index(blueprint_data: Dict[str, Any], scenario_name: str) -> List[GovernanceViolation]:
    """Check GOV-COMP-001: Flow Complexity Index
    
    Algorithm: (Router count × Average branches per router) + Maximum nesting depth
    Threshold: Flag scenarios with complexity index > 15
    """
    violations = []
    
    router_count = 0
    total_branches = 0
    max_nesting = 0
    
    def analyze_modules_recursive(modules: List[Dict], depth: int = 0):
        nonlocal router_count, total_branches, max_nesting
        
        max_nesting = max(max_nesting, depth)
        
        for module in modules:
            module_type = module.get('module', '').lower()
            
            # Check if this is a router
            if 'router' in module_type or 'routes' in module:
                router_count += 1
                routes = module.get('routes', [])
                total_branches += len(routes)
                
                # Recursively analyze routes
                for route in routes:
                    route_flow = route.get('flow', [])
                    analyze_modules_recursive(route_flow, depth + 1)
            
            # Check error handlers
            if 'onerror' in module:
                analyze_modules_recursive(module['onerror'], depth + 1)
    
    main_flow = blueprint_data.get('flow', [])
    analyze_modules_recursive(main_flow)
    
    # Calculate complexity index
    avg_branches = total_branches / router_count if router_count > 0 else 0
    complexity_index = (router_count * avg_branches) + max_nesting
    
    # Always return the result (violation or informational)
    is_violation = complexity_index > 15
    status = "❌ EXCEEDS THRESHOLD" if is_violation else "✅ WITHIN LIMITS"
    
    violations.append(GovernanceViolation(
        rule_id="GOV-COMP-001",
        rule_title="Flow Complexity Index",
        message=f"{status}: Complexity index is {complexity_index:.1f} (threshold: 15). "
               f"Analysis: {router_count} routers, avg {avg_branches:.1f} branches/router, max nesting depth {max_nesting}.",
        suggested_fix="Consider breaking this scenario into smaller, more focused scenarios or reducing nesting levels." if is_violation else "Scenario complexity is well-managed.",
        rule_description="Calculates scenario complexity using the formula: (Router count × Average branches per router) + Maximum nesting depth. "
                        "This metric identifies scenarios that may be difficult to maintain, debug, or understand due to high decision complexity and deep nesting. "
                        "Complex scenarios are prone to execution errors and harder to troubleshoot when issues arise.",
        is_violation=is_violation
    ))
    
    return violations


def check_router_density_analysis(blueprint_data: Dict[str, Any], scenario_name: str) -> List[GovernanceViolation]:
    """Check GOV-COMP-002: Router Density Analysis
    
    Algorithm: (Router count / Total module count) × 100%
    Threshold: Flag scenarios where >40% of modules are routers
    """
    violations = []
    
    router_count = 0
    total_modules = 0
    
    def count_modules_recursive(modules: List[Dict]):
        nonlocal router_count, total_modules
        
        for module in modules:
            total_modules += 1
            module_type = module.get('module', '').lower()
            
            # Check if this is a router
            if 'router' in module_type or 'routes' in module:
                router_count += 1
                
                # Recursively count routes
                routes = module.get('routes', [])
                for route in routes:
                    route_flow = route.get('flow', [])
                    count_modules_recursive(route_flow)
            
            # Check error handlers
            if 'onerror' in module:
                count_modules_recursive(module['onerror'])
    
    main_flow = blueprint_data.get('flow', [])
    count_modules_recursive(main_flow)
    
    if total_modules == 0:
        violations.append(GovernanceViolation(
            rule_id="GOV-COMP-002",
            rule_title="Router Density Analysis",
            message="✅ NO MODULES: Scenario contains no modules to analyze.",
            suggested_fix="No action needed for empty scenario.",
            rule_description="Measures the percentage of modules that are routers (decision points) in the scenario. "
                            "High router density indicates excessive branching logic, which can make scenarios harder to follow, "
                            "more prone to logical errors, and difficult to maintain. Scenarios with too many decision points "
                            "often benefit from consolidation or restructuring into more linear flows.",
            is_violation=False
        ))
        return violations
    
    router_percentage = (router_count / total_modules) * 100
    
    # Always return the result
    is_violation = router_percentage > 40
    status = "❌ EXCEEDS THRESHOLD" if is_violation else "✅ WITHIN LIMITS"
    
    violations.append(GovernanceViolation(
        rule_id="GOV-COMP-002",
        rule_title="Router Density Analysis",
        message=f"{status}: Router density is {router_percentage:.1f}% ({router_count}/{total_modules} modules, threshold: 40%).",
        suggested_fix="Consider consolidating router logic or restructuring the flow to reduce decision complexity." if is_violation else "Router distribution is appropriate.",
        rule_description="Measures the percentage of modules that are routers (decision points) in the scenario. "
                        "High router density indicates excessive branching logic, which can make scenarios harder to follow, "
                        "more prone to logical errors, and difficult to maintain. Scenarios with too many decision points "
                        "often benefit from consolidation or restructuring into more linear flows.",
        is_violation=is_violation
    ))
    
    return violations


def check_route_fan_out_profile(blueprint_data: Dict[str, Any], scenario_name: str) -> List[GovernanceViolation]:
    """Check GOV-COMP-003: Route Fan-Out Profile
    
    Algorithm: Identify routers with >5 branches
    Threshold: Flag any router with more than 5 branches
    """
    violations = []
    router_details = []
    high_fan_out_routers = []
    
    def check_modules_recursive(modules: List[Dict]):
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
                branch_count = len(routes)
                
                router_details.append(f"{module_name} ({branch_count} branches)")
                
                if branch_count > 5:
                    high_fan_out_routers.append(module_name)
                    violations.append(GovernanceViolation(
                        rule_id="GOV-COMP-003",
                        rule_title="Route Fan-Out Profile",
                        message=f"❌ HIGH FAN-OUT: Router '{module_name}' has {branch_count} branches (threshold: 5).",
                        suggested_fix="Consider breaking this router into multiple routers or using a lookup table approach.",
                        rule_description="Identifies individual routers with excessive branching (fan-out). "
                                        "Routers with many branches become difficult to understand, maintain, and debug. "
                                        "High fan-out routers often indicate complex business logic that could be simplified "
                                        "through hierarchical routing, lookup tables, or breaking into multiple decision points.",
                        module_id=str(module_id),
                        module_name=module_name,
                        is_violation=True
                    ))
                
                # Recursively check routes
                for route in routes:
                    route_flow = route.get('flow', [])
                    check_modules_recursive(route_flow)
            
            # Check error handlers
            if 'onerror' in module:
                check_modules_recursive(module['onerror'])
    
    main_flow = blueprint_data.get('flow', [])
    check_modules_recursive(main_flow)
    
    # Always provide a summary result
    if not router_details:
        violations.append(GovernanceViolation(
            rule_id="GOV-COMP-003",
            rule_title="Route Fan-Out Profile",
            message="✅ NO ROUTERS: Scenario contains no routers to analyze.",
            suggested_fix="No action needed for scenarios without routers.",
            rule_description="Identifies individual routers with excessive branching (fan-out). "
                            "Routers with many branches become difficult to understand, maintain, and debug. "
                            "High fan-out routers often indicate complex business logic that could be simplified "
                            "through hierarchical routing, lookup tables, or breaking into multiple decision points.",
            is_violation=False
        ))
    elif not high_fan_out_routers:
        summary = f"✅ ALL ROUTERS WITHIN LIMITS: {len(router_details)} router(s) found - {', '.join(router_details[:3])}"
        if len(router_details) > 3:
            summary += f" and {len(router_details) - 3} more"
        
        violations.append(GovernanceViolation(
            rule_id="GOV-COMP-003",
            rule_title="Route Fan-Out Profile",
            message=f"{summary}. All routers have ≤5 branches.",
            suggested_fix="Router fan-out is well-managed.",
            rule_description="Identifies individual routers with excessive branching (fan-out). "
                            "Routers with many branches become difficult to understand, maintain, and debug. "
                            "High fan-out routers often indicate complex business logic that could be simplified "
                            "through hierarchical routing, lookup tables, or breaking into multiple decision points.",
            is_violation=False
        ))
    
    return violations


def check_flow_depth_estimate(blueprint_data: Dict[str, Any], scenario_name: str) -> List[GovernanceViolation]:
    """Check GOV-COMP-004: Flow Depth Estimate
    
    Algorithm: Calculate the longest linear execution path through the scenario
    Threshold: Flag scenarios with execution depth > 20 modules
    """
    violations = []
    
    def calculate_max_depth(modules: List[Dict]) -> int:
        if not modules:
            return 0
        
        max_depth = 0
        
        for module in modules:
            current_depth = 1  # Count this module
            
            # Check if this is a router
            if 'routes' in module:
                route_depths = []
                for route in module['routes']:
                    route_flow = route.get('flow', [])
                    route_depth = calculate_max_depth(route_flow)
                    route_depths.append(route_depth)
                
                # Add the maximum route depth
                if route_depths:
                    current_depth += max(route_depths)
            
            # Check error handlers (they add to depth but are alternative paths)
            if 'onerror' in module:
                error_depth = calculate_max_depth(module['onerror'])
                # Error handlers are alternative paths, so we take max of main vs error
                current_depth = max(current_depth, 1 + error_depth)
            
            max_depth = max(max_depth, current_depth)
        
        # For sequential modules, add their depths
        if len(modules) > 1:
            remaining_depth = calculate_max_depth(modules[1:])
            max_depth = max(max_depth, 1 + remaining_depth)
        
        return max_depth
    
    main_flow = blueprint_data.get('flow', [])
    max_execution_depth = calculate_max_depth(main_flow)
    
    # Always return the result
    is_violation = max_execution_depth > 20
    status = "❌ EXCEEDS THRESHOLD" if is_violation else "✅ WITHIN LIMITS"
    
    violations.append(GovernanceViolation(
        rule_id="GOV-COMP-004",
        rule_title="Flow Depth Estimate",
        message=f"{status}: Maximum execution depth is {max_execution_depth} modules (threshold: 20).",
        suggested_fix="Consider breaking the scenario into smaller sub-scenarios or using parallel processing where appropriate." if is_violation else "Flow depth is manageable.",
        rule_description="Calculates the longest possible execution path through the scenario by analyzing sequential modules, "
                        "router branches, and error handlers. Deep execution paths can indicate overly complex scenarios that "
                        "are difficult to debug, slow to execute, and prone to timeout issues. Long linear flows often benefit "
                        "from being broken into smaller, more focused sub-scenarios.",
        is_violation=is_violation
    ))
    
    return violations