"""
Ticket PDF generator using ReportLab.
"""

import base64
import logging
from io import BytesIO

import qrcode
import requests
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.platypus import (
    HRFlowable,
    Image as RLImage,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from events.kpl_team_logos import enrich_match_data_logos

logger = logging.getLogger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _qr_image_buffer(data: str, fill_color: str = "#000000") -> BytesIO:
    """Return a BytesIO PNG of the QR code."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def _fetch_image_buffer(url: str | None, timeout: int = 8) -> BytesIO | None:
    """Fetch a remote image and return a BytesIO PNG, or None on failure."""
    if not url or not url.startswith(("http://", "https://")):
        return None
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "brightpassticket/1.0"})
        r.raise_for_status()
        img = PILImage.open(BytesIO(r.content)).convert("RGBA")
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf
    except Exception as exc:
        logger.debug("Could not fetch image %s: %s", url, exc)
        return None


def _format_datetime(dt) -> tuple[str, str]:
    """Return (date_str, time_str) from a datetime object."""
    if not dt:
        return "Date TBA", "Time TBA"
    try:
        from django.utils import timezone
        # Convert to local time if timezone-aware
        if timezone.is_aware(dt):
            from django.conf import settings
            import zoneinfo
            tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)
            dt = dt.astimezone(tz)
        return dt.strftime("%A, %d %B %Y"), dt.strftime("%I:%M %p")
    except Exception:
        return str(dt.date()), str(dt.time())


def _is_sports_event(event) -> bool:
    if not getattr(event.category, "slug", None):
        return False
    if event.category.slug != "sports":
        return False
    md = event.match_data if isinstance(event.match_data, dict) else {}
    return bool(md.get("home_team") and md.get("away_team"))


# ── PDF builder ───────────────────────────────────────────────────────────────

def generate_ticket_pdf(ticket) -> bytes:
    booking = ticket.booking
    event = booking.event
    tier = ticket.ticket_tier

    qr_payload = ticket.qr_code_data or ticket.ticket_number
    is_sports = _is_sports_event(event)
    accent = "#059669" if is_sports else "#1e40af"  # green for sports, blue otherwise

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Styles ────────────────────────────────────────────────────────────────
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=20,
                        textColor=accent, alignment=TA_CENTER, spaceAfter=4)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14,
                        textColor=accent, alignment=TA_CENTER, spaceAfter=4)
    body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=11, spaceAfter=6)
    label = ParagraphStyle("Label", parent=styles["Normal"], fontSize=9,
                           textColor="#666666", spaceAfter=2)
    center = ParagraphStyle("Center", parent=styles["Normal"], fontSize=11,
                            alignment=TA_CENTER, spaceAfter=6)
    mono = ParagraphStyle("Mono", parent=styles["Normal"], fontSize=13,
                          fontName="Courier-Bold", alignment=TA_CENTER, spaceAfter=4)

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph("BrightPass", h1))
    story.append(Paragraph("E-TICKET", h2))
    story.append(HRFlowable(width="100%", thickness=2, color=accent, spaceAfter=12))

    # ── Sports match header ───────────────────────────────────────────────────
    if is_sports:
        md = enrich_match_data_logos(dict(event.match_data))
        home = md.get("home_team", "")
        away = md.get("away_team", "")
        home_logo_buf = _fetch_image_buffer(md.get("home_team_logo"))
        away_logo_buf = _fetch_image_buffer(md.get("away_team_logo"))

        logo_size = 2.5 * cm
        home_cell = RLImage(home_logo_buf, width=logo_size, height=logo_size) if home_logo_buf else Paragraph(home[0] if home else "?", h1)
        away_cell = RLImage(away_logo_buf, width=logo_size, height=logo_size) if away_logo_buf else Paragraph(away[0] if away else "?", h1)

        match_table = Table(
            [[home_cell, Paragraph("VS", h1), away_cell]],
            colWidths=["40%", "20%", "40%"],
        )
        match_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(match_table)

        name_table = Table(
            [[Paragraph(f"<b>{home}</b>", center), Paragraph("", center), Paragraph(f"<b>{away}</b>", center)]],
            colWidths=["40%", "20%", "40%"],
        )
        name_table.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
        story.append(name_table)
        story.append(Spacer(1, 0.3 * cm))

    # ── Event info ────────────────────────────────────────────────────────────
    story.append(Paragraph(f"<b>{event.title}</b>", center))
    if event.subtitle:
        story.append(Paragraph(event.subtitle, center))

    date_str, time_str = _format_datetime(event.start_datetime)
    venue_name = event.venue.name if event.venue else "Venue TBA"
    venue_city = event.venue.city if event.venue else ""

    info_data = [
        ["📅 Date", date_str],
        ["🕐 Time", time_str],
        ["📍 Venue", f"{venue_name}{', ' + venue_city if venue_city else ''}"],
        ["🎫 Ticket Type", tier.name],
        ["💰 Price Paid", f"KES {ticket.price_paid:,.0f}"],
    ]

    if is_sports:
        md = event.match_data if isinstance(event.match_data, dict) else {}
        stadium = md.get("stadium") or venue_name
        info_data.insert(2, ["🏟️ Stadium", stadium])

    info_table = Table(info_data, colWidths=["35%", "65%"])
    info_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor(accent)),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#f9fafb"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.4 * cm))

    # ── Attendee info ─────────────────────────────────────────────────────────
    attendee_name = ticket.attendee_name or booking.contact_name or "N/A"
    attendee_email = ticket.attendee_email or booking.contact_email or ""

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb"), spaceAfter=8))
    story.append(Paragraph("<b>ATTENDEE</b>", label))
    story.append(Paragraph(attendee_name, body))
    if attendee_email:
        story.append(Paragraph(attendee_email, label))
    story.append(Spacer(1, 0.3 * cm))

    # ── QR code ───────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb"), spaceAfter=8))
    story.append(Paragraph("<b>SCAN TO ENTER</b>", label))

    qr_buf = _qr_image_buffer(qr_payload, fill_color=accent)
    qr_img = RLImage(qr_buf, width=4 * cm, height=4 * cm)
    qr_img.hAlign = "CENTER"
    story.append(qr_img)
    story.append(Spacer(1, 0.2 * cm))

    # Ticket number in monospace
    story.append(Paragraph(ticket.ticket_number, mono))

    # Security code if available
    if ticket.security_code:
        story.append(Paragraph(f"Security Code: {ticket.security_code}", label))

    story.append(Spacer(1, 0.4 * cm))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb"), spaceAfter=6))
    story.append(Paragraph(
        "Present this QR code at the venue entrance. This ticket is non-transferable.",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8,
                       textColor="#9ca3af", alignment=TA_CENTER)
    ))
    story.append(Paragraph(
        f"Booking ref: {booking.booking_number}  |  brightpassticket.web.app",
        ParagraphStyle("Footer2", parent=styles["Normal"], fontSize=8,
                       textColor="#9ca3af", alignment=TA_CENTER)
    ))

    doc.build(story)
    return buf.getvalue()
