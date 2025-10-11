"""
Size-related governance rules for analyzing scenario scale and density.
"""

from typing import Any, Dict, List, Set

from ..models import GovernanceViolation


def check_functional_density_index(
    blueprint_data: Dict[str, Any], scenario_name: str
) -> List[GovernanceViolation]:
    """Check GOV-SIZE-001: Functional Density Index

    Algorithm: Modules per logical cluster analysis
    - Group modules by functional areas (HTTP, Workfront, Tools, etc.)
    - Calculate cluster density: total modules / functional clusters
    - Flag scenarios with density > 8 modules per cluster
    """
    violations = []

    functional_clusters = set()
    total_modules = 0

    def analyze_modules_recursive(modules: List[Dict]):
        nonlocal total_modules

        for module in modules:
            total_modules += 1
            module_type = module.get("module", "").lower()

            # Categorize modules into functional clusters
            if "http" in module_type or "webhook" in module_type:
                functional_clusters.add("HTTP/API")
            elif "workfront" in module_type:
                functional_clusters.add("Workfront")
            elif "email" in module_type or "mail" in module_type:
                functional_clusters.add("Email")
            elif "slack" in module_type or "teams" in module_type:
                functional_clusters.add("Communication")
            elif "google" in module_type or "drive" in module_type or "sheets" in module_type:
                functional_clusters.add("Google Services")
            elif (
                "microsoft" in module_type or "excel" in module_type or "sharepoint" in module_type
            ):
                functional_clusters.add("Microsoft Services")
            elif "salesforce" in module_type:
                functional_clusters.add("Salesforce")
            elif "database" in module_type or "sql" in module_type or "mysql" in module_type:
                functional_clusters.add("Database")
            elif "json" in module_type or "xml" in module_type or "csv" in module_type:
                functional_clusters.add("Data Processing")
            elif "text" in module_type or "parser" in module_type:
                functional_clusters.add("Text Processing")
            elif "tool" in module_type or "variable" in module_type or "iterator" in module_type:
                functional_clusters.add("Tools/Utilities")
            elif "router" in module_type:
                functional_clusters.add("Control Flow")
            elif "error" in module_type or "break" in module_type:
                functional_clusters.add("Error Handling")
            else:
                # Generic/unknown modules
                functional_clusters.add("Other")

            # Recursively analyze router branches
            if "routes" in module:
                for route in module["routes"]:
                    route_flow = route.get("flow", [])
                    analyze_modules_recursive(route_flow)

            # Check error handlers
            if "onerror" in module:
                analyze_modules_recursive(module["onerror"])

    main_flow = blueprint_data.get("flow", [])
    analyze_modules_recursive(main_flow)

    if len(functional_clusters) == 0:
        violations.append(
            GovernanceViolation(
                rule_id="GOV-SIZE-001",
                rule_title="Functional Density Index",
                message="✅ NO MODULES: Scenario contains no modules to analyze.",
                suggested_fix="No action needed for empty scenario.",
                rule_description="Analyzes how modules are distributed across functional areas (HTTP/API, Workfront, Tools, etc.) "
                "by calculating modules per functional cluster. High density indicates scenarios that try to do too much "
                "and would benefit from being split into smaller, more focused scenarios. Well-balanced scenarios "
                "have clear functional separation and manageable scope within each area.",
                is_violation=False,
            )
        )
        return violations

    density_index = total_modules / len(functional_clusters)
    cluster_list = ", ".join(sorted(functional_clusters))

    # Always return the result
    is_violation = density_index > 8
    status = "❌ EXCEEDS THRESHOLD" if is_violation else "✅ WITHIN LIMITS"

    violations.append(
        GovernanceViolation(
            rule_id="GOV-SIZE-001",
            rule_title="Functional Density Index",
            message=f"{status}: Functional density is {density_index:.1f} modules per cluster (threshold: 8). "
            f"Analysis: {total_modules} modules across {len(functional_clusters)} functional areas: {cluster_list}.",
            suggested_fix=(
                "Consider breaking this scenario into smaller, more focused scenarios grouped by functional area."
                if is_violation
                else "Functional distribution is well-balanced."
            ),
            rule_description="Analyzes how modules are distributed across functional areas (HTTP/API, Workfront, Tools, etc.) "
            "by calculating modules per functional cluster. High density indicates scenarios that try to do too much "
            "and would benefit from being split into smaller, more focused scenarios. Well-balanced scenarios "
            "have clear functional separation and manageable scope within each area.",
            is_violation=is_violation,
        )
    )

    return violations
