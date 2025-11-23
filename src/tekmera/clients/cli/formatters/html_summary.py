"""HTML formatter specifically for summary reports."""

import html
from pathlib import Path

from .base import BaseFormatter, register_formatter
from tekmera.reporting.common.types import BaseReport, ReportType, ReportFormat
from tekmera.reporting.summary.summary import BlueprintSummaryReport


@register_formatter(ReportType.SUMMARY, ReportFormat.HTML)
class HTMLSummaryFormatter(BaseFormatter):
    """HTML formatter for summary reports."""
    
    def render(self, report: BaseReport) -> str:
        """Render summary report as HTML."""
        if not isinstance(report, BlueprintSummaryReport):
            raise ValueError(f"HTMLSummaryFormatter can only render BlueprintSummaryReport, got {type(report)}")
        
        return self._generate_html(report)
    
    def get_file_extension(self) -> str:
        """HTML files have .html extension."""
        return ".html"
    
    def should_write_to_file(self) -> bool:
        """HTML output should be written to file."""
        return True
    
    def _generate_html(self, report: BlueprintSummaryReport) -> str:
        """Generate complete HTML document for summary report."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tekmera Blueprint Summary - {html.escape(report.blueprint_name)}</title>
    {self._load_css()}
</head>
<body>
    <div class="page-container">
        <aside class="sidebar">
            {self._generate_sidebar(report)}
        </aside>
        
        <main class="main-content">
            <div class="container">
                <header>
                    <h1>Blueprint Summary Report</h1>
                </header>
                
                {self._generate_overview(report)}
                {self._generate_component_analysis(report)}
                {self._generate_trigger_analysis(report)}
                {self._generate_advanced_sections(report)}
            </div>
        </main>
    </div>
</body>
</html>"""

    def _load_css(self) -> str:
        """Load CSS styles from separate file."""
        try:
            css_path = Path(__file__).parent / "styles.css"
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            return f"    <style>\n{css_content}\n    </style>"
        except FileNotFoundError:
            # Fallback to basic inline styles
            return """    <style>
        :root { --tekmera-blue: #183664; --tekmera-sky: #42B8E6; }
        body { font-family: sans-serif; color: #333; margin: 0; padding: 20px; }
        h1, h2, h3 { color: var(--tekmera-blue); }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; }
        .sidebar { background: var(--tekmera-blue); color: white; padding: 20px; width: 250px; }
        .main-content { flex: 1; padding: 20px; }
        .page-container { display: flex; min-height: 100vh; }
        .info-item { margin: 8px 0; color: var(--tekmera-blue); font-weight: 500; }
        .section-card { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border: 1px solid #dee2e6; border-left: 4px solid var(--tekmera-sky); border-radius: 8px; padding: 20px; margin: 15px 0; }
        .stub-warning { color: #dc3545; font-weight: bold; font-size: 1.1em; margin: 10px 0; }
    </style>"""

    def _generate_sidebar(self, report: BlueprintSummaryReport) -> str:
        """Generate sidebar navigation."""
        return f"""
            <h3>Report Navigation</h3>
            <ul>
                <li><a href="#overview">Overview</a></li>
                <li><a href="#components">Component Analysis</a></li>
                <li><a href="#trigger">Trigger Analysis</a></li>
                <li><a href="#flow-structure">Flow Structure</a></li>
                <li><a href="#routing-patterns">Routing Patterns</a></li>
                <li><a href="#dependencies">Dependencies</a></li>
                <li><a href="#data-surface">Data Surface</a></li>
                <li><a href="#risk-indicators">Risk Indicators</a></li>
                <li><a href="#safe-modify">Safe to Modify</a></li>
                <li><a href="#operational-load">Operational Load</a></li>
                <li><a href="#execution-role">Execution Role</a></li>
                <li><a href="#change-surface">Change Surface</a></li>
            </ul>
            
            <h3>Report Details</h3>
            <div class="info-item">Platform: {report._format_platform()}</div>
            <div class="info-item">Generated: {report.metadata.generated_at.strftime('%Y-%m-%d %H:%M')}</div>
            <div class="info-item">Total Components: {report.total_components}</div>
        """

    def _generate_overview(self, report: BlueprintSummaryReport) -> str:
        """Generate overview section."""
        return f"""
                <section id="overview">
                    <h2>Overview</h2>
                    <div class="section-card">
                        <div class="info-item"><strong>Blueprint Name:</strong> {html.escape(report.blueprint_name)}</div>
                        <div class="info-item"><strong>Platform:</strong> {report._format_platform()}</div>
                        <div class="info-item"><strong>Generated:</strong> {report.metadata.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</div>
                        <div class="info-item"><strong>Total Components:</strong> {report.total_components}</div>
                    </div>
                </section>
        """

    def _generate_component_analysis(self, report: BlueprintSummaryReport) -> str:
        """Generate component breakdown section."""
        breakdown_html = []
        for component_type, count in report.component_counts.items():
            breakdown_html.append(f"<div class='info-item'><strong>{component_type.replace('_', ' ').title()}:</strong> {count}</div>")
        
        insights_html = []
        for insight in report.insights:
            insights_html.append(f"<li>{html.escape(insight)}</li>")
        
        return f"""
                <section id="components">
                    <h2>Component Analysis</h2>
                    <div class="section-card">
                        <h3>Breakdown by Type</h3>
                        {''.join(breakdown_html)}
                        
                        <h3>Analysis Insights</h3>
                        <ul>
                            {''.join(insights_html)}
                        </ul>
                    </div>
                </section>
        """

    def _generate_trigger_analysis(self, report: BlueprintSummaryReport) -> str:
        """Generate trigger analysis section."""
        if report.trigger:
            trigger_html = f"""
                        <div class="info-item"><strong>Trigger Type:</strong> {html.escape(report.trigger.module_type)}</div>
                        <div class="info-item"><strong>Execution Pattern:</strong> {html.escape(report.trigger.execution_pattern.value.replace('_', ' ').title())}</div>
                        <div class="info-item"><strong>Data Source:</strong> {html.escape(report.trigger.data_source.value.replace('_', ' ').title())}</div>
                        <div class="info-item"><strong>Reliability:</strong> {html.escape(report.trigger.reliability.value.replace('_', ' ').title())}</div>
                        <div class="info-item"><strong>Scaling:</strong> {html.escape(report.trigger.scaling.value.replace('_', ' ').title())}</div>
            """
            
            if report.trigger.display_name:
                trigger_html += f"""<div class="info-item"><strong>Display Name:</strong> {html.escape(report.trigger.display_name)}</div>"""
            
            # Add connection details
            if report.trigger.connection.requires_auth:
                conn_type = report.trigger.connection.connection_type or "Unknown"
                trigger_html += f"""<div class="info-item"><strong>Connection Type:</strong> {html.escape(conn_type.replace('_', ' ').title())}</div>"""
                
                if report.trigger.connection.connection_id:
                    trigger_html += f"""<div class="info-item"><strong>Connection ID:</strong> {html.escape(str(report.trigger.connection.connection_id))}</div>"""
            else:
                trigger_html += """<div class="info-item"><strong>Connection Type:</strong> No authentication required</div>"""
        else:
            trigger_html = "<div class='info-item'>No trigger information available</div>"
        
        return f"""
                <section id="trigger">
                    <h2>Trigger Analysis</h2>
                    <div class="section-card">
                        {trigger_html}
                    </div>
                </section>
        """

    def _generate_advanced_sections(self, report: BlueprintSummaryReport) -> str:
        """Generate the advanced analysis sections (currently stubs)."""
        return f"""
                <section id="flow-structure">
                    <h2>1. Flow Structure Map</h2>
                    <div class="section-card">
                        <div class="stub-warning">🔴 STUB: Requires real data analysis</div>
                        <div class="info-item">Total top-level branches: {report.flow_structure.total_top_level_branches}</div>
                        <div class="info-item">Longest execution path: {report.flow_structure.longest_execution_path}</div>
                        <div class="info-item">Deepest nested router level: {report.flow_structure.deepest_nested_router_level}</div>
                        <p><em>Purpose: gives reviewers a skeletal understanding before diving into detail.</em></p>
                    </div>
                </section>

                <section id="routing-patterns">
                    <h2>2. Routing and Logic Patterns</h2>
                    <div class="section-card">
                        <div class="stub-warning">🔴 STUB: Requires real data analysis</div>
                        <div class="info-item">Router branching counts: {len(report.routing_patterns.router_branching_counts)} routers analyzed</div>
                        <div class="info-item">Filters per branch: {len(report.routing_patterns.filters_per_branch)} branches with filters</div>
                        <div class="info-item">Catch-all routes present: {report.routing_patterns.has_catch_all_routes}</div>
                        <div class="info-item">Unconditional routes present: {report.routing_patterns.has_unconditional_routes}</div>
                        <p><em>Purpose: highlights complexity concentration and decision-surface width.</em></p>
                    </div>
                </section>

                <section id="dependencies">
                    <h2>3. External Dependency Table</h2>
                    <div class="section-card">
                        <div class="info-item">API modules + endpoints: {len(report.external_dependencies.api_modules_and_endpoints)} identified</div>
                        <div class="info-item">Workfront object types: {', '.join(report.external_dependencies.workfront_object_types) or 'None identified'}</div>
                        <div class="info-item">Authentication types: {', '.join(report.external_dependencies.authentication_types) or 'None identified'}</div>
                        <p><em>Purpose: shows 'what the automation touches' in one place.</em></p>
                    </div>
                </section>

                <section id="data-surface">
                    <h2>4. Data Surface Summary</h2>
                    <div class="section-card">
                        <div class="info-item">Primary input types: {', '.join(report.data_surface.primary_input_types) or 'None identified'}</div>
                        <div class="info-item">Major mapped fields: {len(report.data_surface.major_mapped_fields)} fields</div>
                        <div class="info-item">Iterated collections: {', '.join(report.data_surface.iterated_collections) or 'None identified'}</div>
                        <p><em>Purpose: identifies the data the scenario expects, transforms, and passes downstream.</em></p>
                    </div>
                </section>

                <section id="risk-indicators">
                    <h2>5. Risk Indicators</h2>
                    <div class="section-card">
                        <div class="stub-warning">🔴 STUB: Requires real data analysis</div>
                        <div class="info-item">Deeply nested routers: {len(report.risk_indicators.deeply_nested_routers)} identified</div>
                        <div class="info-item">Error handlers masking failures: {len(report.risk_indicators.error_handlers_masking_failures)} identified</div>
                        <div class="info-item">High fan-out modules: {len(report.risk_indicators.high_fanout_modules)} identified</div>
                        <div class="info-item">High fan-in modules: {len(report.risk_indicators.high_fanin_modules)} identified</div>
                        <p><em>Purpose: exposes brittle and high-impact regions.</em></p>
                    </div>
                </section>

                <section id="safe-modify">
                    <h2>6. Safe-to-Modify Heuristics</h2>
                    <div class="section-card">
                        <div class="stub-warning">🔴 STUB: Requires real data analysis</div>
                        <div class="info-item">Isolated modules or branches: {len(report.safe_to_modify.isolated_modules_or_branches)} identified</div>
                        <div class="info-item">Modules with no upstream dependencies: {len(report.safe_to_modify.modules_no_upstream_deps)} identified</div>
                        <div class="info-item">Branches not feeding critical paths: {len(report.safe_to_modify.branches_not_feeding_critical_paths)} identified</div>
                        <p><em>Purpose: supports estimation and quoting.</em></p>
                    </div>
                </section>

                <section id="operational-load">
                    <h2>7. Operational Load Signals</h2>
                    <div class="section-card">
                        <div class="stub-warning">🔴 STUB: Requires real data analysis</div>
                        <div class="info-item">Iterators on large collections: {len(report.operational_load.iterators_on_large_collections)} identified</div>
                        <div class="info-item">Aggregators: {len(report.operational_load.aggregators)} identified</div>
                        <div class="info-item">Loops with unclear exit conditions: {len(report.operational_load.loops_with_unclear_exit_conditions)} identified</div>
                        <p><em>Purpose: flags performance and cost implications.</em></p>
                    </div>
                </section>

                <section id="execution-role">
                    <h2>8. Execution Role Summary</h2>
                    <div class="section-card">
                        <div class="info-item">Scenario vs module level error handlers: {report.execution_role.scenario_vs_module_error_handlers}</div>
                        <div class="info-item">Schedulers vs webhooks: {report.execution_role.schedulers_vs_webhooks}</div>
                        <p><em>Purpose: reveals how the scenario is supposed to run and fail.</em></p>
                    </div>
                </section>

                <section id="change-surface">
                    <h2>9. Change Surface Index</h2>
                    <div class="section-card">
                        <div class="stub-warning">🔴 STUB: Requires real data analysis</div>
                        <div class="info-item">Routing depth score: {report.change_surface_index.routing_depth_score:.2f}</div>
                        <div class="info-item">Dependency spread score: {report.change_surface_index.dependency_spread_score:.2f}</div>
                        <div class="info-item">Risk concentration score: {report.change_surface_index.risk_concentration_score:.2f}</div>
                        <div class="info-item">Overall score: {report.change_surface_index.overall_score:.2f}</div>
                        <div class="info-item">Interpretation: {html.escape(report.change_surface_index.interpretation)}</div>
                        <p><em>Purpose: lets agencies compare two inherited scenarios without reading them.</em></p>
                    </div>
                </section>
        """