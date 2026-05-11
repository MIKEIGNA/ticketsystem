"""
Ticket PDF generator — default layout plus sports / match pass layout.
"""

import base64
from io import BytesIO

import qrcode
import requests
from django.template.loader import render_to_string
from events.kpl_team_logos import enrich_match_data_logos
from PIL import Image
from weasyprint import HTML


def _qr_base64(data: str, fill_color: str, back_color: str = "white") -> str:
    buf = BytesIO()
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr.make_image(fill_color=fill_color, back_color=back_color).save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def fetch_image_as_data_uri(url: str | None, timeout: int = 8) -> str | None:
    if not url:
        return None
    
    # Handle local static files
    if url.startswith("/static/"):
        try:
            from django.conf import settings
            import os
            # Build absolute path from static URL
            static_path = url.replace("/static/", "")
            file_path = os.path.join(settings.BASE_DIR, "static", static_path)
            
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    content = f.read()
                img = Image.open(BytesIO(content)).convert("RGBA")
                out = BytesIO()
                img.save(out, format="PNG")
                b64 = base64.b64encode(out.getvalue()).decode()
                return f"data:image/png;base64,{b64}"
        except Exception:
            pass
        return None
    
    # Handle HTTP/HTTPS URLs
    if not url.startswith(("http://", "https://")):
        return None
    
    try:
        r = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "brightpassticket/1.0"},
        )
        r.raise_for_status()
        img = Image.open(BytesIO(r.content)).convert("RGBA")
        out = BytesIO()
        img.save(out, format="PNG")
        b64 = base64.b64encode(out.getvalue()).decode()
        return f"data:image/png;base64,{b64}"
    except (OSError, requests.RequestException, ValueError):
        return None


def _sports_match_context(event, tier, ticket, qr_base64: str):
    raw = event.match_data if isinstance(event.match_data, dict) else {}
    md = enrich_match_data_logos(dict(raw))
    branding = md.get("branding") or {}
    fkf = branding.get("fkf") or {}

    gate = md.get("gate") or "GATE A"
    if tier.seat_section:
        section_access = f"SECTION ACCESS: {tier.seat_section.upper()}"
    elif tier.name.lower() == "vip":
        section_access = "SECTION ACCESS: VIP MAIN STAND"
    else:
        section_access = f"SECTION ACCESS: {tier.name.upper()} — GENERAL"

    org = event.organizer
    organizer_display = (
        (org.get_full_name() or org.username or "Event organizer").strip().upper()
    )

    home_name = (md.get("home_team") or "").strip()
    away_name = (md.get("away_team") or "").strip()
    home_logo_uri = fetch_image_as_data_uri(md.get("home_team_logo"))
    away_logo_uri = fetch_image_as_data_uri(md.get("away_team_logo"))

    return {
        "gate_label": gate.upper() if isinstance(gate, str) else "GATE A",
        "section_access": section_access,
        "home_team": home_name,
        "away_team": away_name,
        "home_team_initial": (home_name[0].upper() if home_name else "?"),
        "away_team_initial": (away_name[0].upper() if away_name else "?"),
        "home_team_logo_data_uri": home_logo_uri,
        "away_team_logo_data_uri": away_logo_uri,
        "fkf_logo_data_uri": fetch_image_as_data_uri(fkf.get("logo")),
        "league_category": md.get("category") or "",
        "stadium_line": (md.get("stadium") or (event.venue.name if event.venue else None) or "Venue TBA").upper(),
        "organizer_display": organizer_display,
        "tier_admission_label": f"{tier.name.upper()} ADMISSION",
        "qr_base64": qr_base64,
    }


def _use_sports_template(event) -> bool:
    if not getattr(event.category, "slug", None):
        return False
    if event.category.slug != "sports":
        return False
    md = event.match_data if isinstance(event.match_data, dict) else {}
    return bool(md.get("home_team") and md.get("away_team"))


def generate_ticket_pdf(ticket):
    booking = ticket.booking
    event = booking.event
    tier = ticket.ticket_tier

    payload = ticket.qr_code_data or ticket.ticket_number
    use_sports = _use_sports_template(event)
    fill = "#000000" if use_sports else "#1e40af"
    qr_base64 = _qr_base64(payload, fill_color=fill)

    context = {
        "ticket": ticket,
        "booking": booking,
        "event": event,
        "tier": tier,
        "qr_base64": qr_base64,
        "venue": event.venue,
        "attendee_name": ticket.attendee_name or booking.contact_name,
        "attendee_email": ticket.attendee_email or booking.contact_email,
        "attendee_phone": ticket.attendee_phone or booking.contact_phone,
    }

    if use_sports:
        context.update(_sports_match_context(event, tier, ticket, qr_base64))
        template_name = "bookings/ticket_template_sports.html"
    else:
        template_name = "bookings/ticket_template.html"

    html_string = render_to_string(template_name, context)
    result = BytesIO()
    HTML(string=html_string).write_pdf(result)
    return result.getvalue()
