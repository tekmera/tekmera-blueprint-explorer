"""Sample report generation for demos and testing.

This module provides sample blueprint reports for demo purposes.
"""

from datetime import datetime

from tekmera.functions.meta.types import Platform, ProjectionResult, create_result

from .summary import BlueprintSummaryReport


def create_sample_report(platform: Platform) -> ProjectionResult[BlueprintSummaryReport]:
    """Create a sample summary report for the given platform."""

    if platform == Platform.WORKFRONT_FUSION:
        return _create_workfront_fusion_sample()
    elif platform == Platform.MAKE_COM:
        return _create_make_com_sample()
    else:
        raise ValueError(f"Sample reports not available for platform: {platform}")


def _create_workfront_fusion_sample() -> ProjectionResult[BlueprintSummaryReport]:
    """Create a sample Workfront Fusion report."""

    # Sample blueprint data
    sample_blueprint = {
        "name": "Sample Workfront Fusion Automation",
        "flow": [
            {"id": 1, "module": "workfront-workfront:searchv3"},
            {"id": 2, "module": "workfront-workfront:updateRecord"},
            {"id": 3, "module": "slack:createChannel"},
        ],
    }

    # Sample component counts
    component_counts = {"modules": 15, "routers": 3, "filters": 5, "error_handlers": 2}

    total_components = sum(component_counts.values())

    # Sample insights
    insights = [
        "This is a medium complexity blueprint with 25 total components",
        "Contains 3 router(s) for conditional logic",
        "Contains 5 filter(s) for data processing",
        "Contains 2 error handler(s) for fault tolerance",
    ]

    # Create the sample report
    report = BlueprintSummaryReport(
        blueprint_name="Sample Workfront Fusion Automation",
        platform=Platform.WORKFRONT_FUSION,
        component_counts=component_counts,
        total_components=total_components,
        generated_at=datetime.now(),
        insights=insights,
    )

    return create_result(
        blueprint=sample_blueprint,
        platform=Platform.WORKFRONT_FUSION,
        function_name="reporting.summary.sample",
        data=report,
    )


def _create_make_com_sample() -> ProjectionResult[BlueprintSummaryReport]:
    """Create a sample Make.com report."""

    # Sample blueprint data
    sample_blueprint = {
        "name": "Sample Make.com Scenario",
        "flow": [
            {"id": 1, "module": "google-sheets:readRowsFromSheet"},
            {"id": 2, "module": "builtin:BasicRouter"},
            {"id": 3, "module": "slack:sendMessage"},
        ],
    }

    # Sample component counts
    component_counts = {"modules": 8, "routers": 2, "filters": 3, "error_handlers": 1}

    total_components = sum(component_counts.values())

    # Sample insights
    insights = [
        "This is a small to medium complexity blueprint",
        "Contains 2 router(s) for conditional logic",
        "Contains 3 filter(s) for data processing",
        "Contains 1 error handler(s) for fault tolerance",
    ]

    # Create the sample report
    report = BlueprintSummaryReport(
        blueprint_name="Sample Make.com Scenario",
        platform=Platform.MAKE_COM,
        component_counts=component_counts,
        total_components=total_components,
        generated_at=datetime.now(),
        insights=insights,
    )

    return create_result(
        blueprint=sample_blueprint,
        platform=Platform.MAKE_COM,
        function_name="reporting.summary.sample",
        data=report,
    )
