"""
TheSportsDB REST API v2 client (X-API-KEY header).
Collection: TheSportsDB V2 API.postman_collection.json (baseUrl /schedule/*, /filter/tv/day/*).
"""

from __future__ import annotations

import logging
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

V2_BASE = "https://www.thesportsdb.com/api/v2/json"


def api_key() -> str:
    return (
        getattr(settings, "THESPORTSDB_V2_API_KEY", None)
        or getattr(settings, "THESPORTSDB_API_KEY", None)
        or "123"
    )


def _headers() -> dict[str, str]:
    return {
        "Accept": "application/json",
        "X-API-KEY": api_key(),
        "User-Agent": "brightpassticket/1.0 (TheSportsDB v2)",
    }


def _get(path: str) -> dict[str, Any]:
    url = f"{V2_BASE.rstrip('/')}/{path.lstrip('/')}"
    r = requests.get(url, headers=_headers(), timeout=45)
    r.raise_for_status()
    return r.json()


def fetch_schedule_league_season(league_id: str, season: str) -> list[dict[str, Any]]:
    """GET /schedule/league/:idLeague/:season — full season fixtures."""
    payload = _get(f"schedule/league/{league_id}/{season}")
    rows = payload.get("schedule")
    if not rows:
        return []
    return list(rows)


def fetch_schedule_next_league(league_id: str) -> list[dict[str, Any]]:
    """GET /schedule/next/league/:idLeague — next events (small batch)."""
    payload = _get(f"schedule/next/league/{league_id}")
    rows = payload.get("schedule")
    if not rows:
        return []
    return list(rows)


def fetch_schedule_previous_league(league_id: str) -> list[dict[str, Any]]:
    """GET /schedule/previous/league/:idLeague — recent past events (small batch)."""
    payload = _get(f"schedule/previous/league/{league_id}")
    rows = payload.get("schedule")
    if not rows:
        return []
    return list(rows)


def fetch_tv_day(date_yyyy_mm_dd: str) -> list[dict[str, Any]]:
    """GET /filter/tv/day/:date — TV listings (mixed sports); filter client-side for Soccer."""
    payload = _get(f"filter/tv/day/{date_yyyy_mm_dd}")
    rows = payload.get("filter")
    if not rows:
        return []
    return list(rows)
