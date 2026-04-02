"""
RailGuard — DB transport REST API client.
Bron: https://v6.db.transport.rest  (geen authenticatie vereist)

Functies:
  - Reisplanning A→B via /journeys
  - Stationszoekfunctie via /locations
  - Live vertrekbord met vertragingen via /stops/:id/departures
  - Actuele ritdetails (stopovers) via /trips/:id
  - Deeplinks naar bahn.de voor boekingen
"""

from __future__ import annotations

import urllib.parse
from datetime import datetime, timedelta

import requests
import streamlit as st

# ── Constanten ────────────────────────────────────────────────────────────────

BASE_URL = "https://v6.db.transport.rest"
TIMEOUT = 8  # seconden

# Mapping stationsnaam → DB stop-ID (voor live lookups)
STATION_IDS: dict[str, str] = {
    "Amsterdam Centraal": "8400058",
    "Amsterdam Zuid":     "8400056",
    "Rotterdam Centraal": "8400621",
    "Den Haag Centraal":  "8400319",
    "Utrecht Centraal":   "8400770",
    "Eindhoven":          "8400226",
    "Berlin Hbf":         "8011160",
    "Hamburg Hbf":        "8002549",
    "München Hbf":        "8000261",
    "Frankfurt(Main)Hbf": "8000105",
    "Köln Hbf":           "8000207",
    "Düsseldorf Hbf":     "8000085",
    "Stuttgart Hbf":      "8000096",
    "Hannover Hbf":       "8000152",
    "Leipzig Hbf":        "8010205",
    "Paris Nord":         "8727100",
    "Bruxelles-Midi":     "8814001",
    "Zürich HB":          "8503000",
    "Wien Hbf":           "8100003",
    "Basel SBB":          "8500010",
}


# ── Verbindingscheck ──────────────────────────────────────────────────────────

@st.cache_data(ttl=60, show_spinner=False)
def is_connected() -> bool:
    """Controleer of de transport REST API bereikbaar is."""
    try:
        resp = requests.get(
            f"{BASE_URL}/locations",
            params={"query": "Berlin", "results": "1"},
            timeout=TIMEOUT,
        )
        return resp.status_code == 200
    except Exception:
        return False


# ── Stationszoekfunctie ───────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def search_locations(query: str) -> list[dict]:
    """
    Zoek stops/stations op naam.
    Geeft lijst terug: [{"id": "8011160", "name": "Berlin Hbf", ...}, ...]
    """
    try:
        resp = requests.get(
            f"{BASE_URL}/locations",
            params={"query": query, "results": "10", "fuzzy": "true"},
            timeout=TIMEOUT,
        )
        if resp.status_code == 200:
            return [loc for loc in resp.json() if loc.get("type") == "station"]
        return []
    except Exception:
        return []


# ── Live vertrekbord ──────────────────────────────────────────────────────────

@st.cache_data(ttl=30, show_spinner=False)
def get_live_departures(
    station_id: str,
    when: datetime,
    duration_min: int = 45,
) -> list[dict]:
    """
    Haal actuele vertrekken op voor een station.

    Parameters
    ----------
    station_id   : DB stop-ID (bijv. "8011160")
    when         : vertrektijd om vanaf te zoeken
    duration_min : tijdvenster in minuten na `when`

    Elk vertrekobject bevat o.a.:
      tripId, line.name, plannedWhen, when, delay (seconden), platform,
      plannedPlatform, direction, cancelled, remarks
    """
    try:
        resp = requests.get(
            f"{BASE_URL}/stops/{station_id}/departures",
            params={
                "when": when.isoformat(),
                "duration": duration_min,
                "results": "80",
                "nationalExpress": "true",
                "national": "true",
                "regionalExpress": "true",
                "regional": "true",
            },
            timeout=TIMEOUT,
        )
        if resp.status_code == 200:
            return resp.json().get("departures", [])
        return []
    except Exception:
        return []


# ── Live ritdetails ───────────────────────────────────────────────────────────

@st.cache_data(ttl=30, show_spinner=False)
def get_trip_details(trip_id: str) -> dict:
    """
    Haal gedetailleerde informatie op over een rit: alle stopovers met actuele
    vertrek-/aankomsttijden en vertragingen.

    trip_id is de `tripId` uit een vertrekbord-response.
    """
    try:
        encoded = urllib.parse.quote(trip_id, safe="")
        resp = requests.get(
            f"{BASE_URL}/trips/{encoded}",
            params={"stopovers": "true", "remarks": "true"},
            timeout=TIMEOUT,
        )
        if resp.status_code == 200:
            return resp.json().get("trip", {})
        return {}
    except Exception:
        return {}


# ── Reisplanning A → B ────────────────────────────────────────────────────────

@st.cache_data(ttl=120, show_spinner=False)
def search_journeys(
    origin_id: str,
    dest_id: str,
    departure_dt: datetime,
    results: int = 8,
) -> list[dict]:
    """
    Zoek reizen van A naar B via /journeys.
    Geeft ruwe API-objecten terug; gebruik parse_api_journey() om te converteren.
    """
    try:
        resp = requests.get(
            f"{BASE_URL}/journeys",
            params={
                "from": origin_id,
                "to": dest_id,
                "departure": departure_dt.isoformat(),
                "results": results,
                "stopovers": "true",
                "nationalExpress": "true",
                "national": "true",
                "regionalExpress": "false",
                "regional": "false",
                "suburban": "false",
                "bus": "false",
                "ferry": "false",
            },
            timeout=TIMEOUT,
        )
        if resp.status_code == 200:
            return resp.json().get("journeys", [])
        return []
    except Exception:
        return []


def _parse_dt(s: str | None) -> datetime | None:
    """Parseer ISO 8601-string (met of zonder timezone) naar naive datetime."""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None


def _product_to_type(product: str) -> str:
    return {
        "nationalExpress": "ICE",
        "national": "IC",
        "regionalExpress": "RE",
        "regional": "RB",
        "suburban": "S",
    }.get(product, "IC")


def parse_api_journey(raw: dict, idx: int) -> dict | None:
    """
    Converteer een ruwe /journeys API-response naar het interne RailGuard-formaat.
    Geeft None terug als de data onvolledig is.
    """
    legs = raw.get("legs", [])
    if not legs:
        return None

    first, last = legs[0], legs[-1]

    dep = _parse_dt(first.get("departure") or first.get("plannedDeparture"))
    arr = _parse_dt(last.get("arrival") or last.get("plannedArrival"))
    if not dep or not arr:
        return None

    duration_min = max(1, int((arr - dep).total_seconds() / 60))
    h, m = divmod(duration_min, 60)

    # Stops verzamelen uit stopovers van alle legs
    stops: list[str] = []
    for leg in legs:
        for sv in leg.get("stopovers", []):
            name = (sv.get("stop") or {}).get("name", "")
            if name and name not in stops:
                stops.append(name)
    if not stops:
        stops = [
            (first.get("origin") or {}).get("name", ""),
            (last.get("destination") or {}).get("name", ""),
        ]

    # Treinnaam
    line1 = (first.get("line") or {}).get("name", "Trein")
    train_type = _product_to_type((first.get("line") or {}).get("product", "national"))
    line_name = line1
    if len(legs) > 1:
        line2 = (legs[1].get("line") or {}).get("name", "")
        line_name = f"{line1} → {line2}"

    # Overstapinformatie
    transfers = len(legs) - 1
    transfer_station = ""
    transfer_buffer_min = 0
    transfer_arrival_dt: datetime | None = None

    if transfers > 0:
        transfer_station = (first.get("destination") or {}).get("name", "")
        arr1 = _parse_dt(first.get("arrival") or first.get("plannedArrival"))
        dep2 = _parse_dt(legs[1].get("departure") or legs[1].get("plannedDeparture"))
        if arr1 and dep2:
            transfer_buffer_min = max(0, int((dep2 - arr1).total_seconds() / 60))
            transfer_arrival_dt = arr1  # exacte aankomsttijd op overstapstation

    platform = (
        first.get("departurePlatform")
        or first.get("plannedDeparturePlatform")
        or "—"
    )

    return {
        "id": f"api-{dep.strftime('%Y%m%d%H%M')}-{idx}",
        "train": line_name,
        "type": train_type,
        "operator": "DB",
        "departure": dep,
        "arrival": arr,
        "duration": f"{h}u {m:02d}m" if h else f"{m}m",
        "duration_min": duration_min,
        "transfers": transfers,
        "transfer_station": transfer_station,
        "transfer_buffer_min": transfer_buffer_min,
        "transfer_arrival_dt": transfer_arrival_dt,
        "stops": stops,
        "platform": str(platform),
        "price_eur": None,  # niet beschikbaar via deze API
        "origin": (first.get("origin") or {}).get("name", ""),
        "destination": (last.get("destination") or {}).get("name", ""),
        "source": "api",
    }


# ── Live vertraging ophalen voor een opgeslagen reis ─────────────────────────

def get_live_delay_for_journey(journey: dict) -> tuple[int, bool, str | None]:
    """
    Zoek de actuele vertraging op voor een opgeslagen reis.

    Werkt door het vertrekbord van het beginstation te raadplegen rond de
    geplande vertrektijd en te matchen op treinnaam.

    Returns
    -------
    (delay_min, is_live, trip_id)
      delay_min : vertraging in minuten (0 als op tijd)
      is_live   : True als data van de API komt, False als gesimuleerd
      trip_id   : DB trip-ID voor verdere details (of None)
    """
    origin = journey.get("origin", "")
    station_id = STATION_IDS.get(origin)
    if not station_id:
        return 0, False, None

    dep_dt: datetime = journey["departure"]
    # Naam van de eerste trein (bij meerdere treinen, bijv. "ICE 123 → ICE 456")
    first_train = journey["train"].split("→")[0].strip()

    # Zoek iets vóór de geplande vertrektijd zodat we kleine vroege treinen ook vangen
    search_from = dep_dt - timedelta(minutes=5)

    try:
        departures = get_live_departures(station_id, search_from, duration_min=30)
    except Exception:
        return 0, False, None

    for dep in departures:
        line_name = (dep.get("line") or {}).get("name", "")
        if _train_matches(first_train, line_name):
            if dep.get("cancelled"):
                return 999, True, None  # seincode voor opgeheven
            delay_sec = dep.get("delay") or 0
            trip_id = dep.get("tripId")
            return delay_sec // 60, True, trip_id

    # Niet gevonden in vertrekbord (trein rijdt mogelijk niet vandaag of is al weg)
    return 0, False, None


def _train_matches(saved_name: str, api_name: str) -> bool:
    """
    Vergelijk treinnaam uit opgeslagen reis met API-response.
    Bijv. "ICE 123" matcht "ICE 123" en "ICE123".
    """
    def norm(s: str) -> str:
        return s.upper().replace(" ", "")
    return norm(saved_name) == norm(api_name)


# ── Booking deeplink ──────────────────────────────────────────────────────────

def build_booking_deeplink(
    origin: str,
    destination: str,
    departure_dt: datetime,
) -> str:
    """
    Deeplink naar bahn.de met vooringevulde route en vertrektijd.
    Formaat: https://www.bahn.de/buchung/fahrplan/suche#sts=true&so=...&zo=...&hd=...&hza=D

    Let op: de hash-fragment wordt NIET via urlencode gebouwd omdat bahn.de de
    %3A-encoding van ':' in de datum-tijd niet correct verwerkt. Stationsnamen
    worden apart met %20-spaties gecodeerd.
    """
    so = urllib.parse.quote(origin, safe="")
    zo = urllib.parse.quote(destination, safe="")
    hd = departure_dt.strftime("%Y-%m-%dT%H:%M")  # literal dubbele punt — niet encoderen
    return (
        f"https://www.bahn.de/buchung/fahrplan/suche"
        f"#sts=true&so={so}&zo={zo}&hd={hd}&hza=D&ar=false&s=true"
    )


def build_realtime_status_url(train_number: str, dep_date: datetime) -> str:
    """Deeplink naar live treinpositie op der-bahnstatus.de."""
    return (
        f"https://www.der-bahnstatus.de/zug/"
        f"{urllib.parse.quote(train_number)}/"
        f"{dep_date.strftime('%Y-%m-%d')}"
    )
