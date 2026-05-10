"""
Persist TheSportsDB v2 league schedule rows as Event records (KPL / configurable league).
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Callable

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify

from accounts.models import User
from events.kpl_team_logos import get_team_assets, kpl_league_branding
from events.models import Category, Event, TicketTier, Venue
from events.thesportsdb_v2_client import (
    fetch_schedule_league_season,
    fetch_schedule_next_league,
    fetch_schedule_previous_league,
)

logger = logging.getLogger(__name__)

LogFn = Callable[[str], None]


def _log(log: LogFn | None, msg: str) -> None:
    if log:
        log(msg)
    else:
        logger.info("%s", msg)


def default_football_season_label(now: datetime | None = None) -> str:
    """European-style season label e.g. 2025-2026 (Aug–May)."""
    now = now or timezone.now()
    y, m = now.year, now.month
    if m >= 8:
        return f"{y}-{y + 1}"
    return f"{y - 1}-{y}"


def _parse_start(row: dict[str, Any]) -> datetime | None:
    ts = row.get("strTimestamp")
    if ts and str(ts).strip():
        dt = parse_datetime(str(ts).strip().replace("Z", "+00:00"))
        if dt:
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt, timezone.utc)
            return dt
    de = (row.get("dateEvent") or "").strip()
    if not de:
        return None
    tm = (row.get("strTime") or "12:00:00").strip() or "12:00:00"
    if len(tm) == 5:
        tm = tm + ":00"
    try:
        naive = datetime.strptime(f"{de} {tm[:8]}", "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            naive = datetime.strptime(de, "%Y-%m-%d")
        except ValueError:
            return None
    return timezone.make_aware(naive, timezone.utc)


def _event_status(row: dict[str, Any]) -> str:
    if (row.get("strPostponed") or "").lower() == "yes":
        return "cancelled"
    st = (row.get("strStatus") or "").lower()
    if "finished" in st:
        return "completed"
    return "published"


def _venue_for_row(row: dict[str, Any]) -> Venue:
    name = (row.get("strVenue") or "").strip() or "Venue TBA"
    city = (row.get("strCity") or "").strip() or "Unknown"
    country = (row.get("strCountry") or "").strip() or "Kenya"
    venue, _ = Venue.objects.get_or_create(
        name=name,
        defaults={
            "address": name,
            "city": city,
            "country": country,
            "capacity": 10000,
            "is_active": True,
        },
    )
    return venue


def _match_data_from_row(row: dict[str, Any], league_id: str) -> dict[str, Any]:
    home = (row.get("strHomeTeam") or "").strip()
    away = (row.get("strAwayTeam") or "").strip()
    ha = get_team_assets(home) if home else {}
    aa = get_team_assets(away) if away else {}
    home_logo = (row.get("strHomeTeamBadge") or "").strip() or ha.get("logo", "")
    away_logo = (row.get("strAwayTeamBadge") or "").strip() or aa.get("logo", "")
    branding = {
        "fkf": {
            "name": "FKF Premier League",
            "logo": "https://footballkenya.org/wp-content/uploads/2023/02/fkf-logo.png",
            "colors": {"red": "#DC3232", "black": "#000000", "green": "#43A047"},
        },
        "sponsor": {
            "name": "SportPesa",
            "logo": "https://www.sportpesa.co.ke/assets/images/sportpesa-logo.png",
            "colors": {"primary": "#0059B3", "white": "#FFFFFF"},
        },
        "kpl": kpl_league_branding(),
    }
    return {
        "idEvent": str(row.get("idEvent") or ""),
        "idLeague": str(row.get("idLeague") or league_id),
        "strLeague": (row.get("strLeague") or "").strip(),
        "strSeason": (row.get("strSeason") or "").strip(),
        "match_id": f"v2-{row.get('idEvent')}",
        "home_team": home,
        "away_team": away,
        "home_team_logo": home_logo,
        "away_team_logo": away_logo,
        "home_team_primary_color": ha.get("primary_color", "#000000"),
        "home_team_secondary_color": ha.get("secondary_color", "#FFFFFF"),
        "away_team_primary_color": aa.get("primary_color", "#000000"),
        "away_team_secondary_color": aa.get("secondary_color", "#FFFFFF"),
        "category": "B",
        "stadium": (row.get("strVenue") or "").strip(),
        "strStatus": row.get("strStatus"),
        "strPostponed": row.get("strPostponed"),
        "intRound": row.get("intRound"),
        "intHomeScore": row.get("intHomeScore"),
        "intAwayScore": row.get("intAwayScore"),
        "branding": branding,
        "source": "thesportsdb_v2",
    }


def _description(row: dict[str, Any]) -> str:
    home = (row.get("strHomeTeam") or "").strip()
    away = (row.get("strAwayTeam") or "").strip()
    venue = (row.get("strVenue") or "").strip()
    rd = row.get("intRound")
    league = (row.get("strLeague") or "").strip()
    return f"""
<h2>{league or "Football"}</h2>
<p><strong>{home}</strong> vs <strong>{away}</strong></p>
<p>Venue: {venue or "TBA"}</p>
<p>Round: {rd}</p>
<p><em>Synced from TheSportsDB</em></p>
""".strip()


def _ensure_ticket_tiers(event: Event) -> None:
    qty_reg, qty_vip = 8000, 2000
    TicketTier.objects.get_or_create(
        event=event,
        name="Regular",
        defaults={
            "description": "Standard seating",
            "price": 200,
            "currency": "KES",
            "total_quantity": qty_reg,
            "available_quantity": qty_reg,
            "min_per_order": 1,
            "max_per_order": 10,
            "is_active": True,
            "order": 1,
            "benefits": ["Standard seating", "Access to match viewing"],
        },
    )
    TicketTier.objects.get_or_create(
        event=event,
        name="VIP",
        defaults={
            "description": "Premium seating",
            "price": 500,
            "currency": "KES",
            "total_quantity": qty_vip,
            "available_quantity": qty_vip,
            "min_per_order": 1,
            "max_per_order": 10,
            "is_active": True,
            "order": 0,
            "benefits": ["Premium seating", "Priority entry"],
        },
    )


def _get_organizer(organizer_id: str | None, log: LogFn | None) -> User | None:
    if organizer_id:
        try:
            return User.objects.get(id=organizer_id)
        except User.DoesNotExist:
            _log(log, f"Organizer {organizer_id} not found")
            return None
    return User.objects.filter(is_superuser=True).first()


def _fetch_rows(mode: str, league_id: str, season: str, log: LogFn | None) -> list[dict[str, Any]]:
    if mode == "full":
        _log(log, f"Fetching full schedule league={league_id} season={season}")
        return fetch_schedule_league_season(league_id, season)
    if mode == "incremental":
        _log(log, f"Fetching next+previous batches league={league_id}")
        merged: dict[str, dict[str, Any]] = {}
        for row in fetch_schedule_next_league(league_id):
            merged[str(row.get("idEvent"))] = row
        for row in fetch_schedule_previous_league(league_id):
            merged[str(row.get("idEvent"))] = row
        return list(merged.values())
    raise ValueError(f"Unknown mode {mode!r}")


def sync_kpl_v2_schedule(
    mode: str,
    *,
    league_id: str | None = None,
    season: str | None = None,
    organizer_id: str | None = None,
    log: LogFn | None = None,
) -> dict[str, int]:
    """
    mode: 'full' | 'incremental'
    Upserts Events keyed by match_data.idEvent.
    """
    league_id = league_id or getattr(settings, "THESPORTSDB_V2_LEAGUE_ID", "4745")
    cfg_season = (getattr(settings, "THESPORTSDB_V2_SEASON", "") or "").strip()
    season = season or (cfg_season or None) or default_football_season_label()

    organizer = _get_organizer(organizer_id, log)
    if not organizer:
        _log(log, "No organizer; aborting")
        return {"created": 0, "updated": 0, "skipped": 0}

    sports_category, _ = Category.objects.get_or_create(
        name="Sports",
        defaults={
            "slug": "sports",
            "description": "Sports events including football matches, tournaments, and more",
            "icon": "trophy",
            "color": "#059669",
        },
    )

    try:
        rows = _fetch_rows(mode, league_id, season, log)
    except Exception as exc:
        _log(log, f"TheSportsDB v2 request failed: {exc}")
        logger.warning("TheSportsDB v2 sync failed: %s", exc)
        return {"created": 0, "updated": 0, "skipped": 0}

    created = updated = skipped = 0

    for row in rows:
        if (row.get("strSport") or "Soccer") != "Soccer":
            skipped += 1
            continue
        eid = str(row.get("idEvent") or "")
        if not eid:
            skipped += 1
            continue
        if str(row.get("idLeague") or "") != str(league_id):
            skipped += 1
            continue

        start = _parse_start(row)
        if not start:
            skipped += 1
            continue

        end = start + timedelta(hours=2)
        title = f"{row.get('strHomeTeam') or 'TBA'} vs {row.get('strAwayTeam') or 'TBA'}"
        slug = slugify(f"kpl-v2-{eid}")[:200] or f"kpl-v2-{eid}"[:200]
        match_data = _match_data_from_row(row, league_id)
        status = _event_status(row)
        venue = _venue_for_row(row)
        rnd = row.get("intRound")
        subtitle = f"FKF Premier League — Round {rnd}" if rnd else "FKF Premier League"

        existing = Event.objects.filter(match_data__idEvent=eid).first()
        if existing:
            existing.title = title[:200]
            existing.subtitle = subtitle[:300]
            existing.description = _description(row)
            existing.venue = venue
            existing.start_datetime = start
            existing.end_datetime = end
            existing.doors_open = (start - timedelta(minutes=30)).time()
            existing.match_data = match_data
            existing.status = status
            existing.tags = ["football", "FKF", "premier league", "sports", "kenya", "thesportsdb"]
            existing.save()
            updated += 1
            _log(log, f"Updated: {title}")
            continue

        if Event.objects.filter(slug=slug).exclude(match_data__idEvent=eid).exists():
            slug = f"{slug}-{eid}"[:200]

        with transaction.atomic():
            event = Event.objects.create(
                title=title[:200],
                slug=slug,
                subtitle=subtitle[:300],
                description=_description(row),
                category=sports_category,
                venue=venue,
                organizer=organizer,
                start_datetime=start,
                end_datetime=end,
                doors_open=(start - timedelta(minutes=30)).time(),
                age_restriction="All Ages",
                status=status,
                is_public=True,
                featured=False,
                tags=["football", "FKF", "premier league", "sports", "kenya", "thesportsdb"],
                match_data=match_data,
            )
            _ensure_ticket_tiers(event)
        created += 1
        _log(log, f"Created: {title}")

    return {"created": created, "updated": updated, "skipped": skipped}
