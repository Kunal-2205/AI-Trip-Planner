"""
streamlit_app.py

Streamlit frontend for the AI Multi-Agent Travel Planner — "Wayfarer" theme
(passport / boarding-pass visual identity).

Run the FastAPI backend first:
    uvicorn app.main:app --reload

Then run this app in a separate terminal:
    streamlit run streamlit_app.py

By default this expects the API at http://localhost:8000.
Change API_BASE_URL below (or set the TRAVEL_PLANNER_API_URL
environment variable) if your backend runs elsewhere.
"""

import os
from datetime import date, timedelta

import requests
import streamlit as st

# --------------------------------------------------------------
# Config
# --------------------------------------------------------------

API_BASE_URL = os.getenv("TRAVEL_PLANNER_API_URL", "http://localhost:8000")
PLAN_TRIP_ENDPOINT = f"{API_BASE_URL}/plan-trip"

st.set_page_config(
    page_title="Wayfarer — AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------
# Theme — fonts + global CSS
# --------------------------------------------------------------

st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">

    <style>
    :root{
        --ink:#12253B;
        --ink-2:#0B1A2B;
        --gold:#C9973B;
        --gold-soft:#E4C077;
        --jade:#1F7A5C;
        --jade-soft:#DCEEE6;
        --rust:#C1502D;
        --rust-soft:#F7E2DA;
        --paper:#F3F1EA;
        --card:#FFFFFF;
        --line:#E4E0D4;
        --text:#1C2431;
        --muted:#6B7280;
    }

    html, body, [data-testid="stAppViewContainer"]{
        background: var(--paper) !important;
        font-family: 'Inter', sans-serif;
        color: var(--text);
    }
    [data-testid="stHeader"]{ background: transparent; }

    h1, h2, h3, h4 { font-family: 'Fraunces', serif !important; letter-spacing: -0.01em; color: var(--ink); }

    /* ---------------- SIDEBAR ---------------- */
    [data-testid="stSidebar"]{
        background: linear-gradient(175deg, var(--ink) 0%, var(--ink-2) 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    [data-testid="stSidebar"] * { color: #EDEEF2; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3{
        color: #fff !important;
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown p{
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #8CA0BD !important;
    }
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea,
    [data-testid="stSidebar"] select,
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="input"]{
        background: rgba(255,255,255,0.05) !important;
        border: none !important;
        border-bottom: 1.5px solid rgba(255,255,255,0.18) !important;
        border-radius: 4px 4px 0 0 !important;
        color: #F3F4F6 !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stSidebar"] input:focus,
    [data-testid="stSidebar"] textarea:focus{
        border-bottom-color: var(--gold) !important;
    }
    [data-testid="stSidebar"] [data-baseweb="tag"]{
        background: var(--gold) !important;
        color: var(--ink-2) !important;
        font-weight: 600;
        border-radius: 100px !important;
    }
    [data-testid="stSidebar"] hr{ border-color: rgba(255,255,255,0.12); }

    /* Sidebar submit button */
    [data-testid="stSidebar"] .stFormSubmitButton button{
        width: 100%;
        background: linear-gradient(135deg, var(--gold-soft), var(--gold)) !important;
        color: var(--ink-2) !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem !important;
        box-shadow: 0 8px 18px rgba(201,151,59,0.28);
        transition: transform .12s ease;
    }
    [data-testid="stSidebar"] .stFormSubmitButton button:hover{ transform: translateY(-1px); }

    /* Brand header block */
    .brand-block{ display:flex; align-items:center; gap:12px; margin-bottom: 8px; }
    .brand-mark{
        width:40px; height:40px; border-radius:10px;
        background: radial-gradient(circle at 30% 20%, var(--gold-soft), var(--gold) 70%);
        display:flex; align-items:center; justify-content:center; font-size:19px;
        box-shadow: 0 4px 10px rgba(201,151,59,0.35);
        flex-shrink:0;
    }
    .brand-title{ font-family:'Fraunces', serif; font-size:20px; color:#fff; font-weight:600; margin:0; }
    .brand-sub{ font-family:'Inter', sans-serif !important; font-size:11.5px !important; color:#9AA7BC !important;
                text-transform:none !important; letter-spacing:0.02em !important; margin:0 !important; }

    /* ---------------- MAIN CONTENT CARDS ---------------- */
    .block-container{ padding-top: 2.2rem; max-width: 1200px; }

    div[data-testid="stMetric"]{
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 14px 16px 10px;
        box-shadow: 0 1px 2px rgba(18,37,59,0.04), 0 8px 24px rgba(18,37,59,0.06);
    }
    div[data-testid="stMetricLabel"]{
        font-family:'IBM Plex Mono', monospace !important;
        text-transform: uppercase; letter-spacing: 0.08em; font-size: 10.5px !important;
        color: var(--muted) !important;
    }
    div[data-testid="stMetricValue"]{
        font-family:'Fraunces', serif !important; color: var(--ink) !important; font-weight:600 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"]{
        background: var(--card);
        border-radius: 12px;
        padding: 6px;
        gap: 4px;
        box-shadow: 0 1px 2px rgba(18,37,59,0.04), 0 8px 24px rgba(18,37,59,0.06);
    }
    .stTabs [data-baseweb="tab"]{
        border-radius: 8px !important;
        font-weight: 600;
        color: var(--muted);
        padding: 8px 16px !important;
    }
    .stTabs [aria-selected="true"]{
        background: var(--ink) !important;
        color: #fff !important;
    }
    .stTabs [data-baseweb="tab-highlight"]{ background: transparent !important; }
    .stTabs [data-baseweb="tab-border"]{ display:none; }

    /* Expander (itinerary days) */
    div[data-testid="stExpander"]{
        border: 1px solid var(--line) !important;
        border-radius: 12px !important;
        background: var(--card) !important;
        overflow: hidden;
    }
    div[data-testid="stExpander"] summary{
        font-weight: 600; color: var(--ink);
        font-family: 'Inter', sans-serif;
    }

    /* Dataframe */
    div[data-testid="stDataFrame"]{
        border: 1px solid var(--line) !important;
        border-radius: 10px !important;
        overflow: hidden;
    }

    /* Card container helper (via st.container(border=True)) */
    div[data-testid="stVerticalBlockBorderWrapper"]{
        background: var(--card);
        border-radius: 14px !important;
        border: 1px solid var(--line) !important;
        box-shadow: 0 1px 2px rgba(18,37,59,0.04), 0 8px 24px rgba(18,37,59,0.06);
    }

    /* Buttons in main area (e.g. demo button) */
    .stButton button{
        border-radius: 8px;
        border: 1px solid var(--line);
        background: var(--card);
        color: var(--ink);
        font-weight: 600;
    }

    /* Boarding-pass hero */
    .ticket{
        position: relative;
        background: var(--card);
        border-radius: 16px;
        box-shadow: 0 1px 2px rgba(18,37,59,0.04), 0 8px 24px rgba(18,37,59,0.08);
        padding: 26px 34px;
        margin-bottom: 10px;
    }
    .ticket-row{ display:flex; align-items:center; justify-content:space-between; gap:20px; flex-wrap: wrap; }
    .ticket-city .code{ font-family:'Fraunces', serif; font-size:34px; font-weight:600; color:var(--ink); line-height:1; }
    .ticket-city .name{ font-size:12.5px; color:var(--muted); margin-top:4px; }
    .ticket-city.dest{ text-align:right; }
    .ticket-mid{ display:flex; flex-direction:column; align-items:center; gap:6px; padding:0 20px; }
    .ticket-mid .plane{ font-size:20px; color:var(--gold); }
    .ticket-mid .line{ width:140px; height:1px; background:var(--line); }
    .ticket-mid .status{
        font-family:'IBM Plex Mono', monospace; font-size:10px; letter-spacing:0.1em; text-transform:uppercase;
        color: var(--jade); background: var(--jade-soft); padding:3px 10px; border-radius:100px; margin-top:2px;
    }
    .ticket-stub{
        margin-top:18px; padding-top:16px; border-top: 1px dashed var(--line);
        display:grid; grid-template-columns:repeat(5,1fr); gap:10px;
    }
    .stub-eyebrow{ font-family:'IBM Plex Mono', monospace; text-transform:uppercase; letter-spacing:0.1em; font-size:10.5px; color:var(--muted); margin-bottom:4px; }
    .stub-val{ font-family:'Fraunces', serif; font-size:16px; font-weight:600; color:var(--ink); }
    .stub-val.over{ color: var(--rust); }
    .stub-val.under{ color: var(--jade); }

    /* Hotel gradient visual */
    .hotel-visual{
        height:140px; border-radius:10px;
        background: linear-gradient(135deg, var(--ink) 0%, var(--jade) 130%);
        display:flex; align-items:flex-end; justify-content:flex-end; padding:14px;
        margin-bottom:14px;
        position: relative; overflow:hidden;
    }
    .hotel-visual::before{
        content:"";
        position:absolute; inset:0;
        background-image:
            radial-gradient(circle at 85% 20%, rgba(255,255,255,0.14) 0, transparent 45%),
            repeating-linear-gradient(90deg, rgba(255,255,255,0.06) 0 2px, transparent 2px 34px);
    }
    .hotel-visual .stars{
        position:relative; color: var(--gold-soft); font-size:13px; font-weight:600;
        background: rgba(0,0,0,0.28); padding:5px 10px; border-radius:100px;
    }

    /* Place cards */
    .place-card{ background: var(--paper); border-radius:12px; padding:16px; border:1px solid var(--line); height:100%; }
    .place-card .place-ico{
        width:34px; height:34px; border-radius:8px; margin-bottom:8px;
        background: var(--gold-soft); color: var(--ink);
        display:flex; align-items:center; justify-content:center; font-size:15px;
    }
    .place-card .place-name{ font-weight:600; font-size:14px; color:var(--ink); margin-bottom:4px; }
    .place-card .place-reason{ font-size:12.5px; color:var(--muted); line-height:1.45; }

    /* Budget bars */
    .bar-row{ display:grid; grid-template-columns:120px 1fr 90px; align-items:center; gap:12px; font-size:12.5px; margin-bottom:10px; }
    .bar-track{ height:9px; border-radius:100px; background:var(--paper); overflow:hidden; }
    .bar-fill{ height:100%; border-radius:100px; background: linear-gradient(90deg, var(--jade), var(--gold)); }
    .util-track{ height:10px; border-radius:100px; background:var(--paper); overflow:hidden; margin:10px 0 6px; }
    .util-fill{ height:100%; border-radius:100px; background: linear-gradient(90deg, var(--jade), var(--jade-soft)); }
    .util-fill.over{ background: linear-gradient(90deg, var(--rust), #E08965); }
    .mono-val{ font-family:'IBM Plex Mono', monospace; text-align:right; }

    /* Banners */
    .banner{ border-radius:10px; padding:14px 16px; font-size:13.5px; margin-top:12px; }
    .banner.warn{ background: var(--rust-soft); color:#8A3A20; }
    .banner.ok{ background: var(--jade-soft); color:#155A41; }

    /* Empty state */
    .empty-wrap{ margin-top: 8vh; max-width: 480px; }
    .empty-stamp{
        width:56px; height:56px; border-radius:50%; border:2px solid var(--jade);
        display:flex; align-items:center; justify-content:center; font-size:24px; color:var(--jade);
        transform: rotate(-8deg); margin-bottom:14px;
    }

    /* Agent status list in sidebar */
    .agent-row{ display:flex; align-items:center; justify-content:space-between; padding:5px 0; font-size:12.5px; color:#C9D2DF; }
    .agent-dot{ width:7px; height:7px; border-radius:50%; background: var(--jade); display:inline-block; margin-right:8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------
# Session state
# --------------------------------------------------------------

if "result" not in st.session_state:
    st.session_state.result = None

if "error" not in st.session_state:
    st.session_state.error = None


# --------------------------------------------------------------
# Sample data (for "preview a sample trip", no backend required)
# --------------------------------------------------------------

SAMPLE_RESULT = {
    "transport": {
        "recommended_mode": {"mode": "Train", "estimated_price": 400, "duration": "6h", "distance_km": 317.82},
        "options": [
            {"mode": "Flight", "estimated_price": 2500, "duration": "1h", "pros": ["Fastest", "Saves time"], "cons": ["Expensive", "Airport transfers"]},
            {"mode": "Train", "estimated_price": 400, "duration": "6h", "pros": ["Cheapest", "Comfortable"], "cons": ["Longer journey"]},
            {"mode": "Bus", "estimated_price": 700, "duration": "7h", "pros": ["Affordable"], "cons": ["Less comfortable"]},
            {"mode": "Car", "estimated_price": 2225, "duration": "5.3h", "pros": ["Flexible", "Door-to-door"], "cons": ["Fuel + toll cost"]},
        ],
    },
    "hotel": {
        "name": "Vinca Inn Sangli",
        "price_per_night": 1200,
        "rating": 3.7,
        "address": "Vinca Inn Sangli, New Pride Multiplex Road, Sangli - 416416, Maharashtra, India",
    },
    "weather": {"city": "Pune", "temperature": 25, "feels_like": 26.48, "condition": "Clouds"},
    "places": [
        {"name": "Sangli Museum", "reason": "Matches the user's interest in History"},
        {"name": "Darbar Hall", "reason": "Matches the user's interest in History"},
        {"name": "Shahu Maharaj Statue", "reason": "Matches the user's interest in History and Temple"},
        {"name": "Patwardhan's Palace", "reason": "Matches the user's interest in History"},
        {"name": "Gandhi Putala", "reason": "Matches the user's interest in History"},
    ],
    "budget_summary": {
        "total_cost": 6400,
        "remaining_budget": 18600,
        "transport_cost": 400,
        "hotel_cost": 6000,
        "food_cost": 0,
        "local_transport_cost": 0,
        "activities_cost": 0,
        "extras_source": None,
    },
    "itinerary": [
        {"day": 1, "estimated_cost": 4000, "morning": "Arrive in Pune, check in, freshen up", "afternoon": "Visit Sangli Museum", "evening": "Relaxed stroll near the hotel", "breakfast": "Hotel breakfast", "lunch": "Local Maharashtrian thali", "dinner": "Vegetarian dinner near hotel", "stay": "Vinca Inn Sangli"},
        {"day": 2, "estimated_cost": 3500, "morning": "Darbar Hall guided tour", "afternoon": "Shahu Maharaj Statue + local market", "evening": "Sunset at the riverside", "breakfast": "Poha & chai", "lunch": "Thali at local eatery", "dinner": "Street food tasting", "stay": "Vinca Inn Sangli"},
        {"day": 3, "estimated_cost": 3000, "morning": "Patwardhan's Palace visit", "afternoon": "Leisure time / shopping", "evening": "Cultural show", "breakfast": "Hotel breakfast", "lunch": "Cafe lunch", "dinner": "Vegetarian thali", "stay": "Vinca Inn Sangli"},
        {"day": 4, "estimated_cost": 3200, "morning": "Gandhi Putala + nearby temple", "afternoon": "Local sightseeing", "evening": "Free time", "breakfast": "Hotel breakfast", "lunch": "Regional specialties", "dinner": "Rooftop dinner", "stay": "Vinca Inn Sangli"},
        {"day": 5, "estimated_cost": 4000, "morning": "Last minute shopping", "afternoon": "Check out, travel back", "evening": "Arrive home", "breakfast": "Hotel breakfast", "lunch": "On the way", "dinner": "-", "stay": "-"},
    ],
}


# --------------------------------------------------------------
# Helpers
# --------------------------------------------------------------

def inr(n):
    try:
        return f"₹{int(round(float(n or 0))):,}"
    except (TypeError, ValueError):
        return "₹0"


def render_ticket(result, payload):
    budget_summary = result.get("budget_summary") or {}
    total_cost = budget_summary.get("total_cost", 0)
    remaining = budget_summary.get("remaining_budget", payload["budget"] - total_cost)
    over = remaining < 0
    src_code = (payload["source"] or "???")[:3].upper()
    dst_code = (payload["destination"] or "???")[:3].upper()

    st.markdown(
        f"""
        <div class="ticket">
            <div class="ticket-row">
                <div class="ticket-city">
                    <div class="code">{src_code}</div>
                    <div class="name">{payload['source']}</div>
                </div>
                <div class="ticket-mid">
                    <span class="plane">✈</span>
                    <div class="line"></div>
                    <span class="status">Confirmed</span>
                </div>
                <div class="ticket-city dest">
                    <div class="code">{dst_code}</div>
                    <div class="name">{payload['destination']}</div>
                </div>
            </div>
            <div class="ticket-stub">
                <div><div class="stub-eyebrow">Travel style</div><div class="stub-val">{payload['travel_style']}</div></div>
                <div><div class="stub-eyebrow">Duration</div><div class="stub-val">{payload['days']} days</div></div>
                <div><div class="stub-eyebrow">Travellers</div><div class="stub-val">{payload['travellers']}</div></div>
                <div><div class="stub-eyebrow">Est. cost</div><div class="stub-val">{inr(total_cost)}</div></div>
                <div><div class="stub-eyebrow">{'Over by' if over else 'Remaining'}</div><div class="stub-val {'over' if over else 'under'}">{inr(abs(remaining))}</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_agent_status():
    agents = [
        "Planner Agent", "Transport Agent", "Hotel Agent",
        "Weather Agent", "Places Agent", "Budget Agent", "Itinerary Agent",
    ]
    rows = "".join(
        f'<div class="agent-row"><span><span class="agent-dot"></span>{a}</span>'
        f'<span style="font-family:\'IBM Plex Mono\',monospace;color:#7FD9B7;">done</span></div>'
        for a in agents
    )
    st.sidebar.markdown(
        f'<div style="margin-top:20px;padding-top:16px;border-top:1px dashed rgba(255,255,255,0.15);">'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10.5px;text-transform:uppercase;'
        f'letter-spacing:0.1em;color:#8CA0BD;margin-bottom:8px;">AI Agents</div>{rows}</div>',
        unsafe_allow_html=True,
    )


def render_place_cards(places, columns=4):
    if not places:
        st.caption("No places returned.")
        return
    cols = st.columns(min(len(places), columns) or 1)
    for i, place in enumerate(places):
        with cols[i % len(cols)]:
            st.markdown(
                f"""
                <div class="place-card">
                    <div class="place-ico">📍</div>
                    <div class="place-name">{place.get('name', 'Unknown')}</div>
                    <div class="place-reason">{place.get('reason', '')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_budget_bars(budget_summary):
    rows = [
        ("Transport", budget_summary.get("transport_cost", 0)),
        ("Hotel", budget_summary.get("hotel_cost", 0)),
        ("Food", budget_summary.get("food_cost", 0)),
        ("Local transport", budget_summary.get("local_transport_cost", 0)),
        ("Activities", budget_summary.get("activities_cost", 0)),
    ]
    max_val = max([v or 0 for _, v in rows] + [1])
    html_rows = ""
    for label, val in rows:
        pct = max(4, (val or 0) / max_val * 100)
        html_rows += (
            f'<div class="bar-row"><span>{label}</span>'
            f'<div class="bar-track"><div class="bar-fill" style="width:{pct}%;"></div></div>'
            f'<span class="mono-val">{inr(val)}</span></div>'
        )
    st.markdown(html_rows, unsafe_allow_html=True)


def render_hotel_visual(rating):
    st.markdown(
        f"""
        <div class="hotel-visual"><span class="stars">{rating or '-'} ★</span></div>
        """,
        unsafe_allow_html=True,
    )


def build_payload(source, destination, start_date, days, travellers, budget,
                   travel_style, preferred_transport, hotel_type, food_preference,
                   interests, user_request):
    return {
        "source": source,
        "destination": destination,
        "start_date": start_date.isoformat(),
        "days": int(days),
        "budget": int(budget),
        "travellers": int(travellers),
        "travel_style": travel_style,
        "preferred_transport": preferred_transport,
        "hotel_type": hotel_type,
        "food_preference": food_preference,
        "interests": interests,
        "user_request": user_request,
    }


# --------------------------------------------------------------
# Sidebar - Trip Input Form
# --------------------------------------------------------------

st.sidebar.markdown(
    """
    <div class="brand-block">
        <div class="brand-mark">✈️</div>
        <div>
            <p class="brand-title">Wayfarer</p>
            <p class="brand-sub">AI Multi-Agent Trip Planner</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar.form("trip_form"):

    source = st.text_input("Source city", value="Mumbai")
    destination = st.text_input("Destination city", value="Goa")

    start_date = st.date_input(
        "Start date",
        value=date.today() + timedelta(days=14),
        min_value=date.today(),
    )

    col1, col2 = st.columns(2)
    with col1:
        days = st.number_input("Days", min_value=1, max_value=60, value=5, step=1)
    with col2:
        travellers = st.number_input("Travellers", min_value=1, max_value=20, value=2, step=1)

    budget = st.number_input(
        "Budget (₹)",
        min_value=1000,
        max_value=2_000_000,
        value=25000,
        step=1000,
    )

    travel_style = st.selectbox(
        "Travel style",
        ["Budget", "Luxury", "Family", "Adventure", "Business"],
    )

    preferred_transport = st.selectbox(
        "Preferred transport",
        ["Any", "Flight", "Train", "Bus", "Car"],
    )

    hotel_type = st.selectbox(
        "Hotel type",
        ["Budget", "3 Star", "4 Star", "5 Star", "Any"],
    )

    food_preference = st.selectbox(
        "Food preference",
        ["Any", "Vegetarian", "Non-Vegetarian", "Vegan"],
    )

    interests = st.multiselect(
        "Interests",
        ["Beach", "History", "Adventure", "Shopping", "Nightlife", "Nature", "Food"],
        default=["History"],
    )

    user_request = st.text_area(
        "Tell us more about your trip",
        value=(
            f"Plan a {travel_style.lower()} trip from {source} to {destination} "
            f"for {travellers} traveller(s)."
        ),
        height=100,
    )

    submitted = st.form_submit_button("Plan My Trip →", use_container_width=True)

st.sidebar.button(
    "or preview a sample trip",
    key="demo_btn",
    use_container_width=True,
)

with st.sidebar.expander("API settings"):
    st.caption(f"Backend: {API_BASE_URL}")
    st.caption("Set TRAVEL_PLANNER_API_URL to change it.")

if submitted:
    payload = build_payload(
        source, destination, start_date, days, travellers, budget,
        travel_style, preferred_transport, hotel_type, food_preference,
        interests, user_request,
    )

    st.session_state.result = None
    st.session_state.error = None
    st.session_state.payload = payload

    with st.spinner("Talking to the planner agents... this can take a minute."):
        try:
            response = requests.post(PLAN_TRIP_ENDPOINT, json=payload, timeout=180)
            response.raise_for_status()
            st.session_state.result = response.json()
        except requests.exceptions.ConnectionError:
            st.session_state.error = (
                f"Couldn't reach the API at {PLAN_TRIP_ENDPOINT}. "
                "Is the FastAPI backend running? "
                "(uvicorn app.main:app --reload)"
            )
        except requests.exceptions.Timeout:
            st.session_state.error = "The request timed out. The planner may be taking longer than usual - try again."
        except requests.exceptions.HTTPError:
            try:
                detail = response.json()
            except Exception:
                detail = response.text
            st.session_state.error = f"API returned an error ({response.status_code}): {detail}"
        except Exception as e:
            st.session_state.error = f"Unexpected error: {e}"

if st.session_state.get("demo_btn"):
    st.session_state.result = SAMPLE_RESULT
    st.session_state.error = None
    st.session_state.payload = build_payload(
        source, destination, start_date, days, travellers, budget,
        travel_style, preferred_transport, hotel_type, food_preference,
        interests, user_request,
    )

if st.session_state.result:
    render_agent_status()


# --------------------------------------------------------------
# Main area
# --------------------------------------------------------------

if st.session_state.error:
    st.error(st.session_state.error)

result = st.session_state.result
payload = st.session_state.get("payload")

if not result:
    st.markdown(
        """
        <div class="empty-wrap">
            <div class="empty-stamp">✈</div>
            <h2>Your itinerary starts here.</h2>
            <p style="color:var(--muted); font-size:14.5px; line-height:1.6;">
                Fill in the trip details on the left and hit <b>Plan My Trip</b> — six AI agents
                will handle transport, stays, weather, sights, budget and the day-by-day plan.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# Guard against a completely empty response (e.g. a partial plan
# that never reached the itinerary/budget agents).
if not any(result.get(k) for k in ["transport", "hotel", "weather", "places", "budget_summary", "itinerary"]):
    st.warning(
        "The planner didn't return any trip details. "
        "This can happen if your request only asked about one part of the trip "
        "(e.g. just the weather)."
    )
    st.json(result)
    st.stop()

render_ticket(result, payload)

tab_overview, tab_transport, tab_hotel, tab_weather, tab_places, tab_budget, tab_itinerary, tab_raw = st.tabs(
    ["◈ Overview", "🚆 Transport", "🏨 Hotel", "☀️ Weather", "📍 Places", "💰 Budget", "🗓️ Itinerary", "⌁ Raw JSON"]
)

transport = result.get("transport") or {}
hotel = result.get("hotel") or {}
weather = result.get("weather") or {}
places = result.get("places") or []
budget_summary = result.get("budget_summary") or {}
itinerary = result.get("itinerary") or []

# ------------------------------
# Overview
# ------------------------------
with tab_overview:
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown("#### 🚆 Transport")
            rec = transport.get("recommended_mode")
            if rec:
                st.metric("Mode", rec.get("mode", "-"))
                st.metric("Price", inr(rec.get("estimated_price")))
                st.metric("Duration", rec.get("duration", "-"))
            else:
                st.caption("No recommendation yet.")
    with c2:
        with st.container(border=True):
            st.markdown("#### 🏨 Hotel")
            if hotel:
                st.metric("Name", hotel.get("name", "-"))
                st.metric("Price / night", inr(hotel.get("price_per_night")))
                st.metric("Rating", f"{hotel.get('rating', '-')} ★")
            else:
                st.caption("No hotel selected yet.")
    with c3:
        with st.container(border=True):
            st.markdown("#### ☀️ Weather")
            if weather:
                st.metric(f"{weather.get('city', '-')}", f"{weather.get('temperature', '-')}°C")
                st.caption(f"Feels like {weather.get('feels_like', '-')}°C · {weather.get('condition', '-')}")
            else:
                st.caption("No forecast yet.")

    st.markdown("#### 📍 Top places")
    render_place_cards(places[:4], columns=4)

    if budget_summary:
        st.markdown("#### 💰 Budget snapshot")
        remaining = budget_summary.get("remaining_budget", 0)
        over = remaining < 0
        c1, c2 = st.columns(2)
        c1.metric("Total estimated cost", inr(budget_summary.get("total_cost")))
        c2.metric("Over budget" if over else "Remaining budget", inr(abs(remaining)))

    st.markdown(
        f"""
        <div class="banner ok">💡 Travel tip: shoulder-season travel usually cuts hotel
        rates 15–20% for {weather.get('city', 'this destination')}.</div>
        """,
        unsafe_allow_html=True,
    )

# ------------------------------
# Transport
# ------------------------------
with tab_transport:
    recommended = transport.get("recommended_mode")
    if recommended:
        with st.container(border=True):
            st.markdown("#### 🚆 Recommended transport")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Mode", recommended.get("mode", "-"))
            c2.metric("Price", inr(recommended.get("estimated_price")))
            c3.metric("Duration", recommended.get("duration", "-"))
            c4.metric("Distance", f"{recommended.get('distance_km', 0):,.0f} km")

            options = transport.get("options", [])
            if options:
                st.markdown("###### Compare all transport options")
                st.dataframe(
                    [
                        {
                            "Mode": o.get("mode"),
                            "Price (₹)": o.get("estimated_price"),
                            "Duration": o.get("duration"),
                            "Pros": ", ".join(o.get("pros", [])),
                            "Cons": ", ".join(o.get("cons", [])),
                        }
                        for o in options
                    ],
                    use_container_width=True,
                    hide_index=True,
                )
    else:
        st.caption("No transport data returned.")

# ------------------------------
# Hotel
# ------------------------------
with tab_hotel:
    if hotel:
        with st.container(border=True):
            render_hotel_visual(hotel.get("rating"))
            st.markdown(f"#### {hotel.get('name', '-')}")
            c1, c2 = st.columns(2)
            c1.metric("Price / night", inr(hotel.get("price_per_night")))
            c2.metric("Rating", f"{hotel.get('rating', '-')} ★")
            if hotel.get("address"):
                st.caption(hotel["address"])
    else:
        st.caption("No hotel data returned.")

# ------------------------------
# Weather
# ------------------------------
with tab_weather:
    if weather:
        with st.container(border=True):
            st.markdown(f"#### ☀️ Weather in {weather.get('city', '-')}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Temperature", f"{weather.get('temperature', '-')}°C")
            c2.metric("Feels like", f"{weather.get('feels_like', '-')}°C")
            c3.metric("Condition", weather.get("condition", "-"))
    else:
        st.caption("No weather data returned.")

# ------------------------------
# Places
# ------------------------------
with tab_places:
    if places:
        st.markdown("#### 📍 Recommended places")
        render_place_cards(places, columns=5)
    else:
        st.caption("No places returned.")

# ------------------------------
# Budget Summary
# ------------------------------
with tab_budget:
    if budget_summary:
        with st.container(border=True):
            remaining = budget_summary.get("remaining_budget", 0)
            over = remaining < 0
            total_cost = budget_summary.get("total_cost", 0)

            c1, c2 = st.columns(2)
            c1.metric("Total Estimated Cost", inr(total_cost))
            c2.metric(
                "Remaining Budget",
                inr(remaining),
                delta=None if remaining >= 0 else "Over budget!",
                delta_color="inverse",
            )

            utilization = 0
            denom = total_cost + max(remaining, 0)
            if denom:
                utilization = min(100, (total_cost / denom) * 100)

            st.markdown(
                f"""
                <div class="util-track">
                    <div class="util-fill {'over' if over else ''}" style="width:{max(4, utilization)}%;"></div>
                </div>
                <div style="font-size:12.5px;color:var(--muted);">Budget utilization: {utilization:.1f}%</div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("###### Cost breakdown")
            render_budget_bars(budget_summary)

            if budget_summary.get("extras_source"):
                st.caption(f"Extras total sourced from: **{budget_summary['extras_source']}**")

            if over:
                st.markdown(
                    f"""<div class="banner warn">⚠ This plan is {inr(abs(remaining))} over your budget.
                    Consider a cheaper hotel, transport mode, or fewer days.</div>""",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """<div class="banner ok">✓ You're within budget — nice work.</div>""",
                    unsafe_allow_html=True,
                )
    else:
        st.caption("No budget summary returned.")

# ------------------------------
# Itinerary
# ------------------------------
with tab_itinerary:
    if itinerary:
        st.markdown("#### 🗓️ Day-by-day itinerary")
        for day in itinerary:
            day_num = day.get("day", "?")
            cost = day.get("estimated_cost", 0)

            with st.expander(f"Day {day_num} — Estimated cost: {inr(cost)}", expanded=(day_num == 1)):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**🌅 Morning:** {day.get('morning', '-')}")
                    st.markdown(f"**☀️ Afternoon:** {day.get('afternoon', '-')}")
                    st.markdown(f"**🌙 Evening:** {day.get('evening') or '-'}")
                with c2:
                    st.markdown(f"**🍳 Breakfast:** {day.get('breakfast', '-')}")
                    st.markdown(f"**🍽️ Lunch:** {day.get('lunch', '-')}")
                    st.markdown(f"**🍛 Dinner:** {day.get('dinner') or '-'}")
                st.markdown(f"**🏨 Stay:** {day.get('stay') or '-'}")
    else:
        st.caption("No itinerary returned.")

# ------------------------------
# Raw JSON (debug)
# ------------------------------
with tab_raw:
    st.json(result)