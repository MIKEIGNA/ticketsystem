"""
Modern Ticket PDF Generator
Generates beautiful, impressive tickets with QR codes
"""

import qrcode
import base64
from io import BytesIO
from django.template.loader import render_to_string
from django.conf import settings
from xhtml2pdf import pisa


def generate_ticket_pdf(ticket):
    """Generate a modern, impressive PDF ticket"""
    
    booking = ticket.booking
    event = booking.event
    tier = ticket.ticket_tier
    
    # Generate QR code as base64
    qr_buffer = BytesIO()
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(ticket.qr_code_data or ticket.ticket_number)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="#1e40af", back_color="white")
    qr_img.save(qr_buffer, format='PNG')
    qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()
    
    # Prepare context for template
    context = {
        'ticket': ticket,
        'booking': booking,
        'event': event,
        'tier': tier,
        'qr_base64': qr_base64,
        'venue': event.venue,
        'attendee_name': ticket.attendee_name or booking.contact_name,
        'attendee_email': ticket.attendee_email or booking.contact_email,
        'attendee_phone': ticket.attendee_phone or booking.contact_phone,
    }
    
    # Render HTML
    html_string = render_to_string('bookings/ticket_template.html', context)
    
    # Generate PDF using xhtml2pdf
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
    
    if pdf.err:
        raise Exception(f"PDF generation error: {pdf.err}")
    
    return result.getvalue()
