"""
Scrape TheSportsDB public league HTML pages (e.g. /league/4745-kenyan-premier-league).
Use when JSON APIs are unavailable; respect site terms and rate limits.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

SITE_ORIGIN = "https://www.thesportsdb.com"
DEFAULT_LEAGUE_PATH = "/league/4745-kenyan-premier-league"
EAT = ZoneInfo("Africa/Nairobi")

_EVENT_HREF = re.compile(r"^/event/(\d+)-(.+)$")
_TEAM_HREF = re.compile(r"^/team/(\d+)-(.+)$")
_DAY_MONTH = re.compile(r"^\s*(\d{1,2})\s+([A-Za-z]+)\s*$")
_SCORE = re.compile(r"^\s*(\d+)\s*-\s*(\d+)\s*$")


@dataclass
class ScrapedFixture:
    id_event: str
    href: str
    home_team: str
    away_team: str
    home_badge_url: str
    away_badge_url: str
    day_label: str
    kickoff_local: datetime | None = None
    home_score: int | None = None
    away_score: int | None = None
    section: str = ""  # "upcoming" | "results"


@dataclass
class ScrapedTeam:
    id_team: str
    href: str
    name: str
    badge_url: str


@dataclass
class ScrapedLeaguePage:
    league_name: str
    league_path: str
    season: str | None
    current_round: str | None
    badge_url: str | None
    logo_url: str | None
    location: str | None
    established: str | None
    upcoming: list[ScrapedFixture] = field(default_factory=list)
    results: list[ScrapedFixture] = field(default_factory=list)
    teams: list[ScrapedTeam] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        def fx(f: ScrapedFixture) -> dict[str, Any]:
            return {
                "id_event": f.id_event,
                "href": f.href,
                "home_team": f.home_team,
                "away_team": f.away_team,
                "home_badge_url": f.home_badge_url,
                "away_badge_url": f.away_badge_url,
                "day_label": f.day_label,
                "kickoff_local": f.kickoff_local.isoformat() if f.kickoff_local else None,
                "home_score": f.home_score,
                "away_score": f.away_score,
                "section": f.section,
            }

        return {
            "league_name": self.league_name,
            "league_path": self.league_path,
            "season": self.season,
            "current_round": self.current_round,
            "badge_url": self.badge_url,
            "logo_url": self.logo_url,
            "location": self.location,
            "established": self.established,
            "upcoming": [fx(x) for x in self.upcoming],
            "results": [fx(x) for x in self.results],
            "teams": [
                {
                    "id_team": t.id_team,
                    "href": t.href,
                    "name": t.name,
                    "badge_url": t.badge_url,
                }
                for t in self.teams
            ],
        }


def fetch_league_html(league_path: str = DEFAULT_LEAGUE_PATH, *, timeout: int = 45) -> str:
    path = league_path if league_path.startswith("/") else f"/{league_path}"
    url = f"{SITE_ORIGIN}{path}"
    r = requests.get(
        url,
        timeout=timeout,
        headers={"User-Agent": "brightpassticket/1.0 (league page; +https://thesportsdb.com)"},
    )
    r.raise_for_status()
    return r.text


def _img_badge_url(td) -> str:
    img = td.find("img", src=re.compile(r"badge", re.I))
    if not img or not img.get("src"):
        return ""
    src = img["src"].strip()
    if "/tiny" in src:
        src = src.replace("/tiny", "/medium")
    if src.startswith("//"):
        src = "https:" + src
    elif src.startswith("/"):
        src = SITE_ORIGIN + src
    return src


def _event_link(td):
    for a in td.find_all("a", href=_EVENT_HREF):
        m = _EVENT_HREF.match(a.get("href", "").strip())
        if m:
            return m.group(1), a.get("href", "").strip(), a.get_text(strip=True)
    return None, "", ""


def _names_from_slug(slug_rest: str) -> tuple[str, str]:
    """slug_rest like 'gor-mahia-vs-kenya-police'."""
    if "-vs-" not in slug_rest:
        return "", ""
    left, right = slug_rest.split("-vs-", 1)

    def tit(part: str) -> str:
        return " ".join(w.capitalize() for w in part.split("-") if w)

    return tit(left), tit(right)


def _parse_day_month(day_label: str, ref: date) -> date | None:
    m = _DAY_MONTH.match(day_label)
    if not m:
        return None
    d, mon = int(m.group(1)), m.group(2).strip()
    year = ref.year
    for fmt in ("%d %B %Y", "%d %b %Y"):
        try:
            return datetime.strptime(f"{d} {mon} {year}", fmt).date()
        except ValueError:
            continue
    return None


def _combine_day_and_time(day_label: str, time_text: str, ref: date) -> datetime | None:
    d = _parse_day_month(day_label, ref)
    if not d:
        return None
    t_raw = (time_text or "").strip()
    if not t_raw:
        return datetime.combine(d, datetime.min.time().replace(hour=12, minute=0), tzinfo=EAT)
    t_clean = t_raw.upper().replace(" ", "")
    for fmt in ("%I:%M%p", "%I%p"):
        try:
            t = datetime.strptime(t_clean, fmt).time()
            return datetime.combine(d, t, tzinfo=EAT)
        except ValueError:
            continue
    return datetime.combine(d, datetime.min.time().replace(hour=12, minute=0), tzinfo=EAT)


def _text_after_brs(node) -> str | None:
    el = node.next_sibling
    while el is not None and getattr(el, "name", None) == "br":
        el = el.next_sibling
    if isinstance(el, str):
        t = el.strip()
        return t or None
    return None


def _anchor_visible_text(a) -> str:
    """Site uses malformed `<a href='...'/>Label</a>`; text may sit after the tag."""
    t = a.get_text(strip=True)
    if t:
        return t
    sib = a.next_sibling
    if isinstance(sib, str) and sib.strip():
        return sib.strip()
    return ""


def _parse_sidebar_left(soup: BeautifulSoup) -> dict[str, Any]:
    out: dict[str, Any] = {
        "league_name": "",
        "season": None,
        "current_round": None,
        "badge_url": None,
        "location": None,
        "established": None,
    }
    left = soup.select_one("div.col-sm-3")
    if not left:
        return out
    h1 = left.find("h1")
    if h1:
        out["league_name"] = h1.get_text(strip=True)
    for b in left.find_all("b"):
        label = (b.string or b.get_text(strip=True) or "").strip()
        if label == "Current Season":
            a = b.find_next("a", href=re.compile(r"/season/"))
            if a:
                out["season"] = _anchor_visible_text(a) or None
        elif label == "Current Round":
            a = b.find_next("a", href=re.compile(r"/season/.*[?]r="))
            if a:
                out["current_round"] = _anchor_visible_text(a) or None
        elif label == "Badge":
            a = b.find_next("a", href=re.compile(r"images/media/league/badge", re.I))
            if a and a.get("href"):
                out["badge_url"] = a["href"].strip()
        elif label == "Location":
            out["location"] = _text_after_brs(b)
        elif label == "Established":
            out["established"] = _text_after_brs(b)
    return out


def _parse_logo_url(soup: BeautifulSoup) -> str | None:
    main = soup.select_one("div.col-sm-9")
    if not main:
        return None
    for b in main.find_all("b"):
        if (b.string or "").strip() == "Logo":
            a = b.find_next("a", href=re.compile(r"thesportsdb|r2\.thesportsdb", re.I))
            if a and a.get("href"):
                return a["href"].strip()
    return None


def _find_fixtures_table(soup: BeautifulSoup):
    for tab in soup.find_all("table"):
        b = tab.find("b")
        if b and (b.string or "").strip() == "Upcoming":
            return tab
    return None


def _parse_upcoming_cells(table, ref: date) -> list[ScrapedFixture]:
    tds = [c for c in table.children if getattr(c, "name", None) == "td"]
    out: list[ScrapedFixture] = []
    for i in range(0, len(tds), 4):
        chunk = tds[i : i + 4]
        if len(chunk) < 4:
            break
        date_td, home_td, time_td, away_td = chunk
        day_label = date_td.get_text(strip=True)
        time_text = time_td.get_text(strip=True)
        eid_h, href_h, _ = _event_link(home_td)
        eid_a, href_a, _ = _event_link(away_td)
        eid = eid_h or eid_a
        href = href_h or href_a
        if not eid or not href:
            continue
        m = _EVENT_HREF.match(href)
        slug_names = _names_from_slug(m.group(2)) if m else ("", "")
        ha = home_td.find("a", href=_EVENT_HREF)
        aa = away_td.find("a", href=_EVENT_HREF)
        home_name = slug_names[0] or (_anchor_visible_text(ha) if ha else "")
        away_name = slug_names[1] or (_anchor_visible_text(aa) if aa else "")
        ko = _combine_day_and_time(day_label, time_text, ref)
        out.append(
            ScrapedFixture(
                id_event=eid,
                href=href,
                home_team=home_name,
                away_team=away_name,
                home_badge_url=_img_badge_url(home_td),
                away_badge_url=_img_badge_url(away_td),
                day_label=day_label,
                kickoff_local=ko,
                section="upcoming",
            )
        )
    return out


def _parse_result_rows(table, ref: date) -> list[ScrapedFixture]:
    out: list[ScrapedFixture] = []
    seen_results = False
    for child in table.children:
        if getattr(child, "name", None) != "tr":
            continue
        b = child.find("b")
        if b and (b.string or "").strip() == "Results":
            seen_results = True
            continue
        if not seen_results:
            continue
        tds = child.find_all("td")
        if len(tds) != 4:
            continue
        date_td, home_td, score_td, away_td = tds
        day_label = date_td.get_text(strip=True)
        score_m = _SCORE.match(score_td.get_text())
        hs = int(score_m.group(1)) if score_m else None
        aws = int(score_m.group(2)) if score_m else None
        eid_h, href_h, _ = _event_link(home_td)
        eid_a, href_a, _ = _event_link(away_td)
        eid = eid_h or eid_a
        href = href_h or href_a
        if not eid:
            continue
        m = _EVENT_HREF.match(href)
        slug_names = _names_from_slug(m.group(2)) if m else ("", "")
        ha = home_td.find("a", href=_EVENT_HREF)
        aa = away_td.find("a", href=_EVENT_HREF)
        home_name = slug_names[0] or (_anchor_visible_text(ha) if ha else "")
        away_name = slug_names[1] or (_anchor_visible_text(aa) if aa else "")
        d = _parse_day_month(day_label, ref)
        ko = datetime.combine(d, datetime.min.time().replace(hour=12, minute=0), tzinfo=EAT) if d else None
        out.append(
            ScrapedFixture(
                id_event=eid,
                href=href,
                home_team=home_name,
                away_team=away_name,
                home_badge_url=_img_badge_url(home_td),
                away_badge_url=_img_badge_url(away_td),
                day_label=day_label,
                kickoff_local=ko,
                home_score=hs,
                away_score=aws,
                section="results",
            )
        )
    return out


def _parse_teams(soup: BeautifulSoup) -> list[ScrapedTeam]:
    teams_header = soup.find("b", id="teamImages")
    if not teams_header:
        return []
    tbl = teams_header.find_next("table")
    if not tbl:
        return []
    out: list[ScrapedTeam] = []
    for td in tbl.find_all("td", valign="top"):
        center = td.find("center")
        if not center:
            continue
        a = center.find("a", href=_TEAM_HREF)
        if not a:
            continue
        m = _TEAM_HREF.match(a.get("href", "").strip())
        if not m:
            continue
        tid, slug = m.group(1), m.group(2)
        img = center.find("img", src=re.compile(r"badge", re.I))
        badge = ""
        if img and img.get("src"):
            badge = img["src"].strip()
            if badge.startswith("//"):
                badge = "https:" + badge
            elif badge.startswith("/"):
                badge = SITE_ORIGIN + badge
        name = ""
        candidates: list[str] = []
        for s in center.strings:
            t = s.strip()
            if len(t) >= 2 and t.lower() not in ("country", "team badge") and "Icon" not in t:
                candidates.append(t)
        if candidates:
            name = candidates[-1]
        if not name:
            name = " ".join(w.capitalize() for w in slug.split("-") if w)
        out.append(
            ScrapedTeam(
                id_team=tid,
                href=a["href"].strip(),
                name=name,
                badge_url=badge,
            )
        )
    return out


def parse_league_html(
    html: str,
    *,
    league_path: str = DEFAULT_LEAGUE_PATH,
    reference_date: date | None = None,
) -> ScrapedLeaguePage:
    ref = reference_date or datetime.now(EAT).date()
    soup = BeautifulSoup(html, "html.parser")
    side = _parse_sidebar_left(soup)
    logo = _parse_logo_url(soup)
    table = _find_fixtures_table(soup)
    upcoming: list[ScrapedFixture] = []
    results: list[ScrapedFixture] = []
    if table:
        upcoming = _parse_upcoming_cells(table, ref)
        results = _parse_result_rows(table, ref)
    teams = _parse_teams(soup)
    return ScrapedLeaguePage(
        league_name=side.get("league_name") or "",
        league_path=league_path if league_path.startswith("/") else f"/{league_path}",
        season=side.get("season"),
        current_round=side.get("current_round"),
        badge_url=side.get("badge_url"),
        logo_url=logo,
        location=side.get("location"),
        established=side.get("established"),
        upcoming=upcoming,
        results=results,
        teams=teams,
    )


def scrape_league_page(
    league_path: str = DEFAULT_LEAGUE_PATH,
    *,
    reference_date: date | None = None,
) -> ScrapedLeaguePage:
    html = fetch_league_html(league_path)
    return parse_league_html(html, league_path=league_path, reference_date=reference_date)
