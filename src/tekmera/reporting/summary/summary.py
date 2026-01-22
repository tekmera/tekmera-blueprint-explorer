"""Summary report generation for single blueprints."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from tekmera.functions.components.connections.types import ConnectionComponent, create_connection_component
from tekmera.functions.meta.platform_detection import detect_platform
from tekmera.functions.meta.trigger_types import UniversalTrigger
from tekmera.functions.meta.types import Platform, ProjectionResult, create_result
from tekmera.functions.meta.utils.make_com.extract_components import extract_all_components

from ..common.types import BaseReport, ReportMetadata, ReportType

@dataclass
class BuiltInConnections:
    """Connections analysis - STUB: requires real data analysis."""

    def __init__(
            self,
            total_connections: int,
            connections: List[ConnectionComponent]
    ):
        self.total_connections = total_connections
        self.connection_types = connections


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
        built_in_connections: Optional[BuiltInConnections] = None,
        routing_patterns: Optional[RoutingAndLogicPatterns] = None,
        external_dependencies: Optional[ExternalDependencyTable] = None,
        data_surface: Optional[DataSurfaceSummary] = None,
        risk_indicators: Optional[RiskIndicators] = None,
        safe_to_modify: Optional[SafeToModifyHeuristics] = None,
        operational_load: Optional[OperationalLoadSignals] = None,
        execution_role: Optional[ExecutionRoleSummary] = None,
        change_surface_index: Optional[ChangeSurfaceIndex] = None,
    ):
        """Initialize summary report with data."""
        metadata = ReportMetadata(
            report_type=ReportType.SUMMARY,
            platform=platform,
            generated_at=generated_at or datetime.now(),
        )
        super().__init__(metadata)

        # Core data
        self.blueprint_name = blueprint_name
        self.component_counts = component_counts
        self.total_components = total_components
        self.insights = insights or []

        # Analysis sections
        self.trigger = trigger
        self.built_in_connections = built_in_connections or BuiltInConnections(0, {})
        self.routing_patterns = routing_patterns or RoutingAndLogicPatterns()
        self.external_dependencies = external_dependencies or ExternalDependencyTable()
        self.data_surface = data_surface or DataSurfaceSummary()
        self.risk_indicators = risk_indicators or RiskIndicators()
        self.safe_to_modify = safe_to_modify or SafeToModifyHeuristics()
        self.operational_load = operational_load or OperationalLoadSignals()
        self.execution_role = execution_role or ExecutionRoleSummary()
        self.change_surface_index = change_surface_index or ChangeSurfaceIndex()

    def to_text(self) -> str:
        """Generate formatted text report using dedicated renderer."""
        from .renderers import SummaryReportTextRenderer

        renderer = SummaryReportTextRenderer(self)
        return renderer.render()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization using dedicated renderer."""
        from .renderers import SummaryReportJSONRenderer

        renderer = SummaryReportJSONRenderer(self)
        return renderer.render()


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

    connections = generate_connections(blueprint)

    # Create the new reporting format
    report = BlueprintSummaryReport(
        blueprint_name=blueprint_name,
        platform=platform,
        component_counts=component_counts,
        total_components=total_components,
        generated_at=datetime.now(),
        insights=insights,
        trigger=trigger,
        built_in_connections=connections,
    )

    # Return in the same format but with new report type
    return create_result(
        blueprint=blueprint, platform=platform, function_name="reporting.summary", data=report
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
    router_count = component_counts.get("routers", 0)
    if router_count > 0:
        insights.append(f"Contains {router_count} router(s) for conditional logic")

    # Filter analysis
    filter_count = component_counts.get("filters", 0)
    if filter_count > 0:
        insights.append(f"Contains {filter_count} filter(s) for data processing")

    # Error handling analysis
    error_handler_count = component_counts.get("error_handlers", 0)
    if error_handler_count > 0:
        insights.append(f"Contains {error_handler_count} error handler(s) for fault tolerance")
    else:
        insights.append("No error handlers detected - consider adding for robustness")

    return insights

def generate_connections(blueprint: Dict[str, Any]) -> BuiltInConnections:
    """Generate built-in connections analysis given the blueprint data."""
    # Placeholder implementation
    connections = []
    
    components = extract_all_components(blueprint)
    for component in components["modules"]:
        if ('__IMTCONN__' in component.raw_data.get('parameters', {})):
            connection = create_connection_component(
                component.id,
                blueprint,
                component.extraction_context,
                component.raw_data,
                component.raw_data.get('parameters', {}).get('__IMTCONN__', {})
            )
            connections.append(connection)

    # Remove duplicates based on connection_label
    seen = set()
    connections = [obj for obj in connections if obj.connection_label not in seen and not seen.add(obj.connection_label)]
    
    return BuiltInConnections(
        total_connections=len(connections),
        connections=connections
    )