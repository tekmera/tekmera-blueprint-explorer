"""
PDF formatter for report output.

This module provides PDF rendering functionality for typed reports.
"""

from pathlib import Path
from typing import Any

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def render_report_to_pdf(report_data: Any, output_path: str) -> str:
    """
    Render a BlueprintSummaryReport to PDF format.
    
    Args:
        report_data: The BlueprintSummaryReport object
        output_path: Path where the PDF should be saved
        
    Returns:
        The path to the generated PDF file
        
    Raises:
        ImportError: If ReportLab is not installed
        Exception: If PDF generation fails
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError(
            "ReportLab is required for PDF generation. Install with: pip install reportlab"
        )
    
    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create PDF document
    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Build content
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Center alignment
    )
    story.append(Paragraph("BLUEPRINT SUMMARY REPORT", title_style))
    story.append(Spacer(1, 12))
    
    # Blueprint Info
    info_style = styles['Normal']
    story.append(Paragraph(f"<b>Blueprint Name:</b> {report_data.blueprint_name}", info_style))
    story.append(Paragraph(f"<b>Platform:</b> {_format_platform(report_data.platform)}", info_style))
    story.append(Paragraph(f"<b>Generated:</b> {report_data.generated_at.strftime('%Y-%m-%d %H:%M:%S')}", info_style))
    story.append(Spacer(1, 20))
    
    # Component Analysis Section
    heading_style = styles['Heading2']
    story.append(Paragraph("COMPONENT ANALYSIS", heading_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(f"<b>Total Components:</b> {report_data.total_components}", info_style))
    story.append(Spacer(1, 12))
    
    # Component breakdown table
    table_data = [
        ['Component Type', 'Count'],
        ['Modules', str(report_data.component_counts.get('modules', 0))],
        ['Routers', str(report_data.component_counts.get('routers', 0))],
        ['Filters', str(report_data.component_counts.get('filters', 0))],
        ['Error Handlers', str(report_data.component_counts.get('error_handlers', 0))],
    ]
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Insights Section
    story.append(Paragraph("SUMMARY", heading_style))
    story.append(Spacer(1, 12))
    
    for insight in report_data.insights:
        story.append(Paragraph(f"• {insight}", info_style))
        story.append(Spacer(1, 6))
    
    # Build PDF
    doc.build(story)
    
    return str(output_file)


def _format_platform(platform) -> str:
    """Format platform name for display."""
    if hasattr(platform, 'value'):
        value = platform.value
    else:
        value = str(platform)
    
    if value == "workfront_fusion":
        return "Workfront Fusion"
    elif value == "make_com":
        return "Make.com"
    else:
        return value.replace('_', ' ').title()