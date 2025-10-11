"""
Naming-related governance rules.
"""

import re
from typing import Any, Dict, List

from ..models import GovernanceViolation


def check_scenario_naming_prefix(
    blueprint_data: Dict[str, Any], scenario_name: str
) -> List[GovernanceViolation]:
    """Check 1: Scenario Naming Prefix (GOV-NAME-001)"""
    valid_prefixes = ["SA_", "INT_", "UTIL_", "DEV_"]

    # Always return a result
    has_valid_prefix = any(scenario_name.startswith(prefix) for prefix in valid_prefixes)

    if has_valid_prefix:
        matched_prefix = next(
            prefix for prefix in valid_prefixes if scenario_name.startswith(prefix)
        )
        return [
            GovernanceViolation(
                rule_id="GOV-NAME-001",
                rule_title="Scenario Naming Prefix",
                message=f"✅ VALID PREFIX: Scenario name '{scenario_name}' uses valid prefix '{matched_prefix}'.",
                suggested_fix="Naming convention is properly followed.",
                rule_description="Enforces standardized scenario naming conventions using prefixes like SA_ (Scenario), INT_ (Integration), "
                "UTIL_ (Utility), or DEV_ (Development). Consistent naming helps with organization, environment identification, "
                "and team collaboration by making scenario purpose and deployment target immediately clear.",
                is_violation=False,
            )
        ]
    else:
        return [
            GovernanceViolation(
                rule_id="GOV-NAME-001",
                rule_title="Scenario Naming Prefix",
                message=f"❌ MISSING PREFIX: Scenario name '{scenario_name}' is missing required prefix.",
                suggested_fix="Rename the scenario to include a valid prefix such as 'SA_' for scenarios, 'INT_' for integrations, 'UTIL_' for utilities, or 'DEV_' for development.",
                rule_description="Enforces standardized scenario naming conventions using prefixes like SA_ (Scenario), INT_ (Integration), "
                "UTIL_ (Utility), or DEV_ (Development). Consistent naming helps with organization, environment identification, "
                "and team collaboration by making scenario purpose and deployment target immediately clear.",
                is_violation=True,
            )
        ]


def check_default_module_labels(
    blueprint_data: Dict[str, Any], scenario_name: str
) -> List[GovernanceViolation]:
    """Check 2: Default Module Label (GOV-NAME-002)"""
    violations = []
    total_modules = 0
    modules_with_default_labels = []

    # Common default module label patterns
    default_patterns = [
        r"HTTP > Make a request",
        r"Workfront > Create Record",
        r"Workfront > Search",
        r"Workfront > Update Record",
        r"Workfront > Read a Record",
        r"Tools > Set variable",
        r"Tools > Get variable",
        r"Router",
        r"Email > Send an Email",
        r"Slack > Create a Message",
        r"Google Sheets > Add a Row",
        r"JSON > Parse JSON",
        r"Text parser > Match pattern",
    ]

    def check_modules_recursive(modules: List[Dict], depth: int = 0):
        nonlocal total_modules

        for module in modules:
            total_modules += 1

            # Get module name from metadata
            metadata = module.get("metadata", {})
            designer = metadata.get("designer", {})
            module_name = designer.get("name", "")
            module_id = module.get("id", "unknown")

            # Check if name matches default patterns
            if module_name:
                for pattern in default_patterns:
                    if re.match(pattern, module_name, re.IGNORECASE):
                        modules_with_default_labels.append(module_name)
                        violations.append(
                            GovernanceViolation(
                                rule_id="GOV-NAME-002",
                                rule_title="Default Module Label",
                                message=f"❌ DEFAULT LABEL: Module '{module_name}' appears to use the default label.",
                                suggested_fix="Rename the module to describe its function clearly.",
                                rule_description="Identifies modules that still use generic default labels instead of descriptive names. "
                                "Default labels make scenarios harder to understand, debug, and maintain. Descriptive module names "
                                "improve documentation, make troubleshooting easier, and help team members understand scenario logic.",
                                module_id=str(module_id),
                                module_name=module_name,
                                is_violation=True,
                            )
                        )
                        break

            # Check router branches
            if "routes" in module:
                for route in module["routes"]:
                    route_flow = route.get("flow", [])
                    check_modules_recursive(route_flow, depth + 1)

            # Check error handlers
            if "onerror" in module:
                check_modules_recursive(module["onerror"], depth + 1)

    main_flow = blueprint_data.get("flow", [])
    check_modules_recursive(main_flow)

    # Always add a summary result
    if total_modules == 0:
        violations.insert(
            0,
            GovernanceViolation(
                rule_id="GOV-NAME-002",
                rule_title="Default Module Label",
                message="✅ NO MODULES: Scenario contains no modules to analyze.",
                suggested_fix="No action needed for empty scenario.",
                rule_description="Identifies modules that still use generic default labels instead of descriptive names. "
                "Default labels make scenarios harder to understand, debug, and maintain. Descriptive module names "
                "improve documentation, make troubleshooting easier, and help team members understand scenario logic.",
                is_violation=False,
            ),
        )
    elif not modules_with_default_labels:
        violations.insert(
            0,
            GovernanceViolation(
                rule_id="GOV-NAME-002",
                rule_title="Default Module Label",
                message=f"✅ ALL MODULES PROPERLY NAMED: {total_modules} modules analyzed, none use default labels.",
                suggested_fix="Module naming is well-maintained.",
                rule_description="Identifies modules that still use generic default labels instead of descriptive names. "
                "Default labels make scenarios harder to understand, debug, and maintain. Descriptive module names "
                "improve documentation, make troubleshooting easier, and help team members understand scenario logic.",
                is_violation=False,
            ),
        )

    return violations
