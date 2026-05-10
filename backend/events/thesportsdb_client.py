"""
TheSportsDB REST API v1 client (free tier).
Docs: https://www.thesportsdb.com/documentation
"""

from __future__ import annotations

import logging
import re
from typing import Any

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

V1_BASE = "https://www.thesportsdb.com/api/v1/json"
# v1 list teams: search_all_teams.php?l={League_Name_Underscores}
KPL_LEAGUE_LIST_PARAM = "Kenyan_Premier_League"
KPL_LEAGUE_ID = "4745"
CACHE_KPL_TEAMS = "thesportsdb:kpl:team_lookup:v1"
CACHE_KPL_LEAGUE = "thesportsdb:kpl:league:v1"
# Stay under free-tier limits; data changes infrequently
CACHE_TTL_SECONDS = 60 * 60 * 12


def api_key() -> str:
    return getattr(settings, "THESPORTSDB_API_KEY", None) or "123"


def _name_variants(name: str) -> list[str]:
    if not name or not str(name).strip():
        return []
    raw = name.strip().lower()
    de_apost = raw.replace("'", "").replace("’", "")
    no_fc = re.sub(r"\s+fc$", "", de_apost).strip()
    no_sc = re.sub(r"\s+sc$", "", no_fc).strip()
    collapsed = re.sub(r"[^\w\s]", " ", no_sc)
    collapsed = re.sub(r"\s+", " ", collapsed).strip()
    out: list[str] = []
    seen: set[str] = set()
    for v in (raw, de_apost, no_fc, no_sc, collapsed):
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out


def _register_names(mapping: dict[str, dict[str, str]], names: list[str], asset: dict[str, str]) -> None:
    for nm in names:
        for v in _name_variants(nm):
            if v and v not in mapping:
                mapping[v] = asset


def _fetch_kpl_teams_raw() -> list[dict[str, Any]]:
    url = f"{V1_BASE}/{api_key()}/search_all_teams.php"
    r = requests.get(
        url,
        params={"l": KPL_LEAGUE_LIST_PARAM},
        timeout=20,
        headers={"User-Agent": "brightpassticket/1.0 (TheSportsDB v1)"},
    )
    r.raise_for_status()
    payload = r.json()
    teams = payload.get("teams")
    if teams is None:
        return []
    if isinstance(teams, dict):
        return [teams]
    return list(teams)


def build_kpl_team_lookup(teams: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    """Normalized name -> {logo, optional primary_color, optional secondary_color}."""
    by_key: dict[str, dict[str, str]] = {}
    for t in teams:
        badge = (t.get("strBadge") or "").strip()
        if not badge:
            continue
        asset: dict[str, str] = {"logo": badge}
        c1 = (t.get("strColour1") or "").strip()
        c2 = (t.get("strColour2") or "").strip()
        if c1:
            asset["primary_color"] = c1
        if c2:
            asset["secondary_color"] = c2
        primary = t.get("strTeam") or ""
        alts: list[str] = [primary]
        alt_raw = t.get("strTeamAlternate") or ""
        if isinstance(alt_raw, str) and alt_raw.strip():
            alts.extend([a.strip() for a in alt_raw.split(",") if a.strip()])
        _register_names(by_key, alts, asset)
    return by_key


def get_kpl_team_lookup() -> dict[str, dict[str, str]]:
    cached = cache.get(CACHE_KPL_TEAMS)
    if isinstance(cached, dict):
        return cached
    try:
        teams = _fetch_kpl_teams_raw()
        lookup = build_kpl_team_lookup(teams)
        if lookup:
            cache.set(CACHE_KPL_TEAMS, lookup, CACHE_TTL_SECONDS)
        return lookup
    except Exception as exc:
        logger.warning("TheSportsDB search_all_teams KPL failed: %s", exc)
        return {}


def lookup_team_from_api(team_name: str) -> dict[str, str]:
    if not team_name:
        return {}
    lu = get_kpl_team_lookup()
    for v in _name_variants(team_name):
        hit = lu.get(v)
        if hit:
            return dict(hit)
    return {}


def _fetch_kpl_league_raw() -> dict[str, Any]:
    url = f"{V1_BASE}/{api_key()}/lookupleague.php"
    r = requests.get(
        url,
        params={"id": KPL_LEAGUE_ID},
        timeout=20,
        headers={"User-Agent": "brightpassticket/1.0 (TheSportsDB v1)"},
    )
    r.raise_for_status()
    leagues = r.json().get("leagues") or []
    if isinstance(leagues, dict):
        return leagues
    return leagues[0] if leagues else {}


def get_kpl_league_from_api() -> dict[str, str]:
    cached = cache.get(CACHE_KPL_LEAGUE)
    if isinstance(cached, dict):
        return cached
    try:
        row = _fetch_kpl_league_raw()
        meta = {
            "league_id": KPL_LEAGUE_ID,
            "league_name": (row.get("strLeague") or "Kenyan Premier League").strip(),
            "badge": (row.get("strBadge") or "").strip(),
            "logo": (row.get("strLogo") or "").strip(),
            "source": "https://www.thesportsdb.com/documentation",
        }
        if meta.get("badge") or meta.get("logo"):
            cache.set(CACHE_KPL_LEAGUE, meta, CACHE_TTL_SECONDS)
        return meta
    except Exception as exc:
        logger.warning("TheSportsDB lookupleague KPL failed: %s", exc)
        return {}
