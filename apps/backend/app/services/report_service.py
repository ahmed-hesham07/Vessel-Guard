"""
Advanced report generation service for professional PDF reports.

This service provides comprehensive PDF report generation with
professional templates, engineering calculations, and compliance documentation.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import jinja2
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

from sqlalchemy.orm import Session
from app.db.models.calculation import Calculation
from app.db.models.vessel import Vessel
from app.db.models.project import Project
from app.db.models.user import User
from app.db.models.inspection import Inspection, InspectionFinding
from app.core.config import settings


class ReportService:
    """Service for generating professional engineering reports."""
    
    def __init__(self, db: Session):
        self.db = db
        self.template_dir = Path(__file__).parent.parent / "templates" / "reports"
        self.output_dir = Path(settings.STATIC_FILES_DIR) / "reports"
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_calculation_report(self, calculation_id: int, user_id: int) -> str:
        """Generate comprehensive calculation report in PDF format."""
        calculation = self.db.query(Calculation).filter(Calculation.id == calculation_id).first()
        if not calculation:
            raise ValueError("Calculation not found")
        
        vessel = self.db.query(Vessel).filter(Vessel.id == calculation.vessel_id).first()
        project = self.db.query(Project).filter(Project.id == calculation.project_id).first()
        user = self.db.query(User).filter(User.id == user_id).first()
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"calculation_{calculation_id}_{timestamp}.pdf"
        filepath = self.output_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build story (content)
        story = []
        styles = getSampleStyleSheet()
        
        # Add custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#1f2937')
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=HexColor('#374151')
        )
        
        # Title page
        story.append(Paragraph("Vessel Guard Engineering Report", title_style))
        story.append(Spacer(1, 20))
        
        # Project and vessel information
        if project:
            story.append(Paragraph(f"Project: {project.name}", styles['Normal']))
        if vessel:
            story.append(Paragraph(f"Vessel: {vessel.tag_number} - {vessel.name}", styles['Normal']))
        story.append(Paragraph(f"Calculation: {calculation.name}", styles['Normal']))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Paragraph(f"Engineer: {user.full_name if user else 'Unknown'}", styles['Normal']))
        
        story.append(PageBreak())
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        summary_text = f"This report presents the engineering analysis for {calculation.name}. "
        if calculation.output_parameters:
            if 'safety_factor' in calculation.output_parameters:
                sf = calculation.output_parameters['safety_factor']
                summary_text += f"The calculated safety factor is {sf:.2f}. "
            if 'compliance_status' in calculation.output_parameters:
                status = calculation.output_parameters['compliance_status']
                summary_text += f"The analysis indicates {status} compliance. "
        story.append(Paragraph(summary_text, styles['Normal']))
        
        story.append(Spacer(1, 12))
        
        # Input Parameters
        story.append(Paragraph("Input Parameters", heading_style))
        if calculation.input_parameters:
            input_data = []
            for key, value in calculation.input_parameters.items():
                if isinstance(value, (int, float)):
                    formatted_value = f"{value:.4f}" if isinstance(value, float) else str(value)
                else:
                    formatted_value = str(value)
                input_data.append([key.replace('_', ' ').title(), formatted_value])
            
            input_table = Table(input_data, colWidths=[2.5*inch, 3.5*inch])
            input_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#1e293b')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e5e7eb'))
            ]))
            story.append(input_table)
        
        story.append(Spacer(1, 12))
        
        # Results
        story.append(Paragraph("Calculation Results", heading_style))
        if calculation.output_parameters:
            results_data = []
            for key, value in calculation.output_parameters.items():
                if isinstance(value, (int, float)):
                    formatted_value = f"{value:.4f}" if isinstance(value, float) else str(value)
                else:
                    formatted_value = str(value)
                results_data.append([key.replace('_', ' ').title(), formatted_value])
            
            results_table = Table(results_data, colWidths=[2.5*inch, 3.5*inch])
            results_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#f0f9ff')),
                ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#1e293b')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#0ea5e9'))
            ]))
            story.append(results_table)
        
        story.append(Spacer(1, 12))
        
        # Engineering Analysis
        story.append(Paragraph("Engineering Analysis", heading_style))
        analysis_text = self._generate_engineering_analysis(calculation)
        story.append(Paragraph(analysis_text, styles['Normal']))
        
        story.append(Spacer(1, 12))
        
        # Compliance Statement
        story.append(Paragraph("Compliance Statement", heading_style))
        compliance_text = self._generate_compliance_statement(calculation)
        story.append(Paragraph(compliance_text, styles['Normal']))
        
        story.append(Spacer(1, 12))
        
        # Recommendations
        story.append(Paragraph("Recommendations", heading_style))
        recommendations = self._generate_recommendations(calculation)
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", styles['Normal']))
            story.append(Spacer(1, 6))
        
        # Build PDF
        doc.build(story)
        
        return str(filepath)
    
    def generate_inspection_report(self, inspection_id: int, user_id: int) -> str:
        """Generate comprehensive inspection report in PDF format."""
        inspection = self.db.query(Inspection).filter(Inspection.id == inspection_id).first()
        if not inspection:
            raise ValueError("Inspection not found")
        
        vessel = self.db.query(Vessel).filter(Vessel.id == inspection.vessel_id).first()
        inspector = self.db.query(User).filter(User.id == inspection.inspector_id).first()
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"inspection_{inspection_id}_{timestamp}.pdf"
        filepath = self.output_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build story (content)
        story = []
        styles = getSampleStyleSheet()
        
        # Add custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#1f2937')
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=HexColor('#374151')
        )
        
        # Title page
        story.append(Paragraph("Vessel Guard Technical Inspection Report", title_style))
        story.append(Spacer(1, 20))
        
        # Report header information
        story.append(Paragraph(f"Inspection Number: {inspection.inspection_number or 'N/A'}", styles['Normal']))
        story.append(Paragraph(f"Inspection Type: {inspection.inspection_type.value if hasattr(inspection.inspection_type, 'value') else inspection.inspection_type}", styles['Normal']))
        if vessel:
            story.append(Paragraph(f"Vessel: {vessel.tag_number} - {vessel.name}", styles['Normal']))
        story.append(Paragraph(f"Inspection Date: {inspection.scheduled_date.strftime('%B %d, %Y') if inspection.scheduled_date else 'N/A'}", styles['Normal']))
        if inspector:
            story.append(Paragraph(f"Inspector: {inspector.full_name}", styles['Normal']))
        story.append(Paragraph(f"Report Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        
        story.append(PageBreak())
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        summary_text = f"This technical inspection report presents the findings from the {inspection.inspection_type.value if hasattr(inspection.inspection_type, 'value') else inspection.inspection_type} inspection. "
        if inspection.overall_result:
            summary_text += f"The overall assessment indicates {inspection.overall_result.value if hasattr(inspection.overall_result, 'value') else inspection.overall_result} condition. "
        if inspection.findings:
            summary_text += f"The inspection identified {len(inspection.findings)} findings requiring attention. "
        story.append(Paragraph(summary_text, styles['Normal']))
        
        story.append(Spacer(1, 12))
        
        # Inspection Details
        story.append(Paragraph("Inspection Details", heading_style))
        
        details_data = [
            ["Inspection Type", inspection.inspection_type.value if hasattr(inspection.inspection_type, 'value') else inspection.inspection_type],
            ["Scheduled Date", inspection.scheduled_date.strftime('%B %d, %Y') if inspection.scheduled_date else 'N/A'],
            ["Actual Start Date", inspection.actual_start_date.strftime('%B %d, %Y') if inspection.actual_start_date else 'N/A'],
            ["Actual Completion Date", inspection.actual_completion_date.strftime('%B %d, %Y') if inspection.actual_completion_date else 'N/A'],
            ["Status", inspection.status.value if hasattr(inspection.status, 'value') else inspection.status],
            ["Overall Result", inspection.overall_result.value if hasattr(inspection.overall_result, 'value') else inspection.overall_result or 'N/A'],
            ["Vessel Condition", inspection.vessel_condition or 'N/A'],
            ["Operating Pressure", f"{inspection.operating_pressure} psi" if inspection.operating_pressure else 'N/A'],
            ["Operating Temperature", f"{inspection.operating_temperature}°F" if inspection.operating_temperature else 'N/A'],
        ]
        
        details_table = Table(details_data, colWidths=[2.5*inch, 3.5*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#1e293b')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e5e7eb'))
        ]))
        story.append(details_table)
        
        story.append(Spacer(1, 12))
        
        # Inspection Methods
        story.append(Paragraph("Inspection Methods", heading_style))
        if inspection.inspection_methods:
            methods_text = "The following inspection methods were employed: "
            methods_list = []
            for method in inspection.inspection_methods:
                if isinstance(method, dict):
                    methods_list.append(method.get('method', str(method)))
                else:
                    methods_list.append(str(method))
            methods_text += ", ".join(methods_list) + "."
            story.append(Paragraph(methods_text, styles['Normal']))
        
        story.append(Spacer(1, 12))
        
        # Findings
        story.append(Paragraph("Inspection Findings", heading_style))
        if inspection.findings:
            story.append(Paragraph(inspection.findings, styles['Normal']))
        
        # Detailed findings table
        if inspection.findings:
            findings = self.db.query(InspectionFinding).filter(InspectionFinding.inspection_id == inspection.id).all()
            if findings:
                findings_data = [["Finding", "Location", "Severity", "Status", "Description"]]
                for finding in findings:
                    findings_data.append([
                        finding.finding_number or 'N/A',
                        finding.location,
                        finding.severity.value if hasattr(finding.severity, 'value') else finding.severity,
                        finding.status,
                        finding.description[:50] + "..." if len(finding.description) > 50 else finding.description
                    ])
                
                findings_table = Table(findings_data, colWidths=[0.8*inch, 1.2*inch, 0.8*inch, 0.8*inch, 2.4*inch])
                findings_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1e293b')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
                    ('TEXTCOLOR', (0, 1), (-1, -1), HexColor('#1e293b')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e5e7eb'))
                ]))
                story.append(findings_table)
        
        story.append(Spacer(1, 12))
        
        # Measurements
        if inspection.thickness_measurements:
            story.append(Paragraph("Thickness Measurements", heading_style))
            measurements_text = "The following thickness measurements were recorded: "
            story.append(Paragraph(measurements_text, styles['Normal']))
            
            # Create measurements table
            measurements_data = [["Location", "Thickness (inches)", "Date"]]
            for measurement in inspection.thickness_measurements:
                if isinstance(measurement, dict):
                    measurements_data.append([
                        measurement.get('location', 'N/A'),
                        f"{measurement.get('thickness', 0):.4f}",
                        measurement.get('date', 'N/A')
                    ])
            
            measurements_table = Table(measurements_data, colWidths=[2*inch, 2*inch, 2*inch])
            measurements_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f0f9ff')),
                ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#1e293b')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#0ea5e9'))
            ]))
            story.append(measurements_table)
        
        story.append(Spacer(1, 12))
        
        # Recommendations
        story.append(Paragraph("Recommendations", heading_style))
        if inspection.recommendations:
            story.append(Paragraph(inspection.recommendations, styles['Normal']))
        
        # Generate recommendations based on findings
        recommendations = self._generate_inspection_recommendations(inspection)
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", styles['Normal']))
            story.append(Spacer(1, 6))
        
        story.append(Spacer(1, 12))
        
        # Compliance Assessment
        story.append(Paragraph("Compliance Assessment", heading_style))
        compliance_text = self._generate_inspection_compliance_assessment(inspection)
        story.append(Paragraph(compliance_text, styles['Normal']))
        
        story.append(Spacer(1, 12))
        
        # Next Inspection
        story.append(Paragraph("Next Inspection", heading_style))
        if inspection.recommended_next_inspection:
            next_inspection_text = f"Recommended next inspection date: {inspection.recommended_next_inspection.strftime('%B %d, %Y')}"
            if inspection.inspection_interval_months:
                next_inspection_text += f" (Interval: {inspection.inspection_interval_months} months)"
            story.append(Paragraph(next_inspection_text, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        return str(filepath)
    
    def generate_project_summary_report(self, project_id: int, user_id: int) -> str:
        """Generate project summary report in PDF format."""
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from datetime import datetime
        import tempfile
        import os
        
        # Get project data
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        # Get associated data
        vessels = self.db.query(Vessel).filter(Vessel.project_id == project_id).all()
        calculations = self.db.query(Calculation).filter(Calculation.project_id == project_id).all()
        inspections = self.db.query(Inspection).join(Vessel).filter(Vessel.project_id == project_id).all()
        
        # Create temporary file
        temp_dir = os.path.join(os.getcwd(), "temp_reports")
        os.makedirs(temp_dir, exist_ok=True)
        filename = f"project_summary_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(temp_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(str(filepath), pagesize=letter, topMargin=1*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.darkblue,
            spaceBefore=20,
            spaceAfter=10
        )
        
        # Title
        story.append(Paragraph(f"Project Summary Report", title_style))
        story.append(Paragraph(f"{project.name}", styles['Heading1']))
        story.append(Spacer(1, 20))
        
        # Project Information
        story.append(Paragraph("Project Information", heading_style))
        project_data = [
            ["Project Name:", project.name],
            ["Description:", project.description or "N/A"],
            ["Status:", project.status.value if project.status else "N/A"],
            ["Created:", project.created_at.strftime("%Y-%m-%d") if project.created_at else "N/A"],
            ["Organization:", project.organization.name if project.organization else "N/A"]
        ]
        
        project_table = Table(project_data, colWidths=[2*inch, 4*inch])
        project_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ]))
        story.append(project_table)
        story.append(Spacer(1, 20))
        
        # Vessels Summary
        story.append(Paragraph("Vessels Summary", heading_style))
        if vessels:
            vessel_data = [["Tag Number", "Type", "Design Pressure", "Design Temperature", "Material"]]
            for vessel in vessels:
                vessel_data.append([
                    vessel.tag_number or "N/A",
                    vessel.vessel_type.value if vessel.vessel_type else "N/A",
                    f"{vessel.design_pressure or 0} {vessel.pressure_unit or 'psi'}",
                    f"{vessel.design_temperature or 0} {vessel.temperature_unit or '°F'}",
                    vessel.material or "N/A"
                ])
            
            vessel_table = Table(vessel_data, colWidths=[1.2*inch, 1*inch, 1.3*inch, 1.3*inch, 1.2*inch])
            vessel_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            story.append(vessel_table)
        else:
            story.append(Paragraph("No vessels found for this project.", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Calculations Summary
        story.append(Paragraph("Engineering Calculations Summary", heading_style))
        if calculations:
            calc_data = [["Calculation Type", "Status", "Safety Factor", "Created Date"]]
            for calc in calculations:
                safety_factor = "N/A"
                if calc.output_parameters and 'safety_factor' in calc.output_parameters:
                    safety_factor = f"{calc.output_parameters['safety_factor']:.2f}"
                
                calc_data.append([
                    calc.calculation_type or "N/A",
                    calc.status.value if calc.status else "N/A",
                    safety_factor,
                    calc.created_at.strftime("%Y-%m-%d") if calc.created_at else "N/A"
                ])
            
            calc_table = Table(calc_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1.5*inch])
            calc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            story.append(calc_table)
        else:
            story.append(Paragraph("No calculations found for this project.", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Inspections Summary
        story.append(Paragraph("Inspections Summary", heading_style))
        if inspections:
            insp_data = [["Vessel", "Inspection Type", "Status", "Date", "Next Due"]]
            for insp in inspections:
                next_due = "N/A"
                if insp.next_inspection_date:
                    next_due = insp.next_inspection_date.strftime("%Y-%m-%d")
                
                insp_data.append([
                    insp.vessel.tag_number if insp.vessel else "N/A",
                    insp.inspection_type.value if insp.inspection_type else "N/A",
                    insp.status.value if insp.status else "N/A",
                    insp.inspection_date.strftime("%Y-%m-%d") if insp.inspection_date else "N/A",
                    next_due
                ])
            
            insp_table = Table(insp_data, colWidths=[1.2*inch, 1.3*inch, 1*inch, 1*inch, 1.5*inch])
            insp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkorange),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            story.append(insp_table)
        else:
            story.append(Paragraph("No inspections found for this project.", styles['Normal']))
        
        # Footer
        story.append(PageBreak())
        story.append(Spacer(1, 100))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
        story.append(Paragraph("Vessel Guard Engineering Platform", footer_style))
        
        # Build PDF
        doc.build(story)
        
        return str(filepath)
    
    def _generate_engineering_analysis(self, calculation: Calculation) -> str:
        """Generate engineering analysis text based on calculation results."""
        analysis = f"The engineering analysis was performed using {calculation.calculation_type} standards. "
        
        if calculation.output_parameters:
            if 'safety_factor' in calculation.output_parameters:
                sf = calculation.output_parameters['safety_factor']
                analysis += f"The calculated safety factor is {sf:.2f}, which "
                if sf >= 3.5:
                    analysis += "meets ASME requirements for pressure vessels."
                elif sf >= 2.0:
                    analysis += "provides adequate safety margins."
                else:
                    analysis += "requires additional analysis or design modifications."
            
            if 'required_thickness' in calculation.output_parameters:
                thickness = calculation.output_parameters['required_thickness']
                analysis += f" The minimum required thickness is {thickness:.4f} inches."
            
            if 'fitness_rating' in calculation.output_parameters:
                rating = calculation.output_parameters['fitness_rating']
                analysis += f" The fitness-for-service assessment indicates a '{rating}' rating."
        
        return analysis
    
    def _generate_compliance_statement(self, calculation: Calculation) -> str:
        """Generate compliance statement based on calculation type."""
        if calculation.calculation_type.startswith('ASME'):
            return f"This calculation complies with {calculation.calculation_type} American Society of Mechanical Engineers standards. " \
                   "The analysis follows the applicable ASME Boiler and Pressure Vessel Code requirements."
        elif calculation.calculation_type.startswith('EN'):
            return f"This calculation complies with {calculation.calculation_type} European standards. " \
                   "The analysis follows the harmonized European approach to pressure equipment design."
        else:
            return "This calculation follows standard engineering practices and applicable codes and standards."
    
    def _generate_recommendations(self, calculation: Calculation) -> List[str]:
        """Generate recommendations based on calculation results."""
        recommendations = []
        
        if calculation.output_parameters:
            if 'safety_factor' in calculation.output_parameters:
                sf = calculation.output_parameters['safety_factor']
                if sf < 2.0:
                    recommendations.append("Consider design modifications to increase safety factor.")
                elif sf < 3.5:
                    recommendations.append("Monitor operating conditions and consider additional analysis.")
            
            if 'fitness_rating' in calculation.output_parameters:
                rating = calculation.output_parameters['fitness_rating']
                if rating == 'monitor':
                    recommendations.append("Increase inspection frequency and monitor corrosion rates.")
                elif rating == 'repair':
                    recommendations.append("Plan repair or replacement within recommended timeframe.")
                elif rating == 'replace':
                    recommendations.append("Immediate replacement or repair required.")
            
            if 'remaining_life' in calculation.output_parameters:
                life = calculation.output_parameters['remaining_life']
                if life != "Indefinite" and life < 5:
                    recommendations.append(f"Plan for replacement within {life} years.")
        
        recommendations.append("Maintain proper documentation and inspection records.")
        recommendations.append("Follow applicable codes and standards for continued operation.")
        
        return recommendations
    
    def _generate_inspection_recommendations(self, inspection: Inspection) -> List[str]:
        """Generate recommendations based on inspection findings."""
        recommendations = []
        
        if inspection.overall_result:
            result = inspection.overall_result.value if hasattr(inspection.overall_result, 'value') else inspection.overall_result
            if result == 'requires_repair':
                recommendations.append("Schedule repair activities as soon as possible.")
                recommendations.append("Consider reducing operating pressure until repairs are completed.")
            elif result == 'requires_replacement':
                recommendations.append("Immediate replacement is required.")
                recommendations.append("Do not operate the vessel until replacement is completed.")
            elif result == 'acceptable_with_conditions':
                recommendations.append("Monitor the vessel closely and implement recommended actions.")
                recommendations.append("Increase inspection frequency.")
        
        # Add recommendations based on findings
        if inspection.findings:
            findings = self.db.query(InspectionFinding).filter(InspectionFinding.inspection_id == inspection.id).all()
            critical_findings = [f for f in findings if (hasattr(f.severity, 'value') and f.severity.value == 'critical') or (not hasattr(f.severity, 'value') and f.severity == 'critical')]
            if critical_findings:
                recommendations.append(f"Address {len(critical_findings)} critical findings immediately.")
        
        recommendations.append("Maintain detailed records of all inspection activities.")
        recommendations.append("Follow the recommended inspection interval for future inspections.")
        
        return recommendations
    
    def _generate_inspection_compliance_assessment(self, inspection: Inspection) -> str:
        """Generate compliance assessment for inspection."""
        assessment = f"The inspection was conducted in accordance with applicable standards and procedures. "
        
        if inspection.overall_result:
            result = inspection.overall_result.value if hasattr(inspection.overall_result, 'value') else inspection.overall_result
            if result == 'satisfactory':
                assessment += "The vessel is compliant with operational requirements and may continue in service."
            elif result == 'acceptable_with_conditions':
                assessment += "The vessel is conditionally compliant and may continue in service with monitoring."
            elif result == 'requires_repair':
                assessment += "The vessel requires repair before returning to service."
            elif result == 'requires_replacement':
                assessment += "The vessel requires replacement and should not be operated."
        
        if inspection.applicable_standards:
            assessment += f" The inspection was conducted in accordance with {', '.join(inspection.applicable_standards)}."
        
        return assessment
    
    def generate_custom_report(self, template_name: str, data: Dict[str, Any]) -> str:
        """Generate custom report using specified template."""
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from datetime import datetime
        import tempfile
        import os
        
        # Create temporary file
        temp_dir = os.path.join(os.getcwd(), "temp_reports")
        os.makedirs(temp_dir, exist_ok=True)
        filename = f"custom_report_{template_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(temp_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(str(filepath), pagesize=letter, topMargin=1*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=20,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        # Title based on template
        template_titles = {
            'vessel_inspection_report': 'Vessel Inspection Report',
            'calculation_summary': 'Engineering Calculation Summary',
            'compliance_report': 'Compliance Assessment Report',
            'safety_analysis': 'Safety Analysis Report',
            'maintenance_schedule': 'Maintenance Schedule Report',
            'audit_report': 'Audit and Review Report'
        }
        
        title = template_titles.get(template_name, f"Custom Report - {template_name.replace('_', ' ').title()}")
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 20))
        
        # Report metadata
        if 'metadata' in data:
            metadata = data['metadata']
            story.append(Paragraph("Report Information", styles['Heading2']))
            
            meta_data = []
            for key, value in metadata.items():
                formatted_key = key.replace('_', ' ').title()
                meta_data.append([f"{formatted_key}:", str(value)])
            
            if meta_data:
                meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
                meta_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                story.append(meta_table)
                story.append(Spacer(1, 20))
        
        # Main content sections
        if 'sections' in data:
            for section in data['sections']:
                if 'title' in section:
                    story.append(Paragraph(section['title'], styles['Heading2']))
                
                if 'content' in section:
                    story.append(Paragraph(section['content'], styles['Normal']))
                    story.append(Spacer(1, 10))
                
                if 'table_data' in section:
                    table_data = section['table_data']
                    if table_data and len(table_data) > 0:
                        # Create table with headers
                        table = Table(table_data)
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 10),
                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 1), (-1, -1), 9),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ]))
                        story.append(table)
                        story.append(Spacer(1, 15))
        
        # Summary and recommendations
        if 'summary' in data:
            story.append(Paragraph("Summary", styles['Heading2']))
            story.append(Paragraph(data['summary'], styles['Normal']))
            story.append(Spacer(1, 20))
        
        if 'recommendations' in data:
            story.append(Paragraph("Recommendations", styles['Heading2']))
            for i, recommendation in enumerate(data['recommendations'], 1):
                story.append(Paragraph(f"{i}. {recommendation}", styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
        story.append(Paragraph("Vessel Guard Engineering Platform", footer_style))
        
        # Build PDF
        doc.build(story)
        
        return str(filepath)
