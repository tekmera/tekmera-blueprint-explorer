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
    
    This function takes the report's built-in text formatting and converts it 
    to properly formatted PDF with styling for headings, sections, and tables.
    
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
    
    # Get the formatted text from the report
    report_text = report_data.to_text()
    
    # Build content using the report's structured text
    story = []
    styles = getSampleStyleSheet()
    
    # Define custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Center alignment
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.black
    )
    separator_style = ParagraphStyle(
        'Separator',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey
    )
    stub_style = ParagraphStyle(
        'StubNotice',
        parent=styles['Normal'],
        textColor=colors.red,
        fontName='Helvetica-Bold',
        spaceBefore=5
    )
    info_style = styles['Normal']
    
    # Parse the report text and apply PDF-specific formatting
    lines = report_text.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if not line:
            story.append(Spacer(1, 6))
            continue
            
        # Main title
        if line == "BLUEPRINT SUMMARY REPORT":
            story.append(Paragraph(line, title_style))
        
        # Section headers (all caps with dashes below)
        elif line.isupper() and not line.startswith("🔴") and not line.startswith("•"):
            story.append(Paragraph(line, heading_style))
        
        # Separator lines (dashes)
        elif line.startswith("-") and len(set(line)) == 1:
            # Skip separator lines, handled by heading spacing
            continue
        
        # Stub notices (red text)
        elif "🔴 STUB:" in line:
            story.append(Paragraph(line, stub_style))
        
        # Bullet points and regular content
        else:
            # Handle special formatting for key-value pairs
            if ":" in line and not line.startswith("•") and not line.startswith("Purpose:"):
                # Make the part before the colon bold
                parts = line.split(":", 1)
                if len(parts) == 2:
                    line = f"<b>{parts[0]}:</b>{parts[1]}"
            
            story.append(Paragraph(line, info_style))
            story.append(Spacer(1, 3))
    
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