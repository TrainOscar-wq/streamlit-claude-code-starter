"""
RailGuard — Mijn Reizen
Bekijk en beheer je opgeslagen reizen.
"""

from datetime import datetime, timedelta

import streamlit as st

from utils.db_api import build_booking_deeplink
from utils.translations import t

st.set_page_config(
    page_title="RailGuard — Mijn Reizen",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state ────────────────────────────────────────────────────────────

if "language" not in st.session_state:
    st.session_state.language = "nl"
if "saved_trips" not in st.session_state:
    st.session_state.saved_trips = []

# ── CSS ──────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
.trip-row {
    border:1px solid #dde3ec; border-radius:8px; padding:14px 18px;
    margin-bottom:10px; background:#fff;
    box-shadow:0 1px 4px rgba(0,0,0,0.05);
}
.trip-badge-upcoming { background:#1B4F8A; color:white; padding:2px 10px;
                       border-radius:20px; font-size:0.78rem; }
.trip-badge-today    { background:#e67e22; color:white; padding:2px 10px;
                       border-radius:20px; font-size:0.78rem; }
.trip-badge-past     { background:#aaa; color:white; padding:2px 10px;
                       border-radius:20px; font-size:0.78rem; }
.train-badge     { display:inline-block; background:#1B4F8A; color:white;
                   padding:2px 10px; border-radius:20px; font-size:0.8rem;
                   font-weight:600; margin-right:6px; }
.train-badge-ice { background:#c0392b; }
.train-badge-ic  { background:#2980b9; }
hr.rg-divider { border:none; border-top:1px solid #dde3ec; margin:16px 0; }
</style>
""", unsafe_allow_html=True)


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
    trips_count = len(st.session_state.saved_trips)
    if trips_count:
        label = "reis" if trips_count == 1 else "reizen"
        st.markdown(f"🗂️ **{trips_count}** {label} opgeslagen")


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown(
    '<div style="font-size:2rem;font-weight:800;color:#1B4F8A;letter-spacing:-1px">🗂️ RailGuard</div>'
    f'<div style="color:#555;font-size:0.95rem">{t("trips_subtitle")}</div>',
    unsafe_allow_html=True,
)
st.markdown('<hr class="rg-divider">', unsafe_allow_html=True)
st.subheader(t("trips_title"))

# ── Geen reizen ───────────────────────────────────────────────────────────────

if not st.session_state.saved_trips:
    st.info(t("no_saved_trips"), icon="ℹ️")
    if st.button(f"→ {t('go_to_planner')}", type="primary"):
        st.switch_page("Home.py")
    st.stop()

# ── Sorteren: komend / verleden ───────────────────────────────────────────────

now = datetime.now()
upcoming = [j for j in st.session_state.saved_trips if j["departure"] >= now - timedelta(hours=2)]
past = [j for j in st.session_state.saved_trips if j["departure"] < now - timedelta(hours=2)]


def trip_time_badge(journey: dict) -> str:
    dep: datetime = journey["departure"]
    today = datetime.now().date()
    if dep.date() == today:
        return "trip-badge-today", "Vandaag" if st.session_state.language == "nl" else "Today"
    elif dep > now:
        days_left = (dep.date() - today).days
        label = f"Over {days_left} dag{'en' if days_left != 1 else ''}" if st.session_state.language == "nl" else f"In {days_left} day{'s' if days_left != 1 else ''}"
        return "trip-badge-upcoming", label
    else:
        return "trip-badge-past", "Afgelopen" if st.session_state.language == "nl" else "Past"


def render_trip_row(journey: dict, idx: int) -> bool:
    """Render een reis-rij. Geeft True terug als de reis verwijderd moet worden."""
    dep: datetime = journey["departure"]
    arr: datetime = journey["arrival"]
    train_type = journey["type"].upper()
    badge_cls = (
        "train-badge-ice" if "ICE" in train_type
        else "train-badge-ic" if "IC" in train_type
        else ""
    )
    time_badge_cls, time_badge_label = trip_time_badge(journey)

    should_remove = False

    with st.container(border=True):
        left, right = st.columns([4, 1])
        with left:
            st.markdown(
                f'<span class="train-badge {badge_cls}">{journey["train"]}</span>'
                f'<span class="{time_badge_cls}">{time_badge_label}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'**{journey["origin"]}** → **{journey["destination"]}**'
            )
            st.markdown(
                f'🕐 {dep.strftime("%a %d %b %Y, %H:%M")} → {arr.strftime("%H:%M")} '
                f'· {journey["duration"]} · €{journey["price_eur"]}'
            )
            if journey.get("transfers", 0) > 0:
                st.caption(
                    f'Overstap in {journey["transfer_station"]}' if st.session_state.language == "nl"
                    else f'Transfer at {journey["transfer_station"]}'
                )

        with right:
            booking_url = build_booking_deeplink(
                journey["origin"],
                journey["destination"],
                journey["departure"],
            )
            st.link_button("🎟️ Boek", url=booking_url, use_container_width=True)

            # Verwijder-knop
            if st.button(
                f"🗑️ {t('remove_trip')}",
                key=f"remove_{journey['id']}_{idx}",
                use_container_width=True,
            ):
                should_remove = True

    return should_remove


# ── Komende reizen ────────────────────────────────────────────────────────────

if upcoming:
    st.markdown(f"### {t('upcoming_trips')} ({len(upcoming)})")
    to_remove = []
    for i, journey in enumerate(upcoming):
        if render_trip_row(journey, i):
            to_remove.append(journey["id"])
    if to_remove:
        st.session_state.saved_trips = [
            j for j in st.session_state.saved_trips if j["id"] not in to_remove
        ]
        st.toast(t("trip_removed"), icon="🗑️")
        st.rerun()

# ── Afgelopen reizen ──────────────────────────────────────────────────────────

if past:
    st.markdown('<hr class="rg-divider">', unsafe_allow_html=True)
    st.markdown(f"### {t('past_trips')} ({len(past)})")
    to_remove = []
    for i, journey in enumerate(past):
        if render_trip_row(journey, 1000 + i):
            to_remove.append(journey["id"])
    if to_remove:
        st.session_state.saved_trips = [
            j for j in st.session_state.saved_trips if j["id"] not in to_remove
        ]
        st.toast(t("trip_removed"), icon="🗑️")
        st.rerun()

# ── Alles wissen ──────────────────────────────────────────────────────────────

st.markdown('<hr class="rg-divider">', unsafe_allow_html=True)
if st.button(
    "🗑️ Alle reizen wissen" if st.session_state.language == "nl" else "🗑️ Clear all trips",
    type="secondary",
):
    st.session_state.saved_trips = []
    st.toast(
        "Alle reizen gewist." if st.session_state.language == "nl" else "All trips cleared.",
        icon="🗑️",
    )
    st.rerun()
