"""
Kenyan Premier League club badges.
Primary source: TheSportsDB v1 API (search_all_teams / lookupleague).
Offline TEAM_ASSETS is a fallback if the API is unavailable.
"""

from __future__ import annotations

from .thesportsdb_client import get_kpl_league_from_api, lookup_team_from_api

# https://www.thesportsdb.com/league/4745-kenyan-premier-league
TEAM_ASSETS: dict[str, dict[str, str]] = {
    "AFC Leopards": {
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/4taj3p1583767536.png",
        "primary_color": "#0000FF",
        "secondary_color": "#FFFFFF",
    },
    "APS Bomet": {
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/480ss31660940507.png",
        "primary_color": "#DC3232",
        "secondary_color": "#FFFFFF",
    },
    "Bandari FC": {
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/j0k5hr1583767461.png",
        "primary_color": "#004A99",
        "secondary_color": "#FDB913",
    },
    "Bidco United": {
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/7kovoy1616161037.png",
        "primary_color": "#43A047",
        "secondary_color": "#FFFFFF",
    },
    "Gor Mahia": {
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/8hqogn1583765598.png",
        "primary_color": "#008000",
        "secondary_color": "#FFFFFF",
    },
    "Kakamega Homeboyz": {
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/jk0iy41583764938.png",
        "primary_color": "#0059B3",
        "secondary_color": "#FFFFFF",
    },
    "Kariobangi Sharks": {
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/3byxk61583357154.png",
        "primary_color": "#43A047",
        "secondary_color": "#000000",
    },
    "KCB FC": {
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/ewpyvl1583765049.png",
        "primary_color": "#006837",
        "secondary_color": "#FFD700",
    },
    "Kenya Police FC": {
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/8rc7kn1776296960.png",
        "primary_color": "#CE1126",
        "secondary_color": "#0033A0",
    },
    "Mara Sugar FC": {
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/xycge61726169941.png",
        "primary_color": "#43A047",
        "secondary_color": "#FFFFFF",
    },
    "Mathare United": {
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/yj43x31583407667.png",
        "primary_color": "#DC3232",
        "secondary_color": "#000000",
    },
    "Murang'a SEAL": {
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/yb7j381689947933.png",
        "primary_color": "#DC3232",
        "secondary_color": "#FFFFFF",
    },
    "Nairobi United": {
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/c22eja1759163430.png",
        "primary_color": "#0059B3",
        "secondary_color": "#FFFFFF",
    },
    "Nzoia Sugar": {
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/fi78rj1583407331.png",
        "primary_color": "#0059B3",
        "secondary_color": "#FFFFFF",
    },
    "Posta Rangers": {
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/w8uos81583407110.png",
        "primary_color": "#E31E24",
        "secondary_color": "#FFFFFF",
    },
    "Shabana FC": {
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/bnu4ha1689948335.png",
        "primary_color": "#FF0000",
        "secondary_color": "#FFFFFF",
    },
    "Sofapaka FC": {
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/p7qrgw1583406664.png",
        "primary_color": "#0059B3",
        "secondary_color": "#FFFFFF",
    },
    "Tusker FC": {
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/9rnoc81583406233.png",
        "primary_color": "#FFFF00",
        "secondary_color": "#000000",
    },
    "Ulinzi Stars": {
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/5hzcu31583357971.png",
        "primary_color": "#ED1C24",
        "secondary_color": "#FFFFFF",
    },
}

KPL_THESPORTSDB = {
    "league_id": "4745",
    "league_name": "Kenyan Premier League",
    "badge": "https://r2.thesportsdb.com/images/media/league/badge/93vh0s1729441061.png",
    "logo": "https://r2.thesportsdb.com/images/media/league/logo/3v9tuh1729441106.png",
    "source": "https://www.thesportsdb.com/documentation",
}


def _static_team_assets(team_name: str) -> dict:
    if not team_name:
        return {}
    if team_name in TEAM_ASSETS:
        return TEAM_ASSETS[team_name]
    tn = team_name.strip().lower()
    for key, assets in TEAM_ASSETS.items():
        if key.lower() == tn:
            return assets
    return {}


def get_team_assets(team_name: str) -> dict:
    """Merge TheSportsDB API team row with static fallback (logo + colours)."""
    static = _static_team_assets(team_name)
    api = lookup_team_from_api(team_name)
    if not api and not static:
        return {}
    if not api:
        return static
    if not static:
        return {
            "logo": api.get("logo", ""),
            "primary_color": api.get("primary_color", "#000000"),
            "secondary_color": api.get("secondary_color", "#FFFFFF"),
        }
    return {
        "logo": api.get("logo") or static.get("logo", ""),
        "primary_color": api.get("primary_color") or static.get("primary_color", "#000000"),
        "secondary_color": api.get("secondary_color") or static.get("secondary_color", "#FFFFFF"),
    }


def kpl_league_branding() -> dict:
    """League badge/logo from API with static fallback."""
    merged = dict(KPL_THESPORTSDB)
    api = get_kpl_league_from_api()
    for key in ("league_id", "league_name", "badge", "logo", "source"):
        val = api.get(key) if api else None
        if val:
            merged[key] = val
    return merged


def enrich_match_data_logos(match_data: dict | None) -> dict:
    """Fill missing team badge URLs from KPL map (same names as stored fixtures)."""
    if not match_data or not isinstance(match_data, dict):
        return dict(match_data) if match_data else {}
    md = dict(match_data)
    home = md.get("home_team")
    away = md.get("away_team")
    for side, key_logo, key_pri, key_sec in (
        (home, "home_team_logo", "home_team_primary_color", "home_team_secondary_color"),
        (away, "away_team_logo", "away_team_primary_color", "away_team_secondary_color"),
    ):
        if not side:
            continue
        assets = get_team_assets(side)
        if not (md.get(key_logo) or "").strip() and assets.get("logo"):
            md[key_logo] = assets["logo"]
        if assets.get("primary_color") and not (md.get(key_pri) or "").strip():
            md[key_pri] = assets["primary_color"]
        if assets.get("secondary_color") and not (md.get(key_sec) or "").strip():
            md[key_sec] = assets["secondary_color"]
    branding = dict(md.get("branding") or {})
    branding["kpl"] = {**(branding.get("kpl") or {}), **kpl_league_branding()}
    # Add FKF logo URL - using local static file
    branding["fkf"] = {
        "logo": "/static/images/fkf-logo.png"
    }
    md["branding"] = branding
    return md
