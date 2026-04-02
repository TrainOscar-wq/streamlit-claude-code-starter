"""
RailGuard — Over RailGuard
Uitleg over de app, functies en roadmap.
"""

import streamlit as st
from utils.translations import t

st.set_page_config(
    page_title="RailGuard — Over ons",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "language" not in st.session_state:
    st.session_state.language = "nl"
if "saved_trips" not in st.session_state:
    st.session_state.saved_trips = []

# ── CSS ──────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
.feature-card {
    border:1px solid #dde3ec; border-radius:10px; padding:16px 20px;
    background:#fff; height:100%;
    box-shadow:0 1px 4px rgba(0,0,0,0.05);
}
.feature-card h4 { color:#1B4F8A; margin:0 0 8px 0; }
.feature-card p  { color:#555; font-size:0.9rem; margin:0; }
.roadmap-row {
    display:flex; gap:12px; align-items:flex-start;
    border-left:3px solid #1B4F8A; padding-left:16px; margin-bottom:14px;
}
.roadmap-phase  { font-size:0.75rem; font-weight:700; color:#fff;
                  background:#1B4F8A; padding:2px 8px; border-radius:4px;
                  white-space:nowrap; }
.roadmap-scope  { font-size:0.88rem; color:#333; }
.source-badge   { display:inline-block; background:#f0f4f8;
                  border:1px solid #dde3ec; border-radius:6px;
                  padding:4px 12px; font-size:0.82rem; margin:4px; }
hr.rg-divider { border:none; border-top:1px solid #dde3ec; margin:20px 0; }
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

# ── Header ────────────────────────────────────────────────────────────────────

is_nl = st.session_state.language == "nl"

st.markdown(
    '<div style="font-size:2rem;font-weight:800;color:#1B4F8A;letter-spacing:-1px">🚆 RailGuard</div>'
    f'<div style="color:#555;font-size:0.95rem">{t("tagline")}</div>',
    unsafe_allow_html=True,
)
st.markdown('<hr class="rg-divider">', unsafe_allow_html=True)

# ── Visie ────────────────────────────────────────────────────────────────────

st.subheader("💡 Visie" if is_nl else "💡 Vision")
st.markdown(t("about_vision"))

st.info(t("pilot_notice"), icon="🔬")

st.markdown('<hr class="rg-divider">', unsafe_allow_html=True)

# ── Functies ─────────────────────────────────────────────────────────────────

st.subheader(t("features_title"))

features = [
    ("🔍", "Reisplanning" if is_nl else "Trip Planning",
     "Zoek verbindingen tussen Europese stations met filter op tijd, overstappen en prijs."
     if is_nl else
     "Search connections between European stations, filtered by time, transfers and price."),
    ("📡", "Live Monitoring",
     "Volg je trein in real-time. Ontvang een melding zodra een overstap in gevaar komt."
     if is_nl else
     "Track your train in real time. Get an alert when a connection is at risk."),
    ("🔄", "Automatische alternatieven" if is_nl else "Automatic alternatives",
     "Bij vertraging tonen we direct de volgende beschikbare verbinding, inclusief boekingsknop."
     if is_nl else
     "On delay, we instantly show the next available connection with a booking button."),
    ("🎟️", "Wallet",
     "Alle tickets op één plek — gekocht via RailGuard of extern toegevoegd."
     if is_nl else
     "All tickets in one place — purchased via RailGuard or added externally."),
    ("🛡️", "Aankomstgarantie (binnenkort)" if is_nl else "Arrival Guarantee (coming soon)",
     "Betaal €2–5 per reis voor automatische compensatie bij vertraging."
     if is_nl else
     "Pay €2–5 per journey for automatic compensation on delay."),
    ("🌍", "Multimodaal" if is_nl else "Multimodal",
     "Trein + bus gecombineerd. FlixBus en BlaBlaBus als terugvaloptie."
     if is_nl else
     "Train + bus combined. FlixBus and BlaBlaBus as fallback options."),
]

cols = st.columns(3)
for i, (icon, title, desc) in enumerate(features):
    with cols[i % 3]:
        st.markdown(
            f'<div class="feature-card">'
            f'<h4>{icon} {title}</h4>'
            f'<p>{desc}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
    if (i + 1) % 3 == 0 and i < len(features) - 1:
        cols = st.columns(3)

st.markdown('<hr class="rg-divider">', unsafe_allow_html=True)

# ── Hoe werkt de pilotversie? ────────────────────────────────────────────────

st.subheader("⚙️ Hoe werkt de pilotversie?" if is_nl else "⚙️ How does the pilot work?")

col_left, col_right = st.columns(2)
with col_left:
    st.markdown(
        "**Databron**\n\n"
        "Treindata komt van de [DB Fahrplan API](https://developers.deutschebahn.com/db-api-marketplace/apis/product/fahrplan) (Deutsche Bahn). "
        "In de pilotversie worden realistische voorbeeldroutes getoond wanneer geen API-sleutel geconfigureerd is."
        if is_nl else
        "**Data source**\n\n"
        "Train data comes from the [DB Fahrplan API](https://developers.deutschebahn.com/db-api-marketplace/apis/product/fahrplan) (Deutsche Bahn). "
        "In the pilot, realistic sample routes are shown when no API key is configured."
    )
    st.markdown(
        "**Boekingen**\n\n"
        "Ticketboekingen worden via een deeplink doorgestuurd naar `reiseauskunft.bahn.de` "
        "met het vertrek- en aankomststation en de gewenste tijd vooringevuld."
        if is_nl else
        "**Bookings**\n\n"
        "Ticket bookings are redirected via deeplink to `reiseauskunft.bahn.de` "
        "with departure, destination, and time pre-filled."
    )

with col_right:
    st.markdown(
        "**Vertraging simulatie**\n\n"
        "Live monitoring toont gesimuleerde vertragingen. Koppel de DB API voor echte real-time data."
        if is_nl else
        "**Delay simulation**\n\n"
        "Live monitoring shows simulated delays. Connect the DB API for real real-time data."
    )
    st.markdown(
        "**API-sleutel instellen**\n\n"
        "Vraag een gratis sleutel aan op [developers.deutschebahn.com](https://developers.deutschebahn.com/) "
        "en voeg die toe in `.streamlit/secrets.toml`."
        if is_nl else
        "**Setting up the API key**\n\n"
        "Get a free key at [developers.deutschebahn.com](https://developers.deutschebahn.com/) "
        "and add it to `.streamlit/secrets.toml`."
    )

st.markdown('<hr class="rg-divider">', unsafe_allow_html=True)

# ── Roadmap ──────────────────────────────────────────────────────────────────

st.subheader(t("roadmap_title"))

roadmap = [
    ("MVP · Maand 1–3" if is_nl else "MVP · Month 1–3",
     "NL + DE · Reisplanning, live monitoring, push notificaties · Web + App"
     if is_nl else
     "NL + DE · Trip planning, live monitoring, push notifications · Web + App"),
    ("Beta · Maand 4–6" if is_nl else "Beta · Month 4–6",
     "FR + CH · Ticketboeking via Trainline · Gebruikersaccounts"
     if is_nl else
     "FR + CH · Ticket booking via Trainline · User accounts"),
    ("Groei · Maand 7–12" if is_nl else "Growth · Month 7–12",
     "SP + IT + AT · Aankomstgarantie · Busalternatieven (FlixBus)"
     if is_nl else
     "SP + IT + AT · Arrival Guarantee · Bus alternatives (FlixBus)"),
    ("Scale · Jaar 2" if is_nl else "Scale · Year 2",
     "Heel West-Europa · Eigen risicofonds · B2B partnerships"
     if is_nl else
     "All of Western Europe · Own risk fund · B2B partnerships"),
]

for phase, scope in roadmap:
    st.markdown(
        f'<div class="roadmap-row">'
        f'<span class="roadmap-phase">{phase}</span>'
        f'<span class="roadmap-scope">{scope}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown('<hr class="rg-divider">', unsafe_allow_html=True)

# ── Databronnen ──────────────────────────────────────────────────────────────

st.subheader(t("data_sources"))

sources = [
    "DB REST API (DE)", "NS API / RDT (NL)", "SNCF Open Data (FR)",
    "SBB Open Data (CH)", "ÖBB Fahrplan API (AT)", "Renfe API (ES)",
    "Trenitalia / RFI (IT)", "FlixBus API", "BlaBlaBus API",
    "Trainline API", "Stripe Payments", "Firebase Auth",
    "Mapbox / OpenStreetMap",
]

st.markdown(
    "".join(f'<span class="source-badge">{s}</span>' for s in sources),
    unsafe_allow_html=True,
)

st.markdown('<hr class="rg-divider">', unsafe_allow_html=True)
st.caption(
    "RailGuard — Pilotversie · Gebouwd met Streamlit · Data: Deutsche Bahn API"
    if is_nl else
    "RailGuard — Pilot version · Built with Streamlit · Data: Deutsche Bahn API"
)
