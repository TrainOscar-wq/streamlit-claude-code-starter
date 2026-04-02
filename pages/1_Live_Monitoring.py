"""
RailGuard — Live Monitoring
Volg je actieve reizen in real-time met actuele DB-vertragingsdata.
Databron: https://v6.db.transport.rest
"""

from datetime import datetime, timedelta

import streamlit as st

from utils.db_api import (
    build_booking_deeplink,
    build_realtime_status_url,
    get_live_delay_for_journey,
    get_trip_details,
    is_connected,
)
from utils.mock_data import get_simulated_delay, get_alternative_journey, get_journeys
from utils.translations import t

st.set_page_config(
    page_title="RailGuard — Live Monitoring",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state ─────────────────────────────────────────────────────────────

if "language" not in st.session_state:
    st.session_state.language = "nl"
if "saved_trips" not in st.session_state:
    st.session_state.saved_trips = []
if "refresh_count" not in st.session_state:
    st.session_state.refresh_count = 0

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
.status-dot-green  { display:inline-block; width:10px; height:10px; border-radius:50%;
                     background:#27ae60; margin-right:6px; animation:pulse-green 2s infinite; }
.status-dot-orange { display:inline-block; width:10px; height:10px; border-radius:50%;
                     background:#e67e22; margin-right:6px; animation:pulse-orange 1.5s infinite; }
.status-dot-red    { display:inline-block; width:10px; height:10px; border-radius:50%;
                     background:#e74c3c; margin-right:6px; animation:pulse-red 1s infinite; }
@keyframes pulse-green  { 0%,100%{opacity:1} 50%{opacity:0.5} }
@keyframes pulse-orange { 0%,100%{opacity:1} 50%{opacity:0.4} }
@keyframes pulse-red    { 0%,100%{opacity:1} 50%{opacity:0.3} }

.delay-zero   { color:#27ae60; font-weight:700; font-size:1.05rem; }
.delay-low    { color:#e67e22; font-weight:700; font-size:1.05rem; }
.delay-high   { color:#e74c3c; font-weight:700; font-size:1.05rem; }
.delay-cancel { color:#7b2d8b; font-weight:700; font-size:1.05rem; }

.connection-green  { background:#d4edda; border:1px solid #c3e6cb; color:#155724;
                     padding:6px 14px; border-radius:6px; font-size:0.88rem; font-weight:600; }
.connection-orange { background:#fff3cd; border:1px solid #ffc107; color:#856404;
                     padding:6px 14px; border-radius:6px; font-size:0.88rem; font-weight:600; }
.connection-red    { background:#f8d7da; border:1px solid #f5c6cb; color:#721c24;
                     padding:6px 14px; border-radius:6px; font-size:0.88rem; font-weight:600; }

.alt-card { border:2px solid #1B4F8A; border-radius:8px; padding:14px 18px;
            background:#f0f4f8; margin-top:10px; }
.alt-card h5 { color:#1B4F8A; margin:0 0 8px 0; }

.train-badge     { display:inline-block; background:#1B4F8A; color:white;
                   padding:2px 10px; border-radius:20px; font-size:0.8rem;
                   font-weight:600; margin-right:6px; }
.train-badge-ice { background:#c0392b; }
.train-badge-ic  { background:#2980b9; }

.progress-bar-bg   { background:#e0e0e0; border-radius:4px; height:8px;
                     overflow:hidden; margin:6px 0; }
.progress-bar-fill { background:linear-gradient(90deg,#1B4F8A,#3498db);
                     height:100%; border-radius:4px; }

.source-live { background:#d4edda; color:#155724; padding:2px 8px;
               border-radius:4px; font-size:0.75rem; font-weight:600; }
.source-demo { background:#fff3cd; color:#856404; padding:2px 8px;
               border-radius:4px; font-size:0.75rem; }

.stopover-passed { color:#aaa; }
.stopover-current { color:#1B4F8A; font-weight:700; }
.stopover-future  { color:#333; }

hr.rg-divider { border:none; border-top:1px solid #dde3ec; margin:16px 0; }
</style>
""", unsafe_allow_html=True)


# ── Helper functies ───────────────────────────────────────────────────────────

def delay_css_class(delay: int) -> str:
    if delay >= 999:
        return "delay-cancel"
    if delay == 0:
        return "delay-zero"
    if delay <= 5:
        return "delay-low"
    return "delay-high"


def connection_status(buffer_min: int, delay: int) -> tuple[str, str]:
    remaining = buffer_min - delay
    if remaining >= 8:
        return t("connection_safe"), "connection-green"
    elif remaining >= 0:
        return t("connection_tight"), "connection-orange"
    else:
        return t("connection_missed"), "connection-red"


def journey_progress(journey: dict, delay_min: int) -> float:
    now = datetime.now()
    dep = journey["departure"]
    arr = journey["arrival"] + timedelta(minutes=delay_min)
    total = (arr - dep).total_seconds()
    if total <= 0:
        return 1.0
    elapsed = (now - dep).total_seconds()
    return max(0.0, min(1.0, elapsed / total))


def next_stop_estimate(journey: dict, progress: float) -> str:
    stops = journey.get("stops", [])
    if not stops:
        return "—"
    idx = min(int(progress * len(stops)), len(stops) - 1)
    if idx < len(stops) - 1:
        return stops[idx + 1]
    return stops[-1]


def fetch_delay(journey: dict) -> tuple[int | None, bool]:
    """
    Haal actuele vertraging op via de DB transport API.
    Returns (delay_min, is_live).
      delay_min = None als er geen live data beschikbaar is.
    Er wordt GEEN gesimuleerde fallback gebruikt.
    """
    delay_min, is_live, _ = get_live_delay_for_journey(journey)
    if is_live:
        return delay_min, True
    return None, False


def render_stopover_timeline(trip_id: str, journey: dict) -> None:
    """Toon de volledige route met actuele tijden per halte (via trips API)."""
    trip = get_trip_details(trip_id)
    stopovers = trip.get("stopovers", [])
    if not stopovers:
        return

    now = datetime.now()
    st.markdown("**📍 Route & actuele haltetijden**" if st.session_state.language == "nl"
                else "**📍 Route & live stop times**")

    rows = []
    for sv in stopovers:
        stop_name = (sv.get("stop") or {}).get("name", "?")
        planned = sv.get("plannedDeparture") or sv.get("plannedArrival") or ""
        actual  = sv.get("departure") or sv.get("arrival") or planned
        delay_s = sv.get("departureDelay") or sv.get("arrivalDelay") or 0
        cancelled = sv.get("cancelled", False)

        # Bepaal of halte al gepasseerd is
        try:
            actual_dt = datetime.fromisoformat(actual.replace("Z", "+00:00")).replace(tzinfo=None)
            passed = actual_dt < now
        except Exception:
            passed = False

        css = "stopover-passed" if passed else "stopover-current" if not passed and rows else "stopover-future"
        delay_str = ""
        if cancelled:
            delay_str = ' <span style="color:#7b2d8b;font-size:0.75rem">Opgeheven</span>'
        elif delay_s and delay_s > 0:
            delay_str = f' <span style="color:#e74c3c;font-size:0.75rem">+{delay_s//60}min</span>'

        time_str = actual[11:16] if len(actual) >= 16 else "—"
        rows.append(
            f'<span class="{css}">{"✓ " if passed else "● "}{stop_name}</span>'
            f' <span style="color:#888;font-size:0.82rem">{time_str}</span>{delay_str}'
        )

    # Toon maximaal 8 haltes rondom de huidige positie
    st.markdown(
        '<div style="font-size:0.88rem;line-height:2">' +
        "<br>".join(rows[:12]) +
        ("..." if len(rows) > 12 else "") +
        "</div>",
        unsafe_allow_html=True,
    )


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

    st.markdown("---")
    api_ok = is_connected()
    if api_ok:
        st.markdown('<span class="source-live">✅ DB transport API live</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="source-demo">⚠️ API niet bereikbaar — demo</span>', unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown(
    '<div style="font-size:2rem;font-weight:800;color:#1B4F8A;letter-spacing:-1px">📡 RailGuard</div>'
    f'<div style="color:#555;font-size:0.95rem">{t("live_subtitle")}</div>',
    unsafe_allow_html=True,
)
st.markdown('<hr class="rg-divider">', unsafe_allow_html=True)

col_title, col_refresh = st.columns([4, 1])
with col_title:
    st.subheader(f"📡 {t('live_title')}")
with col_refresh:
    if st.button(f"🔄 {t('refresh_button')}", use_container_width=True):
        st.session_state.refresh_count += 1
        # Wis cache zodat nieuwe data opgehaald wordt
        get_live_delay_for_journey.clear() if hasattr(get_live_delay_for_journey, "clear") else None
        st.rerun()

st.caption(f"{t('last_updated')}: {datetime.now().strftime('%H:%M:%S')}")

# ── Geen reizen ───────────────────────────────────────────────────────────────

if not st.session_state.saved_trips:
    st.info(t("no_active_trips"), icon="ℹ️")
    if st.button(f"→ {t('go_to_planner')}", type="primary"):
        st.switch_page("Home.py")
    st.stop()

# ── Reis-kaarten ──────────────────────────────────────────────────────────────

for journey in st.session_state.saved_trips:
    dep: datetime = journey["departure"]
    arr: datetime = journey["arrival"]
    now = datetime.now()

    # Live vertraging ophalen (None = geen data)
    delay, is_live = fetch_delay(journey)

    # Geannuleerd?
    is_cancelled = delay is not None and delay >= 999

    # Tijdsstatus (bij geen data: gebruik geplande tijden)
    effective_delay = delay if (delay is not None and not is_cancelled) else 0
    is_future = dep > now
    is_past   = (arr + timedelta(minutes=min(effective_delay, 120))) < now
    is_active = not is_future and not is_past

    progress = journey_progress(journey, effective_delay) if is_active else (0.0 if is_future else 1.0)
    next_stp = next_stop_estimate(journey, progress) if is_active else ""

    train_type = journey["type"].upper()
    badge_cls = (
        "train-badge-ice" if "ICE" in train_type
        else "train-badge-ic" if "IC" in train_type
        else ""
    )

    with st.container(border=True):
        # ── Rij 1: trein + databron + status + verwijder ─────────────────
        r1, r2, r3, r4 = st.columns([3, 1, 1, 1])
        with r1:
            st.markdown(
                f'<span class="train-badge {badge_cls}">{journey["train"]}</span>'
                f'<strong>{journey["origin"]}</strong> → <strong>{journey["destination"]}</strong>',
                unsafe_allow_html=True,
            )
        with r2:
            source_label = (
                '<span class="source-live">📡 Live</span>'
                if is_live
                else '<span class="source-demo">🔄 Demo</span>'
            )
            st.markdown(source_label, unsafe_allow_html=True)
        with r3:
            if is_cancelled:
                st.markdown("🚫 **Opgeheven**")
            elif is_future:
                st.markdown("🕐 **Gepland**")
            elif is_past:
                st.markdown("✅ **Aangekomen**")
            else:
                dot_cls = (
                    "status-dot-green"  if delay == 0
                    else "status-dot-orange" if delay <= 10
                    else "status-dot-red"
                )
                st.markdown(f'<span class="{dot_cls}"></span>**Live**', unsafe_allow_html=True)
        with r4:
            if st.button("🗑️", key=f"del_{journey['id']}", help="Verwijder reis"):
                st.session_state.saved_trips = [
                    j for j in st.session_state.saved_trips if j["id"] != journey["id"]
                ]
                st.toast("Reis verwijderd", icon="🗑️")
                st.rerun()

        # ── Rij 2: metrics ────────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        actual_dep_dt = dep + timedelta(minutes=effective_delay)
        actual_arr_dt = arr + timedelta(minutes=effective_delay)

        with c1:
            st.metric(
                t("departure"),
                actual_dep_dt.strftime("%H:%M"),
                delta=f"+{effective_delay} min" if effective_delay > 0 and not is_cancelled else None,
                delta_color="inverse",
            )
        with c2:
            st.metric(
                t("arrival"),
                actual_arr_dt.strftime("%H:%M"),
                delta=f"+{effective_delay} min" if effective_delay > 0 and not is_cancelled else None,
                delta_color="inverse",
            )
        with c3:
            st.markdown(f"**{t('delay_label')}**")
            if delay is None:
                st.markdown(
                    '<span style="color:#888;font-size:0.9rem">⚫ Geen live data</span>',
                    unsafe_allow_html=True,
                )
            elif is_cancelled:
                st.markdown('<span class="delay-cancel">🚫 Opgeheven</span>', unsafe_allow_html=True)
            elif delay == 0:
                st.markdown(f'<span class="delay-zero">✅ {t("on_time")}</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="{delay_css_class(delay)}">⏱ +{delay} {t("minutes_delay")}</span>', unsafe_allow_html=True)
        with c4:
            st.metric("Reistijd", journey["duration"])

        # ── Voortgangsbalk (alleen bij live data) ─────────────────────────
        if is_active and is_live and not is_cancelled:
            st.markdown(f"**{t('journey_progress')}**")
            pct = int(progress * 100)
            st.markdown(
                f'<div class="progress-bar-bg">'
                f'<div class="progress-bar-fill" style="width:{pct}%"></div>'
                f'</div>'
                f'<span style="font-size:0.8rem;color:#888">{pct}% — '
                f'{t("next_stop")}: <strong>{next_stp}</strong></span>',
                unsafe_allow_html=True,
            )

        # ── Overstapindicator ──────────────────────────────────────────────
        if journey.get("transfers", 0) > 0 and journey.get("transfer_station") and journey.get("destination"):
            transfer_station = journey["transfer_station"]
            destination = journey["destination"]
            buffer = journey.get("transfer_buffer_min", 0)

            if delay is not None and buffer > 0:
                conn_label, conn_cls = connection_status(buffer, effective_delay)
                remaining = buffer - effective_delay
                connection_missed = remaining < 0
                st.markdown(
                    f'<div class="{conn_cls}" style="display:inline-block;margin-top:8px">'
                    f'🔄 {transfer_station} — {conn_label}'
                    + (f' ({remaining} {t("minutes")} buffer)' if remaining > 0 else "")
                    + '</div>',
                    unsafe_allow_html=True,
                )
            else:
                # Geen live data: toon neutrale indicator
                connection_missed = False
                st.markdown(
                    f'<div style="display:inline-block;margin-top:8px;background:#f0f4f8;'
                    f'border:1px solid #dde3ec;padding:6px 14px;border-radius:6px;font-size:0.88rem">'
                    f'🔄 Overstap in {transfer_station}</div>',
                    unsafe_allow_html=True,
                )

            # Alternatieve verbindingen vanaf overstapstation — ALTIJD tonen
            transfer_search_from = now + timedelta(minutes=max(0, effective_delay))
            alt_journeys = get_journeys(transfer_station, destination, transfer_search_from)

            if connection_missed:
                expander_label = f"🚨 Overstap gemist — Alternatieven vanaf {transfer_station}"
            else:
                expander_label = f"🔄 Alternatieven bij overstap in {transfer_station} → {destination}"

            with st.expander(expander_label, expanded=connection_missed):
                if connection_missed:
                    st.markdown(
                        f"Je mist waarschijnlijk je overstap in **{transfer_station}**. "
                        f"Eerstvolgende verbindingen naar **{destination}**:"
                    )
                else:
                    st.markdown(
                        f"Eerstvolgende verbindingen vanaf **{transfer_station}** naar **{destination}**:"
                    )
                if alt_journeys:
                    for alt_j in alt_journeys[:2]:
                        alt_dep_dt: datetime = alt_j["departure"]
                        alt_arr_dt: datetime = alt_j["arrival"]
                        alt_b = (
                            "train-badge-ice" if "ICE" in alt_j["type"].upper()
                            else "train-badge-ic" if "IC" in alt_j["type"].upper()
                            else ""
                        )
                        st.markdown(
                            f'<div class="alt-card">'
                            f'<span class="train-badge {alt_b}">{alt_j["train"]}</span>'
                            f'<strong>{alt_dep_dt.strftime("%H:%M")}</strong>'
                            f' → <strong>{alt_arr_dt.strftime("%H:%M")}</strong>'
                            f'<span style="color:#888;font-size:0.85rem;margin-left:10px">'
                            f'{alt_j["duration"]} · €{alt_j["price_eur"]}</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                        st.link_button(
                            f"🎟️ Boek {alt_j['train']} via DB",
                            url=build_booking_deeplink(transfer_station, destination, alt_dep_dt),
                            key=f"alt_{journey['id']}_{alt_j['id']}",
                        )
                else:
                    st.info(f"Geen verbindingen gevonden van {transfer_station} naar {destination}.")

        # ── Alternatief volledige reis bij vertraging (geen overstap) ────
        elif delay is not None and (effective_delay >= 10 or is_cancelled) and is_active:
            alt = get_alternative_journey(journey, effective_delay)
            if alt:
                with st.expander(
                    f"⚡ {t('alternative_available')} — {t('show_alternative')}",
                    expanded=True,
                ):
                    alt_dep: datetime = alt["departure"]
                    alt_arr: datetime = alt["arrival"]
                    alt_badge = (
                        "train-badge-ice" if "ICE" in alt["type"].upper()
                        else "train-badge-ic" if "IC" in alt["type"].upper()
                        else ""
                    )
                    st.markdown(
                        f'<div class="alt-card">'
                        f'<h5>🔁 Alternatieve route</h5>'
                        f'<span class="train-badge {alt_badge}">{alt["train"]}</span>'
                        f'<strong>{alt_dep.strftime("%H:%M")}</strong>'
                        f' → <strong>{alt_arr.strftime("%H:%M")}</strong>'
                        f'<br><span style="font-size:0.85rem;color:#555">'
                        f'{alt["origin"]} → {alt["destination"]} · {alt["duration"]}'
                        f'</span></div>',
                        unsafe_allow_html=True,
                    )
                    st.link_button(
                        f"🎟️ {t('book_button')}",
                        url=build_booking_deeplink(alt["origin"], alt["destination"], alt["departure"]),
                    )

        # ── Halte-tijdlijn (alleen live + actief) ─────────────────────────
        if is_active and is_live:
            _, __, trip_id = get_live_delay_for_journey(journey)
            if trip_id:
                with st.expander("📍 Bekijk alle haltes & actuele tijden", expanded=False):
                    render_stopover_timeline(trip_id, journey)

        # ── Link naar bahnstatus.de ───────────────────────────────────────
        st.markdown(
            f'<a href="{build_realtime_status_url(journey["train"], dep)}" '
            f'target="_blank" style="font-size:0.82rem;color:#1B4F8A">'
            f'🔗 Live status op der-bahnstatus.de</a>',
            unsafe_allow_html=True,
        )

st.markdown('<hr class="rg-divider">', unsafe_allow_html=True)

is_nl = st.session_state.language == "nl"
st.caption(
    "Live data: v6.db.transport.rest (DB Fahrplan) · Geen authenticatie vereist · "
    "Vertraging in seconden omgezet naar minuten · Demo-modus bij geen API-verbinding."
    if is_nl else
    "Live data: v6.db.transport.rest (DB Fahrplan) · No authentication required · "
    "Delay in seconds converted to minutes · Demo mode when API is unreachable."
)
