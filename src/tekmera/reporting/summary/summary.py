"""Summary report generation for single blueprints."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..common.types import BaseReport, ReportMetadata, ReportType
from tekmera.projections.meta.trigger_types import UniversalTrigger
from tekmera.projections.meta.types import Platform, ProjectionResult, create_result
from tekmera.projections.meta.platform_detection import detect_platform


@dataclass
class FlowStructureMap:
    """Flow structure analysis - STUB: requires real data analysis."""
    total_top_level_branches: int = 0
    longest_execution_path: int = 0 
    deepest_nested_router_level: int = 0
    iterator_aggregator_positions: List[str] = field(default_factory=list)


@dataclass
class RoutingAndLogicPatterns:
    """Routing and logic patterns analysis - STUB: requires real data analysis."""
    router_branching_counts: Dict[str, int] = field(default_factory=dict)
    filters_per_branch: Dict[str, int] = field(default_factory=dict)
    has_catch_all_routes: bool = False
    has_unconditional_routes: bool = False


@dataclass
class ExternalDependencyTable:
    """External dependencies analysis - STUB: requires real data analysis."""
    api_modules_and_endpoints: List[Dict[str, str]] = field(default_factory=list)
    workfront_object_types: List[str] = field(default_factory=list)
    authentication_types: List[str] = field(default_factory=list)
    reuse_vs_oneoff_integrations: Dict[str, str] = field(default_factory=dict)


@dataclass
class DataSurfaceSummary:
    """Data surface analysis - STUB: requires real data analysis."""
    primary_input_types: List[str] = field(default_factory=list)
    major_mapped_fields: List[str] = field(default_factory=list)
    iterated_collections: List[str] = field(default_factory=list)


@dataclass
class RiskIndicators:
    """Risk analysis - STUB: requires real data analysis."""
    deeply_nested_routers: List[str] = field(default_factory=list)
    error_handlers_masking_failures: List[str] = field(default_factory=list)
    high_fanout_modules: List[str] = field(default_factory=list)
    high_fanin_modules: List[str] = field(default_factory=list)


@dataclass
class SafeToModifyHeuristics:
    """Safe modification analysis - STUB: requires real data analysis."""
    isolated_modules_or_branches: List[str] = field(default_factory=list)
    modules_no_upstream_deps: List[str] = field(default_factory=list)
    branches_not_feeding_critical_paths: List[str] = field(default_factory=list)


@dataclass
class OperationalLoadSignals:
    """Operational load analysis - STUB: requires real data analysis."""
    iterators_on_large_collections: List[str] = field(default_factory=list)
    aggregators: List[str] = field(default_factory=list)
    loops_with_unclear_exit_conditions: List[str] = field(default_factory=list)


@dataclass
class ExecutionRoleSummary:
    """Execution role analysis - STUB: requires real data analysis."""
    scenario_vs_module_error_handlers: Dict[str, int] = field(default_factory=dict)
    schedulers_vs_webhooks: Dict[str, int] = field(default_factory=dict)


@dataclass
class ChangeSurfaceIndex:
    """Change surface complexity score - STUB: requires real data analysis."""
    routing_depth_score: float = 0.0
    dependency_spread_score: float = 0.0
    risk_concentration_score: float = 0.0
    overall_score: float = 0.0
    interpretation: str = "Not yet calculated"


class BlueprintSummaryReport(BaseReport):
    """Platform-agnostic summary report for a single blueprint."""
    
    def __init__(
        self,
        blueprint_name: str,
        platform: Platform,
        component_counts: Dict[str, int],
        total_components: int,
        generated_at: Optional[datetime] = None,
        insights: Optional[List[str]] = None,
        trigger: Optional[UniversalTrigger] = None,
        flow_structure: Optional[FlowStructureMap] = None,
        routing_patterns: Optional[RoutingAndLogicPatterns] = None,
        external_dependencies: Optional[ExternalDependencyTable] = None,
        data_surface: Optional[DataSurfaceSummary] = None,
        risk_indicators: Optional[RiskIndicators] = None,
        safe_to_modify: Optional[SafeToModifyHeuristics] = None,
        operational_load: Optional[OperationalLoadSignals] = None,
        execution_role: Optional[ExecutionRoleSummary] = None,
        change_surface_index: Optional[ChangeSurfaceIndex] = None
    ):
        """Initialize summary report with data."""
        metadata = ReportMetadata(
            report_type=ReportType.SUMMARY,
            platform=platform,
            generated_at=generated_at or datetime.now()
        )
        super().__init__(metadata)
        
        # Core data
        self.blueprint_name = blueprint_name
        self.component_counts = component_counts
        self.total_components = total_components
        self.insights = insights or []
        
        # Analysis sections
        self.trigger = trigger
        self.flow_structure = flow_structure or FlowStructureMap()
        self.routing_patterns = routing_patterns or RoutingAndLogicPatterns()
        self.external_dependencies = external_dependencies or ExternalDependencyTable()
        self.data_surface = data_surface or DataSurfaceSummary()
        self.risk_indicators = risk_indicators or RiskIndicators()
        self.safe_to_modify = safe_to_modify or SafeToModifyHeuristics()
        self.operational_load = operational_load or OperationalLoadSignals()
        self.execution_role = execution_role or ExecutionRoleSummary()
        self.change_surface_index = change_surface_index or ChangeSurfaceIndex()
    
    def to_text(self) -> str:
        """Generate formatted text report."""
        report_lines = [
            "=" * 60,
            "BLUEPRINT SUMMARY REPORT", 
            "=" * 60,
            "",
            f"Blueprint Name: {self.blueprint_name}",
            f"Platform: {self._format_platform()}",
            f"Generated: {self.metadata.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "COMPONENT ANALYSIS",
            "-" * 30,
            f"Total Components: {self.total_components}",
            "",
            "Breakdown by Type:",
            f"  • Modules:        {self.component_counts.get('modules', 0):4d}",
            f"  • Routers:        {self.component_counts.get('routers', 0):4d}",
            f"  • Filters:        {self.component_counts.get('filters', 0):4d}",
            f"  • Error Handlers: {self.component_counts.get('error_handlers', 0):4d}",
            "",
            "SUMMARY",
            "-" * 30,
        ]
        
        # Add insights
        for insight in self.insights:
            report_lines.append(f"• {insight}")
        
        # Add trigger analysis section
        report_lines.extend([
            "",
            "",
            "TRIGGER ANALYSIS",
            "-" * 30,
        ])
        
        if self.trigger:
            report_lines.extend([
                f"Trigger Type: {self.trigger.module_type}",
                f"Execution Pattern: {self.trigger.execution_pattern.value.replace('_', ' ').title()}",
                f"Data Source: {self.trigger.data_source.value.replace('_', ' ').title()}",
                f"Reliability: {self.trigger.reliability.value.replace('_', ' ').title()}",
                f"Scaling: {self.trigger.scaling.value.replace('_', ' ').title()}",
            ])
            
            if self.trigger.display_name:
                report_lines.append(f"Display Name: {self.trigger.display_name}")
            
            # Connection details
            if self.trigger.connection.requires_auth:
                conn_type = self.trigger.connection.connection_type or "Unknown"
                report_lines.append(f"Connection Type: {conn_type.replace('_', ' ').title()}")
                
                if self.trigger.connection.connection_id:
                    report_lines.append(f"Connection ID: {self.trigger.connection.connection_id}")
                
                if self.trigger.connection.account_reference:
                    report_lines.append(f"Account Reference: {self.trigger.connection.account_reference}")
            else:
                report_lines.append("Connection Type: No authentication required")
            
            # Configuration details
            if self.trigger.configuration.batch_size:
                report_lines.append(f"Batch Size: {self.trigger.configuration.batch_size}")
            
            if self.trigger.configuration.filter_conditions:
                filter_count = len(self.trigger.configuration.filter_conditions)
                report_lines.append(f"Filter Conditions: {filter_count} configured")
        else:
            report_lines.append("No trigger information available")
        
        # Add stubbed advanced analysis sections
        report_lines.extend([
            "",
            "",
            "1. FLOW STRUCTURE MAP",
            "-" * 30,
            "🔴 STUB: Requires real data analysis",
            f"Total top-level branches: {self.flow_structure.total_top_level_branches}",
            f"Longest execution path: {self.flow_structure.longest_execution_path}",
            f"Deepest nested router level: {self.flow_structure.deepest_nested_router_level}",
            f"Iterator/aggregator positions: {', '.join(self.flow_structure.iterator_aggregator_positions) or 'None identified'}",
            "Purpose: gives reviewers a skeletal understanding before diving into detail.",
            "",
            "2. ROUTING AND LOGIC PATTERNS", 
            "-" * 30,
            "🔴 STUB: Requires real data analysis",
            f"Router branching counts: {len(self.routing_patterns.router_branching_counts)} routers analyzed",
            f"Filters per branch: {len(self.routing_patterns.filters_per_branch)} branches with filters",
            f"Catch-all routes present: {self.routing_patterns.has_catch_all_routes}",
            f"Unconditional routes present: {self.routing_patterns.has_unconditional_routes}",
            "Purpose: highlights complexity concentration and decision-surface width.",
            "",
            "3. EXTERNAL DEPENDENCY TABLE",
            "-" * 30,
            f"API modules + endpoints: {len(self.external_dependencies.api_modules_and_endpoints)} identified",
            f"Workfront object types touched: {', '.join(self.external_dependencies.workfront_object_types) or 'None identified'}",
            f"Authentication types: {', '.join(self.external_dependencies.authentication_types) or 'None identified'}",
            f"Reuse vs one-off integrations: {len(self.external_dependencies.reuse_vs_oneoff_integrations)} mappings",
            "Purpose: shows 'what the automation touches' in one place.",
            "",
            "4. DATA SURFACE SUMMARY",
            "-" * 30,
            f"Primary input types: {', '.join(self.data_surface.primary_input_types) or 'None identified'}",
            f"Major mapped fields: {len(self.data_surface.major_mapped_fields)} fields",
            f"Iterated collections: {', '.join(self.data_surface.iterated_collections) or 'None identified'}",
            "Purpose: identifies the data the scenario expects, transforms, and passes downstream.",
            "",
            "5. RISK INDICATORS",
            "-" * 30,
            "🔴 STUB: Requires real data analysis",
            f"Deeply nested routers: {len(self.risk_indicators.deeply_nested_routers)} identified",
            f"Error handlers that mask failures: {len(self.risk_indicators.error_handlers_masking_failures)} identified",
            f"Modules with high fan-out: {len(self.risk_indicators.high_fanout_modules)} identified",
            f"Modules with high fan-in: {len(self.risk_indicators.high_fanin_modules)} identified",
            "Purpose: exposes brittle and high-impact regions.",
            "",
            "6. SAFE-TO-MODIFY HEURISTICS",
            "-" * 30,
            "🔴 STUB: Requires real data analysis",
            f"Isolated modules or branches: {len(self.safe_to_modify.isolated_modules_or_branches)} identified",
            f"Modules with no upstream dependencies: {len(self.safe_to_modify.modules_no_upstream_deps)} identified",
            f"Branches not feeding critical paths: {len(self.safe_to_modify.branches_not_feeding_critical_paths)} identified",
            "Purpose: supports estimation and quoting.",
            "",
            "7. OPERATIONAL LOAD SIGNALS",
            "-" * 30,
            "🔴 STUB: Requires real data analysis",
            f"Iterators on large collections: {len(self.operational_load.iterators_on_large_collections)} identified",
            f"Aggregators: {len(self.operational_load.aggregators)} identified",
            f"Loops with unclear exit conditions: {len(self.operational_load.loops_with_unclear_exit_conditions)} identified",
            "Purpose: flags performance and cost implications.",
            "",
            "8. EXECUTION ROLE SUMMARY",
            "-" * 30,
            f"Scenario vs module level error handlers: {self.execution_role.scenario_vs_module_error_handlers}",
            f"Schedulers vs webhooks: {self.execution_role.schedulers_vs_webhooks}",
            "Purpose: reveals how the scenario is supposed to run and fail.",
            "",
            "9. CHANGE SURFACE INDEX",
            "-" * 30,
            "🔴 STUB: Requires real data analysis",
            f"Routing depth score: {self.change_surface_index.routing_depth_score:.2f}",
            f"Dependency spread score: {self.change_surface_index.dependency_spread_score:.2f}",
            f"Risk concentration score: {self.change_surface_index.risk_concentration_score:.2f}", 
            f"Overall score: {self.change_surface_index.overall_score:.2f}",
            f"Interpretation: {self.change_surface_index.interpretation}",
            "Purpose: lets agencies compare two inherited scenarios without reading them.",
        ])
        
        report_lines.extend([
            "",
            "=" * 60,
            "End of Report",
            "=" * 60
        ])
        
        return "\n".join(report_lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "blueprint_name": self.blueprint_name,
            "platform": self.metadata.platform.value,
            "component_counts": self.component_counts.copy(),
            "total_components": self.total_components,
            "generated_at": self.metadata.generated_at.isoformat(),
            "insights": self.insights.copy(),
            "trigger": {
                "module_type": self.trigger.module_type if self.trigger else None,
                "execution_pattern": self.trigger.execution_pattern.value if self.trigger else None,
                "data_source": self.trigger.data_source.value if self.trigger else None,
                "reliability": self.trigger.reliability.value if self.trigger else None,
                "scaling": self.trigger.scaling.value if self.trigger else None,
                "display_name": self.trigger.display_name if self.trigger else None,
                "connection": {
                    "requires_auth": self.trigger.connection.requires_auth if self.trigger else None,
                    "connection_type": self.trigger.connection.connection_type if self.trigger else None,
                    "connection_id": self.trigger.connection.connection_id if self.trigger else None,
                    "account_reference": self.trigger.connection.account_reference if self.trigger else None
                } if self.trigger else None,
                "configuration": {
                    "batch_size": self.trigger.configuration.batch_size if self.trigger else None,
                    "filter_conditions": self.trigger.configuration.filter_conditions.copy() if self.trigger and self.trigger.configuration.filter_conditions else {}
                } if self.trigger else None
            },
            "flow_structure": {
                "total_top_level_branches": self.flow_structure.total_top_level_branches,
                "longest_execution_path": self.flow_structure.longest_execution_path,
                "deepest_nested_router_level": self.flow_structure.deepest_nested_router_level,
                "iterator_aggregator_positions": self.flow_structure.iterator_aggregator_positions.copy()
            },
            "routing_patterns": {
                "router_branching_counts": self.routing_patterns.router_branching_counts.copy(),
                "filters_per_branch": self.routing_patterns.filters_per_branch.copy(),
                "has_catch_all_routes": self.routing_patterns.has_catch_all_routes,
                "has_unconditional_routes": self.routing_patterns.has_unconditional_routes
            },
            "external_dependencies": {
                "api_modules_and_endpoints": self.external_dependencies.api_modules_and_endpoints.copy(),
                "workfront_object_types": self.external_dependencies.workfront_object_types.copy(),
                "authentication_types": self.external_dependencies.authentication_types.copy(),
                "reuse_vs_oneoff_integrations": self.external_dependencies.reuse_vs_oneoff_integrations.copy()
            },
            "data_surface": {
                "primary_input_types": self.data_surface.primary_input_types.copy(),
                "major_mapped_fields": self.data_surface.major_mapped_fields.copy(),
                "iterated_collections": self.data_surface.iterated_collections.copy()
            },
            "risk_indicators": {
                "deeply_nested_routers": self.risk_indicators.deeply_nested_routers.copy(),
                "error_handlers_masking_failures": self.risk_indicators.error_handlers_masking_failures.copy(),
                "high_fanout_modules": self.risk_indicators.high_fanout_modules.copy(),
                "high_fanin_modules": self.risk_indicators.high_fanin_modules.copy()
            },
            "safe_to_modify": {
                "isolated_modules_or_branches": self.safe_to_modify.isolated_modules_or_branches.copy(),
                "modules_no_upstream_deps": self.safe_to_modify.modules_no_upstream_deps.copy(),
                "branches_not_feeding_critical_paths": self.safe_to_modify.branches_not_feeding_critical_paths.copy()
            },
            "operational_load": {
                "iterators_on_large_collections": self.operational_load.iterators_on_large_collections.copy(),
                "aggregators": self.operational_load.aggregators.copy(),
                "loops_with_unclear_exit_conditions": self.operational_load.loops_with_unclear_exit_conditions.copy()
            },
            "execution_role": {
                "scenario_vs_module_error_handlers": self.execution_role.scenario_vs_module_error_handlers.copy(),
                "schedulers_vs_webhooks": self.execution_role.schedulers_vs_webhooks.copy()
            },
            "change_surface_index": {
                "routing_depth_score": self.change_surface_index.routing_depth_score,
                "dependency_spread_score": self.change_surface_index.dependency_spread_score,
                "risk_concentration_score": self.change_surface_index.risk_concentration_score,
                "overall_score": self.change_surface_index.overall_score,
                "interpretation": self.change_surface_index.interpretation
            },
            "report_text": self.to_text()  # Include formatted text for convenience
        }


def generate_summary_report(blueprint: Dict[str, Any]) -> ProjectionResult[BlueprintSummaryReport]:
    """
    Generate summary report using component analysis directly.
    
    This function analyzes components directly without delegating to 
    the old projections structure, maintaining clean separation.
    """
    # Detect platform and route to platform-specific analysis
    platform = detect_platform(blueprint)
    
    # Extract blueprint metadata
    blueprint_name = blueprint.get("name", "Unnamed Blueprint")
    
    # Use platform-specific helpers
    if platform == Platform.WORKFRONT_FUSION:
        from ..common.platforms.workfront_fusion import WorkfrontFusionReportingHelper
        component_counts = WorkfrontFusionReportingHelper.analyze_components(blueprint)
        trigger = WorkfrontFusionReportingHelper.detect_trigger(blueprint)
    elif platform == Platform.MAKE_COM:
        from ..common.platforms.make_com import MakeComReportingHelper  
        component_counts = MakeComReportingHelper.analyze_components(blueprint)
        trigger = MakeComReportingHelper.detect_trigger(blueprint)
    else:
        # Fallback for unknown platforms
        component_counts = {"modules": 0, "routers": 0, "filters": 0, "error_handlers": 0}
        trigger = None
    
    total_components = sum(component_counts.values())
    
    # Generate insights
    insights = generate_insights(component_counts, total_components)
    
    # Create the new reporting format
    report = BlueprintSummaryReport(
        blueprint_name=blueprint_name,
        platform=platform,
        component_counts=component_counts,
        total_components=total_components,
        generated_at=datetime.now(),
        insights=insights,
        trigger=trigger
    )
    
    # Return in the same format but with new report type
    return create_result(
        blueprint=blueprint,
        platform=platform,
        function_name="reporting.summary",
        data=report
    )


def generate_insights(component_counts: Dict[str, int], total_components: int) -> List[str]:
    """Generate analysis insights based on component counts."""
    insights = []
    
    # Complexity analysis
    if total_components == 0:
        insights.append("This blueprint contains no components")
    elif total_components == 1:
        insights.append("This is a simple single-component blueprint")
    elif total_components <= 10:
        insights.append("This is a small to medium complexity blueprint")
    elif total_components <= 50:
        insights.append("This is a medium to high complexity blueprint")
    else:
        insights.append("This is a high complexity blueprint with many components")
    
    # Router analysis
    router_count = component_counts.get('routers', 0)
    if router_count > 0:
        insights.append(f"Contains {router_count} router(s) for conditional logic")
    
    # Filter analysis
    filter_count = component_counts.get('filters', 0)
    if filter_count > 0:
        insights.append(f"Contains {filter_count} filter(s) for data processing")
    
    # Error handling analysis
    error_handler_count = component_counts.get('error_handlers', 0)
    if error_handler_count > 0:
        insights.append(f"Contains {error_handler_count} error handler(s) for fault tolerance")
    else:
        insights.append("No error handlers detected - consider adding for robustness")
    
    return insights