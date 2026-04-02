"""
Vertalingen voor RailGuard — NL en EN.
"""

STRINGS = {
    # ── App-wide ──────────────────────────────────────────────────────────────
    "app_name": {"nl": "RailGuard", "en": "RailGuard"},
    "tagline": {
        "nl": "Slim Europees treinreizen — altijd op tijd, altijd een alternatief",
        "en": "Smart European train travel — always on time, always an alternative",
    },
    "language_label": {"nl": "Taal", "en": "Language"},

    # ── Navigation ────────────────────────────────────────────────────────────
    "nav_home": {"nl": "Reisplanner", "en": "Trip Planner"},
    "nav_live": {"nl": "Live monitoring", "en": "Live Monitoring"},
    "nav_trips": {"nl": "Mijn reizen", "en": "My Trips"},
    "nav_about": {"nl": "Over RailGuard", "en": "About RailGuard"},

    # ── Search form ───────────────────────────────────────────────────────────
    "search_title": {"nl": "Plan je reis", "en": "Plan your trip"},
    "from_label": {"nl": "Van", "en": "From"},
    "to_label": {"nl": "Naar", "en": "To"},
    "date_label": {"nl": "Datum", "en": "Date"},
    "time_label": {"nl": "Vertrektijd", "en": "Departure time"},
    "search_button": {"nl": "Zoek reizen", "en": "Search trips"},
    "from_placeholder": {"nl": "Bijv. Amsterdam Centraal", "en": "E.g. Amsterdam Centraal"},
    "to_placeholder": {"nl": "Bijv. Berlin Hbf", "en": "E.g. Berlin Hbf"},

    # ── Results ───────────────────────────────────────────────────────────────
    "results_title": {"nl": "Reisopties", "en": "Journey options"},
    "no_results": {"nl": "Geen reizen gevonden. Probeer een andere datum of bestemming.", "en": "No journeys found. Try a different date or destination."},
    "duration_label": {"nl": "Reistijd", "en": "Duration"},
    "transfers_label": {"nl": "Overstappen", "en": "Transfers"},
    "transfer_singular": {"nl": "overstap", "en": "transfer"},
    "transfer_plural": {"nl": "overstappen", "en": "transfers"},
    "no_transfer": {"nl": "Rechtstreeks", "en": "Direct"},
    "book_button": {"nl": "Boek via DB", "en": "Book via DB"},
    "save_trip_button": {"nl": "Bewaar reis", "en": "Save trip"},
    "trip_saved": {"nl": "Reis opgeslagen!", "en": "Trip saved!"},
    "already_saved": {"nl": "Al opgeslagen", "en": "Already saved"},
    "platform_label": {"nl": "Spoor", "en": "Platform"},
    "price_from": {"nl": "Vanaf", "en": "From"},

    # ── Journey card details ───────────────────────────────────────────────────
    "departure": {"nl": "Vertrek", "en": "Departure"},
    "arrival": {"nl": "Aankomst", "en": "Arrival"},
    "train_type": {"nl": "Trein", "en": "Train"},
    "via_label": {"nl": "Via", "en": "Via"},
    "operator": {"nl": "Vervoerder", "en": "Operator"},

    # ── Live monitoring ───────────────────────────────────────────────────────
    "live_title": {"nl": "Live monitoring", "en": "Live Monitoring"},
    "live_subtitle": {"nl": "Volg je actieve en geplande reizen in real-time.", "en": "Track your active and upcoming journeys in real time."},
    "no_active_trips": {"nl": "Je hebt nog geen reizen opgeslagen. Zoek een reis en bewaar hem om hem hier te volgen.", "en": "You have no saved trips yet. Search for a journey and save it to track it here."},
    "status_label": {"nl": "Status", "en": "Status"},
    "delay_label": {"nl": "Vertraging", "en": "Delay"},
    "on_time": {"nl": "Op tijd", "en": "On time"},
    "delayed": {"nl": "Vertraagd", "en": "Delayed"},
    "cancelled": {"nl": "Opgeheven", "en": "Cancelled"},
    "connection_safe": {"nl": "Overstap veilig", "en": "Connection safe"},
    "connection_tight": {"nl": "Overstap krap", "en": "Connection tight"},
    "connection_missed": {"nl": "Overstap gemist", "en": "Connection missed"},
    "alternative_available": {"nl": "Alternatief beschikbaar", "en": "Alternative available"},
    "show_alternative": {"nl": "Toon alternatief", "en": "Show alternative"},
    "refresh_button": {"nl": "Vernieuwen", "en": "Refresh"},
    "last_updated": {"nl": "Laatst bijgewerkt", "en": "Last updated"},
    "journey_progress": {"nl": "Reisvoortgang", "en": "Journey progress"},
    "current_position": {"nl": "Huidige positie", "en": "Current position"},
    "next_stop": {"nl": "Volgende halte", "en": "Next stop"},
    "minutes_delay": {"nl": "min vertraging", "en": "min delay"},
    "minutes": {"nl": "minuten", "en": "minutes"},
    "buffer_time": {"nl": "Buffertijd overstap", "en": "Transfer buffer"},

    # ── My trips ──────────────────────────────────────────────────────────────
    "trips_title": {"nl": "Mijn reizen", "en": "My Trips"},
    "trips_subtitle": {"nl": "Je opgeslagen reizen en boekingshistorie.", "en": "Your saved trips and booking history."},
    "no_saved_trips": {"nl": "Nog geen reizen opgeslagen. Gebruik de reisplanner om een reis te zoeken en op te slaan.", "en": "No trips saved yet. Use the trip planner to search for and save a journey."},
    "upcoming_trips": {"nl": "Komende reizen", "en": "Upcoming trips"},
    "past_trips": {"nl": "Afgelopen reizen", "en": "Past trips"},
    "remove_trip": {"nl": "Verwijder", "en": "Remove"},
    "trip_removed": {"nl": "Reis verwijderd", "en": "Trip removed"},
    "monitor_trip": {"nl": "Volg live", "en": "Track live"},

    # ── About ─────────────────────────────────────────────────────────────────
    "about_title": {"nl": "Over RailGuard", "en": "About RailGuard"},
    "about_subtitle": {"nl": "Slim Europees treinreizen", "en": "Smart European train travel"},
    "about_vision": {
        "nl": "RailGuard lost het grootste pijnpunt van treinreizigers op: wat doe je als je je overstap mist? Wij monitoren je reis live en tonen automatisch alternatieven.",
        "en": "RailGuard solves the biggest pain point for train travellers: what do you do when you miss a connection? We monitor your journey live and automatically show alternatives.",
    },
    "pilot_notice": {
        "nl": "Dit is een pilotversie. Realtime data is afkomstig van de DB (Deutsche Bahn) API. Boekingen worden doorgestuurd naar de website van de vervoerder.",
        "en": "This is a pilot version. Real-time data is sourced from the DB (Deutsche Bahn) API. Bookings are redirected to the carrier's website.",
    },
    "features_title": {"nl": "Functionaliteiten", "en": "Features"},
    "roadmap_title": {"nl": "Roadmap", "en": "Roadmap"},
    "data_sources": {"nl": "Databronnen", "en": "Data sources"},

    # ── Status/feedback ───────────────────────────────────────────────────────
    "api_connected": {"nl": "DB API verbonden", "en": "DB API connected"},
    "api_demo_mode": {"nl": "Demo-modus (geen API-sleutel)", "en": "Demo mode (no API key)"},
    "loading": {"nl": "Laden...", "en": "Loading..."},
    "error_api": {"nl": "API fout — demodata wordt gebruikt.", "en": "API error — using demo data."},
    "go_to_planner": {"nl": "Ga naar reisplanner", "en": "Go to trip planner"},
    "arrival_guarantee": {"nl": "Aankomstgarantie", "en": "Arrival Guarantee"},
    "arrival_guarantee_desc": {
        "nl": "Voeg een aankomstgarantie toe voor €2–5. Als je door vertraging je eindbestemming niet op tijd bereikt, regelen wij compensatie of een alternatief ticket. (Premium — binnenkort beschikbaar)",
        "en": "Add an arrival guarantee for €2–5. If you miss your destination due to a delay, we arrange compensation or an alternative ticket. (Premium — coming soon)",
    },
}


def t(key: str, lang: str | None = None) -> str:
    """Vertaal een sleutel naar de huidige taal."""
    import streamlit as st
    if lang is None:
        lang = st.session_state.get("language", "nl")
    entry = STRINGS.get(key)
    if entry is None:
        return key
    return entry.get(lang, entry.get("nl", key))
