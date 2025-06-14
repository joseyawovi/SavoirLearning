"""
Utility functions for Savoir+ LMS.
"""
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from django.utils.translation import gettext as _


def generate_certificate_pdf(certificate):
    """Generate a PDF certificate for the user."""
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=HexColor('#2c3e50'),
        alignment=1  # Center alignment
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=20,
        textColor=HexColor('#34495e'),
        alignment=1
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=15,
        alignment=1
    )
    
    # Build content
    content = []
    
    # Title
    content.append(Paragraph("SAVOIR+", title_style))
    content.append(Spacer(1, 20))
    
    # Certificate title
    content.append(Paragraph(_("Certificate of Completion"), subtitle_style))
    content.append(Spacer(1, 30))
    
    # User info
    content.append(Paragraph(_("This is to certify that"), body_style))
    content.append(Spacer(1, 10))
    
    user_name_style = ParagraphStyle(
        'UserName',
        parent=styles['Normal'],
        fontSize=20,
        spaceAfter=20,
        textColor=HexColor('#e74c3c'),
        alignment=1,
        fontName='Helvetica-Bold'
    )
    
    full_name = f"{certificate.user.first_name} {certificate.user.last_name}".strip()
    if not full_name:
        full_name = certificate.user.username
    
    content.append(Paragraph(full_name, user_name_style))
    content.append(Spacer(1, 20))
    
    # Course info
    content.append(Paragraph(_("has successfully completed the course"), body_style))
    content.append(Spacer(1, 10))
    
    course_style = ParagraphStyle(
        'CourseName',
        parent=styles['Normal'],
        fontSize=16,
        spaceAfter=30,
        textColor=HexColor('#2980b9'),
        alignment=1,
        fontName='Helvetica-Bold'
    )
    
    content.append(Paragraph(certificate.room.title, course_style))
    content.append(Spacer(1, 40))
    
    # Date and certificate ID
    content.append(Paragraph(f"{_('Date')}: {certificate.issued_at.strftime('%B %d, %Y')}", body_style))
    content.append(Paragraph(f"{_('Certificate ID')}: {certificate.certificate_id}", body_style))
    content.append(Spacer(1, 20))
    
    # Verification info
    verification_style = ParagraphStyle(
        'Verification',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#7f8c8d'),
        alignment=1
    )
    
    content.append(Paragraph(
        _("This certificate can be verified at: savoirplus.com/verify/{certificate_id}").format(
            certificate_id=certificate.certificate_id
        ),
        verification_style
    ))
    
    # Build PDF
    doc.build(content)
    
    # Get PDF content
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content
