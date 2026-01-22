"""Text and JSON renderers for summary reports.

This module separates the presentation logic from the data structures,
following the single responsibility principle.
"""

from typing import Any, Dict, List

from .summary import BlueprintSummaryReport


class SummaryReportTextRenderer:
    """Renders summary reports to formatted text."""

    def __init__(self, report: BlueprintSummaryReport):
        self.report = report

    def render(self) -> str:
        """Generate formatted text summary report."""
        report_lines = [
            "=" * 60,
            "BLUEPRINT SUMMARY REPORT",
            "=" * 60,
            "",
            f"Blueprint Name: {self.report.blueprint_name}",
            f"Platform: {self.report._format_platform()}",
            f"Generated: {self.report.metadata.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "COMPONENT ANALYSIS",
            "-" * 30,
            f"Total Components: {self.report.total_components}",
            "",
            "Breakdown by Type:",
            f"  • Modules:        {self.report.component_counts.get('modules', 0):4d}",
            f"  • Routers:        {self.report.component_counts.get('routers', 0):4d}",
            f"  • Filters:        {self.report.component_counts.get('filters', 0):4d}",
            f"  • Error Handlers: {self.report.component_counts.get('error_handlers', 0):4d}",
            "",
            "SUMMARY",
            "-" * 30,
        ]

        # Add insights
        for insight in self.report.insights:
            report_lines.append(f"• {insight}")

        # Add trigger analysis section
        report_lines.extend(self._render_trigger_analysis())

        # Add advanced analysis sections
        report_lines.extend(self._render_advanced_analysis())

        report_lines.extend(["", "=" * 60, "End of Report", "=" * 60])

        return "\n".join(report_lines)

    def _render_trigger_analysis(self) -> List[str]:
        """Render trigger analysis section."""
        lines = [
            "",
            "",
            "TRIGGER ANALYSIS",
            "-" * 30,
        ]

        if self.report.trigger:
            lines.extend(
                [
                    f"Trigger Type: {self.report.trigger.module_type}",
                    f"Execution Pattern: {self.report.trigger.execution_pattern.value.replace('_', ' ').title()}",
                    f"Data Source: {self.report.trigger.data_source.value.replace('_', ' ').title()}",
                    f"Reliability: {self.report.trigger.reliability.value.replace('_', ' ').title()}",
                    f"Scaling: {self.report.trigger.scaling.value.replace('_', ' ').title()}",
                ]
            )

            if self.report.trigger.display_name:
                lines.append(f"Display Name: {self.report.trigger.display_name}")

            # Connection details
            if self.report.trigger.connection.requires_auth:
                conn_type = self.report.trigger.connection.connection_type or "Unknown"
                lines.append(f"Connection Type: {conn_type.replace('_', ' ').title()}")

                if self.report.trigger.connection.connection_id:
                    lines.append(f"Connection ID: {self.report.trigger.connection.connection_id}")

                if self.report.trigger.connection.account_reference:
                    lines.append(
                        f"Account Reference: {self.report.trigger.connection.account_reference}"
                    )
            else:
                lines.append("Connection Type: No authentication required")

            # Configuration details
            if self.report.trigger.configuration.batch_size:
                lines.append(f"Batch Size: {self.report.trigger.configuration.batch_size}")

            if self.report.trigger.configuration.filter_conditions:
                filter_count = len(self.report.trigger.configuration.filter_conditions)
                lines.append(f"Filter Conditions: {filter_count} configured")
        else:
            lines.append("No trigger information available")

        return lines

    def _render_advanced_analysis(self) -> List[str]:
        """Render advanced analysis sections."""
        separator = '\n + '
        return [
            "",
            "",
            "1. CONNECTIONS",
            "-" * 30,
            f"Total # of connections: {self.report.built_in_connections.total_connections}",
            f"List of connections:\n {'+ ' + separator.join(component.connection_label for component in self.report.built_in_connections.connection_types) or 'None identified'}",
            "Purpose: gives reviewers a list of current connections.",
            "",
            "2. ROUTING AND LOGIC PATTERNS",
            "-" * 30,
            "🔴 STUB: Requires real data analysis",
            f"Router branching counts: {len(self.report.routing_patterns.router_branching_counts)} routers analyzed",
            f"Filters per branch: {len(self.report.routing_patterns.filters_per_branch)} branches with filters",
            f"Catch-all routes present: {self.report.routing_patterns.has_catch_all_routes}",
            f"Unconditional routes present: {self.report.routing_patterns.has_unconditional_routes}",
            "Purpose: highlights complexity concentration and decision-surface width.",
            "",
            "3. EXTERNAL DEPENDENCY TABLE",
            "-" * 30,
            f"API modules + endpoints: {len(self.report.external_dependencies.api_modules_and_endpoints)} identified",
            f"Workfront object types touched: {', '.join(self.report.external_dependencies.workfront_object_types) or 'None identified'}",
            f"Authentication types: {', '.join(self.report.external_dependencies.authentication_types) or 'None identified'}",
            f"Reuse vs one-off integrations: {len(self.report.external_dependencies.reuse_vs_oneoff_integrations)} mappings",
            "Purpose: shows 'what the automation touches' in one place.",
            "",
            "4. DATA SURFACE SUMMARY",
            "-" * 30,
            f"Primary input types: {', '.join(self.report.data_surface.primary_input_types) or 'None identified'}",
            f"Major mapped fields: {len(self.report.data_surface.major_mapped_fields)} fields",
            f"Iterated collections: {', '.join(self.report.data_surface.iterated_collections) or 'None identified'}",
            "Purpose: identifies the data the scenario expects, transforms, and passes downstream.",
            "",
            "5. RISK INDICATORS",
            "-" * 30,
            "🔴 STUB: Requires real data analysis",
            f"Deeply nested routers: {len(self.report.risk_indicators.deeply_nested_routers)} identified",
            f"Error handlers that mask failures: {len(self.report.risk_indicators.error_handlers_masking_failures)} identified",
            f"Modules with high fan-out: {len(self.report.risk_indicators.high_fanout_modules)} identified",
            f"Modules with high fan-in: {len(self.report.risk_indicators.high_fanin_modules)} identified",
            "Purpose: exposes brittle and high-impact regions.",
            "",
            "6. SAFE-TO-MODIFY HEURISTICS",
            "-" * 30,
            "🔴 STUB: Requires real data analysis",
            f"Isolated modules or branches: {len(self.report.safe_to_modify.isolated_modules_or_branches)} identified",
            f"Modules with no upstream dependencies: {len(self.report.safe_to_modify.modules_no_upstream_deps)} identified",
            f"Branches not feeding critical paths: {len(self.report.safe_to_modify.branches_not_feeding_critical_paths)} identified",
            "Purpose: supports estimation and quoting.",
            "",
            "7. OPERATIONAL LOAD SIGNALS",
            "-" * 30,
            "🔴 STUB: Requires real data analysis",
            f"Iterators on large collections: {len(self.report.operational_load.iterators_on_large_collections)} identified",
            f"Aggregators: {len(self.report.operational_load.aggregators)} identified",
            f"Loops with unclear exit conditions: {len(self.report.operational_load.loops_with_unclear_exit_conditions)} identified",
            "Purpose: flags performance and cost implications.",
            "",
            "8. EXECUTION ROLE SUMMARY",
            "-" * 30,
            f"Scenario vs module level error handlers: {self.report.execution_role.scenario_vs_module_error_handlers}",
            f"Schedulers vs webhooks: {self.report.execution_role.schedulers_vs_webhooks}",
            "Purpose: reveals how the scenario is supposed to run and fail.",
            "",
            "9. CHANGE SURFACE INDEX",
            "-" * 30,
            "🔴 STUB: Requires real data analysis",
            f"Routing depth score: {self.report.change_surface_index.routing_depth_score:.2f}",
            f"Dependency spread score: {self.report.change_surface_index.dependency_spread_score:.2f}",
            f"Risk concentration score: {self.report.change_surface_index.risk_concentration_score:.2f}",
            f"Overall score: {self.report.change_surface_index.overall_score:.2f}",
            f"Interpretation: {self.report.change_surface_index.interpretation}",
            "Purpose: lets agencies compare two inherited scenarios without reading them.",
        ]


class SummaryReportJSONRenderer:
    """Renders summary reports to JSON format."""

    def __init__(self, report: BlueprintSummaryReport):
        self.report = report

    def render(self) -> Dict[str, Any]:
        """Generate JSON-serializable dict representation."""
        return {
            "blueprint_name": self.report.blueprint_name,
            "platform": self.report.metadata.platform.value,
            "component_counts": self.report.component_counts.copy(),
            "total_components": self.report.total_components,
            "generated_at": self.report.metadata.generated_at.isoformat(),
            "insights": self.report.insights.copy(),
            "trigger": self._render_trigger_data(),
            "flow_structure": self._render_connections(),
            "routing_patterns": self._render_routing_patterns(),
            "external_dependencies": self._render_external_dependencies(),
            "data_surface": self._render_data_surface(),
            "risk_indicators": self._render_risk_indicators(),
            "safe_to_modify": self._render_safe_to_modify(),
            "operational_load": self._render_operational_load(),
            "execution_role": self._render_execution_role(),
            "change_surface_index": self._render_change_surface_index(),
            "report_text": self.report.to_text(),  # Include formatted text for convenience
        }

    def _render_trigger_data(self) -> Dict[str, Any]:
        """Render trigger data for JSON."""
        if not self.report.trigger:
            return {}

        return {
            "module_type": self.report.trigger.module_type,
            "execution_pattern": self.report.trigger.execution_pattern.value,
            "data_source": self.report.trigger.data_source.value,
            "reliability": self.report.trigger.reliability.value,
            "scaling": self.report.trigger.scaling.value,
            "display_name": self.report.trigger.display_name,
            "connection": {
                "requires_auth": self.report.trigger.connection.requires_auth,
                "connection_type": self.report.trigger.connection.connection_type,
                "connection_id": self.report.trigger.connection.connection_id,
                "account_reference": self.report.trigger.connection.account_reference,
            },
            "configuration": {
                "batch_size": self.report.trigger.configuration.batch_size,
                "filter_conditions": (
                    self.report.trigger.configuration.filter_conditions.copy()
                    if self.report.trigger.configuration.filter_conditions
                    else {}
                ),
            },
        }

    def _render_connections(self) -> Dict[str, Any]:
        """Render flow structure data for JSON."""
        return {
            "total_number_of_connections": self.report.built_in_connections.total_connections,
            "connections": self.report.built_in_connections.connection_types.copy(),
        }

    def _render_routing_patterns(self) -> Dict[str, Any]:
        """Render routing patterns data for JSON."""
        return {
            "router_branching_counts": self.report.routing_patterns.router_branching_counts.copy(),
            "filters_per_branch": self.report.routing_patterns.filters_per_branch.copy(),
            "has_catch_all_routes": self.report.routing_patterns.has_catch_all_routes,
            "has_unconditional_routes": self.report.routing_patterns.has_unconditional_routes,
        }

    def _render_external_dependencies(self) -> Dict[str, Any]:
        """Render external dependencies data for JSON."""
        return {
            "api_modules_and_endpoints": self.report.external_dependencies.api_modules_and_endpoints.copy(),
            "workfront_object_types": self.report.external_dependencies.workfront_object_types.copy(),
            "authentication_types": self.report.external_dependencies.authentication_types.copy(),
            "reuse_vs_oneoff_integrations": self.report.external_dependencies.reuse_vs_oneoff_integrations.copy(),
        }

    def _render_data_surface(self) -> Dict[str, Any]:
        """Render data surface data for JSON."""
        return {
            "primary_input_types": self.report.data_surface.primary_input_types.copy(),
            "major_mapped_fields": self.report.data_surface.major_mapped_fields.copy(),
            "iterated_collections": self.report.data_surface.iterated_collections.copy(),
        }

    def _render_risk_indicators(self) -> Dict[str, Any]:
        """Render risk indicators data for JSON."""
        return {
            "deeply_nested_routers": self.report.risk_indicators.deeply_nested_routers.copy(),
            "error_handlers_masking_failures": self.report.risk_indicators.error_handlers_masking_failures.copy(),
            "high_fanout_modules": self.report.risk_indicators.high_fanout_modules.copy(),
            "high_fanin_modules": self.report.risk_indicators.high_fanin_modules.copy(),
        }

    def _render_safe_to_modify(self) -> Dict[str, Any]:
        """Render safe to modify data for JSON."""
        return {
            "isolated_modules_or_branches": self.report.safe_to_modify.isolated_modules_or_branches.copy(),
            "modules_no_upstream_deps": self.report.safe_to_modify.modules_no_upstream_deps.copy(),
            "branches_not_feeding_critical_paths": self.report.safe_to_modify.branches_not_feeding_critical_paths.copy(),
        }

    def _render_operational_load(self) -> Dict[str, Any]:
        """Render operational load data for JSON."""
        return {
            "iterators_on_large_collections": self.report.operational_load.iterators_on_large_collections.copy(),
            "aggregators": self.report.operational_load.aggregators.copy(),
            "loops_with_unclear_exit_conditions": self.report.operational_load.loops_with_unclear_exit_conditions.copy(),
        }

    def _render_execution_role(self) -> Dict[str, Any]:
        """Render execution role data for JSON."""
        return {
            "scenario_vs_module_error_handlers": self.report.execution_role.scenario_vs_module_error_handlers.copy(),
            "schedulers_vs_webhooks": self.report.execution_role.schedulers_vs_webhooks.copy(),
        }

    def _render_change_surface_index(self) -> Dict[str, Any]:
        """Render change surface index data for JSON."""
        return {
            "routing_depth_score": self.report.change_surface_index.routing_depth_score,
            "dependency_spread_score": self.report.change_surface_index.dependency_spread_score,
            "risk_concentration_score": self.report.change_surface_index.risk_concentration_score,
            "overall_score": self.report.change_surface_index.overall_score,
            "interpretation": self.report.change_surface_index.interpretation,
        }
