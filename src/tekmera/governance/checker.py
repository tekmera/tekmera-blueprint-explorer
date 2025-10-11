"""
Main governance checker that orchestrates all rule checks.
"""

from typing import Any, Dict, List, Tuple

from .models import GovernanceViolation
from .rules.complexity_rules import (
    check_flow_complexity_index,
    check_flow_depth_estimate,
    check_route_fan_out_profile,
    check_router_density_analysis,
)
from .rules.connection_rules import check_dev_connection_in_prod
from .rules.field_rules import check_field_mapping_complexity
from .rules.naming_rules import check_default_module_labels, check_scenario_naming_prefix
from .rules.size_rules import check_functional_density_index
from .rules.structure_rules import check_orphan_modules, check_router_default_branch


class GovernanceChecker:
    """Checks Workfront Fusion blueprints for governance compliance."""

    def __init__(self):
        self.checks = {
            # Basic governance checks
            "1": ("Scenario Naming Prefix", check_scenario_naming_prefix),
            "2": ("Default Module Label", check_default_module_labels),
            "3": ("Router Without Default Branch", check_router_default_branch),
            "4": ("Orphan Module", check_orphan_modules),
            "5": ("Dev Connection in Prod", check_dev_connection_in_prod),
            # Advanced structural checks
            "6": ("Flow Complexity Index", check_flow_complexity_index),
            "7": ("Functional Density Index", check_functional_density_index),
            "8": ("Router Density Analysis", check_router_density_analysis),
            "9": ("Route Fan-Out Profile", check_route_fan_out_profile),
            "10": ("Flow Depth Estimate", check_flow_depth_estimate),
            "11": ("Field Mapping Complexity", check_field_mapping_complexity),
        }

    def get_available_checks(self) -> List[Tuple[str, str]]:
        """Get list of available governance checks."""
        return [(check_id, check_name) for check_id, (check_name, _) in self.checks.items()]

    def run_check(
        self, check_id: str, blueprint_data: Dict[str, Any], scenario_name: str
    ) -> List[GovernanceViolation]:
        """Run a specific governance check."""
        if check_id not in self.checks:
            raise ValueError(f"Unknown check ID: {check_id}")

        _, check_function = self.checks[check_id]
        return check_function(blueprint_data, scenario_name)
