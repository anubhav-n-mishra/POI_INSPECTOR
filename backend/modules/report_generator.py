"""PDF report generation for POI analysis."""
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from io import BytesIO

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon

from config import settings


class ReportGenerator:
    """Generates PDF reports for POI analysis."""
    
    def __init__(self):
        self.reports_dir = settings.reports_dir
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#3b82f6'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#6b7280')
        ))
    
    def generate_report(self, analysis_data: Dict, output_filename: str = None) -> Path:
        """
        Generate PDF report for POI analysis.
        
        Args:
            analysis_data: Complete analysis results
            output_filename: Optional custom filename
        
        Returns:
            Path to generated PDF
        """
        if not output_filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            poi_id = analysis_data.get('poi_id', 'unknown')
            output_filename = f"poi_report_{poi_id}_{timestamp}.pdf"
        
        output_path = self.reports_dir / output_filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build content
        story = []
        
        # Title
        story.append(Paragraph("POI Blueprint Quality Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # POI Information
        story.extend(self._build_poi_info_section(analysis_data))
        story.append(Spacer(1, 0.3*inch))
        
        # Quality Score (prominent)
        story.extend(self._build_quality_score_section(analysis_data))
        story.append(Spacer(1, 0.3*inch))
        
        # Metrics Table
        story.extend(self._build_metrics_section(analysis_data))
        story.append(Spacer(1, 0.3*inch))
        
        # Visualization
        if 'satellite_image' in analysis_data:
            story.extend(self._build_visualization_section(analysis_data))
            story.append(Spacer(1, 0.3*inch))
        
        # Suggestions
        story.extend(self._build_suggestions_section(analysis_data))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | POI Blueprint Quality Inspector",
            self.styles['MetricLabel']
        ))
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def _build_poi_info_section(self, data: Dict) -> List:
        """Build POI information section."""
        elements = []
        
        elements.append(Paragraph("POI Information", self.styles['SectionHeader']))
        
        info_data = [
            ['POI ID:', data.get('poi_id', 'N/A')],
            ['Name:', data.get('metadata', {}).get('name', 'N/A')],
            ['Address:', data.get('metadata', {}).get('address', 'N/A')],
            ['Analysis Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        table = Table(info_data, colWidths=[1.5*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _build_quality_score_section(self, data: Dict) -> List:
        """Build quality score section."""
        elements = []
        
        score = data.get('quality_score', 0)
        grade = data.get('quality_grade', 'F')
        status = data.get('quality_status', {})
        
        elements.append(Paragraph("Overall Quality Score", self.styles['SectionHeader']))
        
        # Create score display
        score_data = [
            [f"{score}/100", grade, status.get('status', 'Unknown')],
            ['Score', 'Grade', 'Status']
        ]
        
        table = Table(score_data, colWidths=[2*inch, 2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 20),
            ('FONTSIZE', (0, 1), (-1, 1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(status.get('color', '#6b7280'))),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#6b7280')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#e5e7eb')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f9fafb')),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(
            status.get('description', ''),
            self.styles['Normal']
        ))
        
        return elements
    
    def _build_metrics_section(self, data: Dict) -> List:
        """Build metrics table section."""
        elements = []
        
        elements.append(Paragraph("Detailed Metrics", self.styles['SectionHeader']))
        
        metrics = data.get('metrics', {})
        
        metrics_data = [
            ['Metric', 'Value', 'Status'],
            ['IOU (Intersection over Union)', f"{metrics.get('iou', 0):.2%}", ''],
            ['Leakage Percentage', f"{metrics.get('leakage_percentage', 0):.1f}%", ''],
            ['Coverage Percentage', f"{metrics.get('coverage_percentage', 0):.1f}%", ''],
            ['Regularity Score', f"{metrics.get('regularity_score', 0):.1f}/100", ''],
            ['Road Overlap', f"{metrics.get('road_overlap_percentage', 0):.1f}%", ''],
            ['Adjacent POI Overlaps', str(metrics.get('adjacent_overlap', {}).get('overlap_count', 0)), '']
        ]
        
        table = Table(metrics_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica'),
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
        ]))
        
        elements.append(table)
        
        return elements
    
    def _build_visualization_section(self, data: Dict) -> List:
        """Build visualization section with satellite image."""
        elements = []
        
        elements.append(Paragraph("Visual Analysis", self.styles['SectionHeader']))
        
        # This would include the satellite image with overlays
        # For now, placeholder
        elements.append(Paragraph(
            "Satellite imagery with polygon overlays would be displayed here.",
            self.styles['Normal']
        ))
        
        return elements
    
    def _build_suggestions_section(self, data: Dict) -> List:
        """Build suggestions section."""
        elements = []
        
        elements.append(Paragraph("Correction Suggestions", self.styles['SectionHeader']))
        
        suggestions = data.get('suggestions', [])
        
        if suggestions:
            for suggestion in suggestions:
                elements.append(Paragraph(f"• {suggestion}", self.styles['Normal']))
                elements.append(Spacer(1, 0.05*inch))
        else:
            elements.append(Paragraph("No suggestions - POI quality is excellent!", self.styles['Normal']))
        
        return elements
