"""
RailGuard — Reisplanner
Startpagina: zoek treinverbindingen en bekijk reisopties.
"""

from datetime import datetime, date, time, timedelta

import streamlit as st

from utils.db_api import (
    build_booking_deeplink,
    is_connected,
    search_journeys,
    parse_api_journey,
    STATION_IDS,
)
from utils.mock_data import get_journeys, POPULAR_STATIONS
from utils.translations import t

# ── Paginaconfiguratie ────────────────────────────────────────────────────────

st.set_page_config(
    page_title="RailGuard — Reisplanner",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state initialisatie ───────────────────────────────────────────────

if "language" not in st.session_state:
    st.session_state.language = "nl"
if "saved_trips" not in st.session_state:
    st.session_state.saved_trips = []
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "last_search" not in st.session_state:
    st.session_state.last_search = {}

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
.rg-logo    { font-size:2rem; font-weight:800; color:#1B4F8A; letter-spacing:-1px; }
.rg-tagline { color:#555; font-size:0.95rem; margin-top:-4px; }

.journey-card {
    border:1px solid #dde3ec; border-radius:10px; padding:16px 20px;
    margin-bottom:4px; background:#fff;
    box-shadow:0 1px 4px rgba(0,0,0,0.06);
}
.train-badge     { display:inline-block; background:#1B4F8A; color:white;
                   padding:2px 10px; border-radius:20px; font-size:0.8rem;
                   font-weight:600; margin-right:8px; }
.train-badge-ice { background:#c0392b; }
.train-badge-ic  { background:#2980b9; }
.train-badge-re  { background:#27ae60; }

.time-big      { font-size:1.55rem; font-weight:700; color:#1A1A2E; }
.duration-pill { background:#f0f4f8; border-radius:20px; padding:3px 12px;
                 font-size:0.85rem; color:#555; font-weight:500; }
.price-tag     { font-size:1.3rem; font-weight:700; color:#1B4F8A; }
.stops-list    { font-size:0.8rem; color:#888; margin-top:4px; }

.platform-badge { background:#fff3cd; border:1px solid #ffc107; color:#856404;
                  padding:2px 8px; border-radius:4px; font-size:0.8rem; font-weight:600; }
.transfer-badge { background:#e8f4fd; border:1px solid #bee3f8; color:#2b6cb0;
                  padding:2px 8px; border-radius:4px; font-size:0.8rem; }
.direct-badge   { background:#d4edda; border:1px solid #c3e6cb; color:#155724;
                  padding:2px 8px; border-radius:4px; font-size:0.8rem; }

.api-badge-ok   { background:#d4edda; color:#155724; padding:3px 10px;
                  border-radius:20px; font-size:0.78rem; }
.api-badge-demo { background:#fff3cd; color:#856404; padding:3px 10px;
                  border-radius:20px; font-size:0.78rem; }

.guarantee-box {
    background:linear-gradient(135deg,#1B4F8A 0%,#2980b9 100%);
    color:white; border-radius:10px; padding:16px 20px; margin-top:12px;
}
.guarantee-box h4 { color:white; margin:0 0 6px 0; }
.guarantee-box p  { color:rgba(255,255,255,0.85); font-size:0.88rem; margin:0; }

hr.rg-divider { border:none; border-top:1px solid #dde3ec; margin:18px 0; }
</style>
""", unsafe_allow_html=True)


# ── Helper: reis-kaart renderen ───────────────────────────────────────────────

def render_journey_card(journey: dict) -> None:
    dep: datetime = journey["departure"]
    arr: datetime = journey["arrival"]
    train_type = journey["type"].upper()
    badge_class = (
        "train-badge-ice" if "ICE" in train_type
        else "train-badge-ic" if "IC" in train_type
        else "train-badge-re"
    )

    stops_preview = " → ".join(journey["stops"][:3])
    if len(journey["stops"]) > 3:
        stops_preview += f" … {journey['stops'][-1]}"

    already_saved = any(s["id"] == journey["id"] for s in st.session_state.saved_trips)

    # Card container
    with st.container(border=True):
        top_left, top_right = st.columns([3, 1])
        with top_left:
            st.markdown(
                f'<span class="train-badge {badge_class}">{journey["train"]}</span>'
                f'<span style="color:#888;font-size:0.85rem">{journey["operator"]}</span>',
                unsafe_allow_html=True,
            )
            if journey["transfers"] == 0:
                badge = f'<span class="direct-badge">{t("no_transfer")}</span>'
            else:
                label = t("transfer_singular") if journey["transfers"] == 1 else t("transfer_plural")
                extra = f' — {journey["transfer_station"]}' if journey.get("transfer_station") else ""
                badge = f'<span class="transfer-badge">{journey["transfers"]} {label}{extra}</span>'
            st.markdown(badge, unsafe_allow_html=True)

        with top_right:
            st.markdown(
                f'<div style="text-align:right">'
                f'<span class="price-tag">€{journey["price_eur"]}</span><br>'
                f'<span style="color:#888;font-size:0.78rem">{t("price_from")}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        col_dep, col_mid, col_arr = st.columns([2, 1, 2])
        with col_dep:
            st.markdown(
                f'<span class="time-big">{dep.strftime("%H:%M")}</span><br>'
                f'<span style="font-size:0.85rem;color:#555">{journey["origin"]}</span><br>'
                f'<span class="platform-badge">{t("platform_label")} {journey["platform"]}</span>',
                unsafe_allow_html=True,
            )
        with col_mid:
            st.markdown(
                f'<div style="text-align:center;padding-top:10px">'
                f'<div style="font-size:1.4rem;color:#1B4F8A">→</div>'
                f'<span class="duration-pill">{journey["duration"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with col_arr:
            st.markdown(
                f'<span class="time-big">{arr.strftime("%H:%M")}</span><br>'
                f'<span style="font-size:0.85rem;color:#555">{journey["destination"]}</span>',
                unsafe_allow_html=True,
            )

        st.markdown(
            f'<div class="stops-list">📍 {stops_preview}</div>',
            unsafe_allow_html=True,
        )

        # Knoppen onder de kaart
        btn1, btn2, _ = st.columns([2, 2, 3])
        with btn1:
            booking_url = build_booking_deeplink(
                journey["origin"],
                journey["destination"],
                journey["departure"],
            )
            st.link_button(
                f"🎟️ {t('book_button')}",
                url=booking_url,
                use_container_width=True,
            )
        with btn2:
            if already_saved:
                st.button(
                    f"✅ {t('already_saved')}",
                    key=f"save_{journey['id']}",
                    disabled=True,
                    use_container_width=True,
                )
            else:
                if st.button(
                    f"🔖 {t('save_trip_button')}",
                    key=f"save_{journey['id']}",
                    use_container_width=True,
                ):
                    st.session_state.saved_trips.append(journey)
                    st.toast(t("trip_saved"), icon="✅")
                    st.rerun()


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🚆 RailGuard")
    st.markdown("---")

    lang_options = ["🇳🇱 Nederlands", "🇬🇧 English"]
    current_idx = 0 if st.session_state.language == "nl" else 1
    chosen = st.selectbox(
        t("language_label"),
        lang_options,
        index=current_idx,
        key="lang_selector",
    )
    st.session_state.language = "nl" if "Nederlands" in chosen else "en"

    st.markdown("---")

    api_ok = is_connected()
    if api_ok:
        st.markdown(
            '<span class="api-badge-ok">✅ DB API live — echte tijden</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="api-badge-demo">⚠️ Demo-modus — voorbeelddata</span>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    trips_count = len(st.session_state.saved_trips)
    if trips_count:
        label = "reis" if trips_count == 1 else "reizen"
        st.markdown(f"🗂️ **{trips_count}** {label} opgeslagen")


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown(
    '<div class="rg-logo">🚆 RailGuard</div>'
    f'<div class="rg-tagline">{t("tagline")}</div>',
    unsafe_allow_html=True,
)
st.markdown('<hr class="rg-divider">', unsafe_allow_html=True)

# ── Zoekformulier ─────────────────────────────────────────────────────────────

st.subheader(t("search_title"))

station_names = [s["name"] for s in POPULAR_STATIONS]

col_from, col_to = st.columns(2)
with col_from:
    origin = st.selectbox(
        t("from_label"),
        options=station_names,
        index=0,
        key="origin_select",
    )
with col_to:
    # Zet standaard destination op Berlin Hbf (index 6)
    dest_default = next(
        (i for i, s in enumerate(station_names) if s == "Berlin Hbf"), 6
    )
    destination = st.selectbox(
        t("to_label"),
        options=station_names,
        index=dest_default,
        key="dest_select",
    )

col_date, col_time, col_btn = st.columns([2, 1, 1])
with col_date:
    travel_date = st.date_input(
        t("date_label"),
        value=date.today() + timedelta(days=1),
        min_value=date.today(),
        key="travel_date",
    )
with col_time:
    travel_time = st.time_input(
        t("time_label"),
        value=time(8, 0),
        key="travel_time",
        step=300,
    )
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    search_clicked = st.button(
        f"🔍 {t('search_button')}",
        type="primary",
        use_container_width=True,
    )

# ── Resultaten ────────────────────────────────────────────────────────────────

if search_clicked:
    if origin == destination:
        st.warning(
            "Vertrek- en aankomststation mogen niet hetzelfde zijn."
            if st.session_state.language == "nl"
            else "Departure and destination must be different."
        )
        st.stop()

    departure_dt = datetime.combine(travel_date, travel_time)
    with st.spinner(t("loading")):
        results = []
        source = "demo"

        # Probeer echte DB API
        origin_id = STATION_IDS.get(origin)
        dest_id = STATION_IDS.get(destination)
        if origin_id and dest_id:
            raw = search_journeys(origin_id, dest_id, departure_dt, results=8)
            results = [j for j in (parse_api_journey(r, i) for i, r in enumerate(raw)) if j]
            if results:
                source = "api"

        # Fallback op demodata
        if not results:
            results = get_journeys(origin, destination, departure_dt)

    st.session_state.search_results = results
    st.session_state.search_source = source
    st.session_state.last_search = {
        "origin": origin,
        "destination": destination,
        "departure_dt": departure_dt,
    }

if st.session_state.search_results:
    last = st.session_state.last_search
    st.markdown('<hr class="rg-divider">', unsafe_allow_html=True)
    st.subheader(
        f"{t('results_title')}: **{last.get('origin', '')}** → **{last.get('destination', '')}**"
    )

    for journey in st.session_state.search_results:
        render_journey_card(journey)

    # Aankomstgarantie promo-banner
    st.markdown(
        f'<div class="guarantee-box">'
        f'<h4>🛡️ {t("arrival_guarantee")}</h4>'
        f'<p>{t("arrival_guarantee_desc")}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
