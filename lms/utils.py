"""
Utility functions for Savoir+ LMS.
"""
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, blue, black
from django.utils.translation import gettext as _
from datetime import datetime


def generate_certificate_pdf(certificate):
    """Generate a beautifully designed certificate PDF."""
    buffer = BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=32,
        spaceAfter=30,
        textColor=blue,
        alignment=1,  # Center alignment
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=20,
        textColor=black,
        alignment=1,
        fontName='Helvetica'
    )
    
    name_style = ParagraphStyle(
        'CustomName',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=20,
        textColor=blue,
        alignment=1,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=14,
        spaceAfter=12,
        alignment=1,
        fontName='Helvetica'
    )
    
    # Certificate content
    elements.append(Spacer(1, 50))
    
    # Title
    title = Paragraph("CERTIFICATE OF COMPLETION", title_style)
    elements.append(title)
    elements.append(Spacer(1, 30))
    
    # Subtitle
    subtitle = Paragraph("This is to certify that", subtitle_style)
    elements.append(subtitle)
    elements.append(Spacer(1, 20))
    
    # User name
    user_name = Paragraph(f"{certificate.user.get_full_name() or certificate.user.username}", name_style)
    elements.append(user_name)
    elements.append(Spacer(1, 30))
    
    # Course completion text
    completion_text = Paragraph(
        f"has successfully completed the course<br/><strong>{certificate.room.title}</strong>",
        body_style
    )
    elements.append(completion_text)
    elements.append(Spacer(1, 30))
    
    # Date and certificate ID
    date_text = Paragraph(
        f"Issued on {certificate.issued_at.strftime('%B %d, %Y')}<br/>"
        f"Certificate ID: {certificate.certificate_id}",
        body_style
    )
    elements.append(date_text)
    elements.append(Spacer(1, 50))
    
    # Signature line
    signature_style = ParagraphStyle(
        'Signature',
        parent=styles['Normal'],
        fontSize=12,
        alignment=1,
        fontName='Helvetica'
    )
    
    signature = Paragraph("Savoir+ Learning Management System", signature_style)
    elements.append(signature)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and return it
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


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
