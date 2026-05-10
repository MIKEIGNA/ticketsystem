"""
Deterministic manual check-in code derived from the same payload encoded in the QR.

The QR holds `qr_code_data` (plain text). The security code is an HMAC-based digest
formatted for typing (XXXX-XXXX-XXXX-XXXX). It does not embed the payload; gate apps
look up the ticket by this code. It always matches the ticket row whose QR encodes
the same `qr_code_data`, so scanning and manual entry refer to one ticket.
"""

from __future__ import annotations

import hashlib
import hmac

from django.conf import settings


def _derived_hmac_key() -> bytes:
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        b"bookings.Ticket.security_code.v1",
        hashlib.sha256,
    ).digest()


def build_security_code(qr_code_data: str) -> str:
    if not qr_code_data:
        return ""
    digest = hmac.new(
        _derived_hmac_key(),
        qr_code_data.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    hex16 = digest[:16].upper()
    return "-".join(hex16[i : i + 4] for i in range(0, 16, 4))


def normalize_security_code(raw: str) -> str | None:
    """Return canonical dashed form or None if not 16 hex digits."""
    if not raw:
        return None
    alnum = "".join(c for c in raw.strip().upper() if c in "0123456789ABCDEF")
    if len(alnum) != 16:
        return None
    return "-".join(alnum[i : i + 4] for i in range(0, 16, 4))
