"""
Field mapping and data transformation governance rules.
"""
import re
from typing import Dict, List, Any
from ..models import GovernanceViolation


def check_field_mapping_complexity(blueprint_data: Dict[str, Any], scenario_name: str) -> List[GovernanceViolation]:
    """Check GOV-FIELD-003: Field Mapping Complexity
    
    Algorithm: Analyze deep field references with dot notation
    - Scan all module parameters for field mappings
    - Count nesting levels (dots) in field references
    - Flag scenarios with >50% fields having 3+ levels of nesting
    """
    violations = []
    
    total_field_mappings = 0
    deep_field_mappings = 0
    complex_modules = []
    
    def analyze_field_mappings(data, module_name="", module_id=""):
        nonlocal total_field_mappings, deep_field_mappings
        
        if isinstance(data, dict):
            for key, value in data.items():
                analyze_field_mappings(value, module_name, module_id)
        elif isinstance(data, list):
            for item in data:
                analyze_field_mappings(item, module_name, module_id)
        elif isinstance(data, str):
            # Look for field mapping patterns
            # Pattern 1: {{X.field.subfield.value}} - Fusion variable syntax
            fusion_patterns = re.findall(r'\{\{[^}]*\}\}', data)
            for pattern in fusion_patterns:
                # Count dots to determine nesting level
                dot_count = pattern.count('.')
                if dot_count > 0:  # This is a field mapping
                    total_field_mappings += 1
                    if dot_count >= 3:  # 3+ levels of nesting
                        deep_field_mappings += 1
                        if module_name and module_name not in [m['name'] for m in complex_modules]:
                            complex_modules.append({
                                'name': module_name,
                                'id': module_id,
                                'example': pattern[:50] + "..." if len(pattern) > 50 else pattern
                            })
            
            # Pattern 2: JSON path expressions like $.data.items[0].attributes.value
            json_path_patterns = re.findall(r'\$\.[a-zA-Z0-9_\[\]\.]+', data)
            for pattern in json_path_patterns:
                dot_count = pattern.count('.')
                if dot_count > 0:
                    total_field_mappings += 1
                    if dot_count >= 3:
                        deep_field_mappings += 1
                        if module_name and module_name not in [m['name'] for m in complex_modules]:
                            complex_modules.append({
                                'name': module_name,
                                'id': module_id,
                                'example': pattern
                            })
    
    def check_modules_recursive(modules: List[Dict]):
        for module in modules:
            module_id = module.get('id', 'unknown')
            
            # Get module name
            metadata = module.get('metadata', {})
            designer = metadata.get('designer', {})
            module_name = designer.get('name', f"Module {module_id}")
            
            # Analyze all parameters for field mappings
            parameters = module.get('parameters', {})
            analyze_field_mappings(parameters, module_name, str(module_id))
            
            # Check router branches
            if 'routes' in module:
                for route in module['routes']:
                    route_flow = route.get('flow', [])
                    check_modules_recursive(route_flow)
            
            # Check error handlers
            if 'onerror' in module:
                check_modules_recursive(module['onerror'])
    
    main_flow = blueprint_data.get('flow', [])
    check_modules_recursive(main_flow)
    
    if total_field_mappings == 0:
        violations.append(GovernanceViolation(
            rule_id="GOV-FIELD-003",
            rule_title="Field Mapping Complexity",
            message="✅ NO FIELD MAPPINGS: Scenario contains no field mappings to analyze.",
            suggested_fix="No action needed for scenarios without field mappings.",
            rule_description="Analyzes field mapping complexity by examining dot notation depth in variable references "
                            "(e.g., {{item.data.attributes.values[0].name}}). Deep field mappings with 3+ nesting levels "
                            "can be difficult to debug, prone to null reference errors, and hard to maintain when data "
                            "structures change. Complex mappings often benefit from intermediate variables or data flattening.",
            is_violation=False
        ))
        return violations
    
    complexity_percentage = (deep_field_mappings / total_field_mappings) * 100
    
    # Always return the result
    is_violation = complexity_percentage > 50
    status = "❌ EXCEEDS THRESHOLD" if is_violation else "✅ WITHIN LIMITS"
    
    if is_violation:
        module_examples = []
        for module_info in complex_modules[:3]:  # Show up to 3 examples
            module_examples.append(f"{module_info['name']} (e.g., {module_info['example']})")
        
        if len(complex_modules) > 3:
            module_examples.append(f"... and {len(complex_modules) - 3} more modules")
        
        complex_detail = f" Complex modules: {'; '.join(module_examples)}."
    else:
        complex_detail = ""
    
    violations.append(GovernanceViolation(
        rule_id="GOV-FIELD-003",
        rule_title="Field Mapping Complexity",
        message=f"{status}: Field mapping complexity is {complexity_percentage:.1f}% ({deep_field_mappings}/{total_field_mappings} mappings use 3+ nesting levels, threshold: 50%).{complex_detail}",
        suggested_fix="Consider flattening data structures, using intermediate variables, or breaking complex mappings into smaller steps." if is_violation else "Field mapping complexity is reasonable.",
        rule_description="Analyzes field mapping complexity by examining dot notation depth in variable references "
                        "(e.g., {{item.data.attributes.values[0].name}}). Deep field mappings with 3+ nesting levels "
                        "can be difficult to debug, prone to null reference errors, and hard to maintain when data "
                        "structures change. Complex mappings often benefit from intermediate variables or data flattening.",
        is_violation=is_violation
    ))
    
    return violations