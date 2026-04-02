"""
Realistische demodata voor RailGuard (DB-routes).
Wordt gebruikt wanneer geen DB API-sleutel beschikbaar is of de API niet bereikbaar is.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any


# ── Populaire stations ────────────────────────────────────────────────────────

POPULAR_STATIONS: list[dict] = [
    {"name": "Amsterdam Centraal", "id": "8400058", "country": "NL"},
    {"name": "Amsterdam Zuid", "id": "8400056", "country": "NL"},
    {"name": "Rotterdam Centraal", "id": "8400621", "country": "NL"},
    {"name": "Den Haag Centraal", "id": "8400319", "country": "NL"},
    {"name": "Utrecht Centraal", "id": "8400770", "country": "NL"},
    {"name": "Eindhoven", "id": "8400226", "country": "NL"},
    {"name": "Berlin Hbf", "id": "8011160", "country": "DE"},
    {"name": "Hamburg Hbf", "id": "8002549", "country": "DE"},
    {"name": "München Hbf", "id": "8000261", "country": "DE"},
    {"name": "Frankfurt(Main)Hbf", "id": "8000105", "country": "DE"},
    {"name": "Köln Hbf", "id": "8000207", "country": "DE"},
    {"name": "Düsseldorf Hbf", "id": "8000085", "country": "DE"},
    {"name": "Stuttgart Hbf", "id": "8000096", "country": "DE"},
    {"name": "Hannover Hbf", "id": "8000152", "country": "DE"},
    {"name": "Leipzig Hbf", "id": "8010205", "country": "DE"},
    {"name": "Paris Nord", "id": "8727100", "country": "FR"},
    {"name": "Bruxelles-Midi", "id": "8814001", "country": "BE"},
    {"name": "Zürich HB", "id": "8503000", "country": "CH"},
    {"name": "Wien Hbf", "id": "8100003", "country": "AT"},
    {"name": "Basel SBB", "id": "8500010", "country": "CH"},
]

# ── Route-templates ────────────────────────────────────────────────────────────

_ROUTE_TEMPLATES: dict[tuple[str, str], list[dict]] = {
    ("Amsterdam Centraal", "Berlin Hbf"): [
        {
            "train": "ICE 123",
            "type": "ICE",
            "operator": "DB / NS International",
            "duration_min": 370,
            "stops": ["Amsterdam Centraal", "Utrecht Centraal", "Arnhem Centraal", "Oberhausen", "Duisburg", "Düsseldorf", "Köln", "Dortmund", "Hannover", "Berlin Hbf"],
            "transfers": 0,
            "price_eur": 39,
            "platform": "4",
        },
        {
            "train": "ICE 225 → ICE 844",
            "type": "ICE",
            "operator": "DB / NS International",
            "duration_min": 395,
            "stops": ["Amsterdam Centraal", "Utrecht Centraal", "Arnhem Centraal", "Oberhausen", "Duisburg", "Düsseldorf", "Köln", "Frankfurt(Main)Hbf", "Fulda", "Berlin Hbf"],
            "transfers": 1,
            "transfer_station": "Köln Hbf",
            "transfer_buffer_min": 14,
            "price_eur": 29,
            "platform": "7",
        },
    ],
    ("Amsterdam Centraal", "Köln Hbf"): [
        {
            "train": "ICE 125",
            "type": "ICE",
            "operator": "DB / NS International",
            "duration_min": 158,
            "stops": ["Amsterdam Centraal", "Utrecht Centraal", "Arnhem Centraal", "Oberhausen", "Duisburg", "Düsseldorf", "Köln Hbf"],
            "transfers": 0,
            "price_eur": 19,
            "platform": "11",
        },
    ],
    ("Amsterdam Centraal", "Frankfurt(Main)Hbf"): [
        {
            "train": "ICE 227",
            "type": "ICE",
            "operator": "DB / NS International",
            "duration_min": 295,
            "stops": ["Amsterdam Centraal", "Utrecht Centraal", "Arnhem Centraal", "Oberhausen", "Duisburg", "Düsseldorf", "Köln Hbf", "Koblenz", "Frankfurt(Main)Hbf"],
            "transfers": 0,
            "price_eur": 39,
            "platform": "6",
        },
        {
            "train": "Thalys 9423 → ICE 511",
            "type": "IC",
            "operator": "Eurostar / DB",
            "duration_min": 330,
            "stops": ["Amsterdam Centraal", "Rotterdam Centraal", "Antwerpen-Centraal", "Bruxelles-Midi", "Liège", "Köln Hbf", "Frankfurt(Main)Hbf"],
            "transfers": 1,
            "transfer_station": "Bruxelles-Midi",
            "transfer_buffer_min": 18,
            "price_eur": 49,
            "platform": "2",
        },
    ],
    ("Amsterdam Centraal", "München Hbf"): [
        {
            "train": "ICE 229 → ICE 1091",
            "type": "ICE",
            "operator": "DB / NS International",
            "duration_min": 440,
            "stops": ["Amsterdam Centraal", "Utrecht Centraal", "Arnhem Centraal", "Oberhausen", "Duisburg", "Düsseldorf", "Köln Hbf", "Frankfurt(Main)Hbf", "Nürnberg Hbf", "München Hbf"],
            "transfers": 1,
            "transfer_station": "Frankfurt(Main)Hbf",
            "transfer_buffer_min": 12,
            "price_eur": 49,
            "platform": "8",
        },
    ],
    ("Rotterdam Centraal", "Berlin Hbf"): [
        {
            "train": "ICE 121",
            "type": "ICE",
            "operator": "DB / NS International",
            "duration_min": 385,
            "stops": ["Rotterdam Centraal", "Utrecht Centraal", "Arnhem Centraal", "Oberhausen", "Duisburg", "Düsseldorf", "Köln Hbf", "Dortmund", "Hannover", "Berlin Hbf"],
            "transfers": 0,
            "price_eur": 39,
            "platform": "3",
        },
    ],
    ("Berlin Hbf", "München Hbf"): [
        {
            "train": "ICE 1001",
            "type": "ICE",
            "operator": "DB",
            "duration_min": 268,
            "stops": ["Berlin Hbf", "Erfurt Hbf", "Nürnberg Hbf", "München Hbf"],
            "transfers": 0,
            "price_eur": 29,
            "platform": "5",
        },
        {
            "train": "ICE 1003",
            "type": "ICE",
            "operator": "DB",
            "duration_min": 285,
            "stops": ["Berlin Hbf", "Halle(Saale)", "Erfurt Hbf", "Nürnberg Hbf", "Ingolstadt", "München Hbf"],
            "transfers": 0,
            "price_eur": 19,
            "platform": "5",
        },
    ],
    ("Berlin Hbf", "Hamburg Hbf"): [
        {
            "train": "ICE 591",
            "type": "ICE",
            "operator": "DB",
            "duration_min": 98,
            "stops": ["Berlin Hbf", "Hamburg Hbf"],
            "transfers": 0,
            "price_eur": 17,
            "platform": "12",
        },
    ],
    ("Frankfurt(Main)Hbf", "München Hbf"): [
        {
            "train": "ICE 1083",
            "type": "ICE",
            "operator": "DB",
            "duration_min": 185,
            "stops": ["Frankfurt(Main)Hbf", "Würzburg Hbf", "Nürnberg Hbf", "Ingolstadt", "München Hbf"],
            "transfers": 0,
            "price_eur": 19,
            "platform": "9",
        },
    ],
    ("Köln Hbf", "Berlin Hbf"): [
        {
            "train": "ICE 843",
            "type": "ICE",
            "operator": "DB",
            "duration_min": 258,
            "stops": ["Köln Hbf", "Dortmund Hbf", "Hannover Hbf", "Berlin Hbf"],
            "transfers": 0,
            "price_eur": 25,
            "platform": "3",
        },
    ],
}


def _fuzzy_match(query: str, name: str) -> bool:
    """Eenvoudige gedeeltelijke match (hoofdletterongevoelig)."""
    return query.lower() in name.lower()


def filter_stations(query: str) -> list[dict]:
    """Filter populaire stations op naam."""
    if not query or len(query) < 2:
        return POPULAR_STATIONS[:8]
    return [s for s in POPULAR_STATIONS if _fuzzy_match(query, s["name"])][:8]


def get_journeys(
    origin: str,
    destination: str,
    departure_dt: datetime,
) -> list[dict]:
    """
    Geef realistische reisopties terug voor de opgegeven route en vertrektijd.
    Vult ontbrekende routes op met gegenereerde resultaten.
    """
    # Zoek directe template-match (ook omgekeerd)
    templates = _ROUTE_TEMPLATES.get(
        (origin, destination),
        _ROUTE_TEMPLATES.get((destination, origin), []),
    )

    results: list[dict] = []
    current_dt = departure_dt

    for i, tpl in enumerate(templates):
        dep = current_dt + timedelta(minutes=i * 30)
        arr = dep + timedelta(minutes=tpl["duration_min"])
        results.append(
            _build_journey(tpl, dep, arr, i)
        )

    # Geen exacte match → genereer plausibele opties
    if not results:
        results = _generate_generic_journeys(origin, destination, departure_dt)

    return results


def _build_journey(tpl: dict, dep: datetime, arr: datetime, index: int) -> dict:
    h, m = divmod(tpl["duration_min"], 60)
    duration_str = f"{h}u {m:02d}m" if h else f"{m}m"
    transfers = tpl.get("transfers", 0)
    return {
        "id": f"rg-{dep.strftime('%Y%m%d%H%M')}-{index}",
        "train": tpl["train"],
        "type": tpl["type"],
        "operator": tpl["operator"],
        "departure": dep,
        "arrival": arr,
        "duration": duration_str,
        "duration_min": tpl["duration_min"],
        "transfers": transfers,
        "transfer_station": tpl.get("transfer_station", ""),
        "transfer_buffer_min": tpl.get("transfer_buffer_min", 0),
        "stops": tpl["stops"],
        "platform": tpl.get("platform", str(random.randint(1, 14))),
        "price_eur": tpl["price_eur"],
        "origin": tpl["stops"][0],
        "destination": tpl["stops"][-1],
    }


def _generate_generic_journeys(
    origin: str,
    destination: str,
    dep_dt: datetime,
) -> list[dict]:
    """Genereer 2 plausibele ICE-ritten wanneer geen template beschikbaar is."""
    journeys = []
    for i in range(2):
        dep = dep_dt + timedelta(minutes=i * 60)
        duration = 180 + i * 30
        arr = dep + timedelta(minutes=duration)
        h, m = divmod(duration, 60)
        train_num = 600 + i * 2
        journeys.append({
            "id": f"rg-gen-{dep.strftime('%Y%m%d%H%M')}-{i}",
            "train": f"ICE {train_num}",
            "type": "ICE",
            "operator": "DB",
            "departure": dep,
            "arrival": arr,
            "duration": f"{h}u {m:02d}m",
            "duration_min": duration,
            "transfers": i,
            "transfer_station": "Frankfurt(Main)Hbf" if i > 0 else "",
            "transfer_buffer_min": 15 if i > 0 else 0,
            "stops": [origin, destination] if i == 0 else [origin, "Frankfurt(Main)Hbf", destination],
            "platform": str(random.randint(1, 14)),
            "price_eur": 29 + i * 10,
            "origin": origin,
            "destination": destination,
        })
    return journeys


def get_simulated_delay(journey_id: str, seed_offset: int = 0) -> int:
    """
    Geef een gesimuleerde vertraging terug in minuten.
    Gebruikt de journey_id als seed zodat de waarde consistent is per rit,
    maar varieert per aanroep door seed_offset.
    """
    rng = random.Random(hash(journey_id) + seed_offset)
    # ~60% op tijd, ~30% licht vertraagd, ~10% fors vertraagd
    roll = rng.random()
    if roll < 0.60:
        return 0
    elif roll < 0.80:
        return rng.randint(1, 5)
    elif roll < 0.95:
        return rng.randint(6, 15)
    else:
        return rng.randint(16, 45)


def get_alternative_journey(original: dict, delay_min: int) -> dict | None:
    """
    Geef een alternatieve rit terug als de vertraging groter is dan 10 minuten.
    """
    if delay_min < 10:
        return None
    dep = original["departure"] + timedelta(minutes=delay_min + 15)
    arr = dep + timedelta(minutes=original["duration_min"] + 10)
    h, m = divmod(original["duration_min"] + 10, 60)
    alt_num = int(original["train"].split()[-1]) + 2 if original["train"].split()[-1].isdigit() else 999
    return {
        **original,
        "id": original["id"] + "-alt",
        "train": f"{original['type']} {alt_num}",
        "departure": dep,
        "arrival": arr,
        "duration": f"{h}u {m:02d}m",
        "platform": str(random.randint(1, 14)),
        "is_alternative": True,
    }


STOP_POSITIONS = {
    # Gebruik bij voortgangsindicator
    "Amsterdam Centraal": 0,
    "Utrecht Centraal": 1,
    "Arnhem Centraal": 2,
    "Oberhausen": 3,
    "Duisburg": 4,
    "Düsseldorf": 5,
    "Köln Hbf": 6,
    "Dortmund Hbf": 7,
    "Hannover Hbf": 8,
    "Berlin Hbf": 9,
    "Hamburg Hbf": 9,
    "Frankfurt(Main)Hbf": 6,
    "Nürnberg Hbf": 7,
    "München Hbf": 9,
    "Erfurt Hbf": 7,
}
