"""
Navigate Page — Route Request & Safety Map
============================================
Users search for locations by name (geocoded via Nominatim), click
the map to set origin/destination, configure demographic context,
and submit a route request to the FastAPI backend. Results are
rendered as red (fastest) and green (safest) polylines with a
metrics panel showing the structural justification for detours.

Run the full platform:
    Terminal 1:  uvicorn app.main:app --reload
    Terminal 2:  streamlit run ui/Home.py
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import folium
import requests
import streamlit as st
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from streamlit_folium import st_folium

# ── Page config ─────────────────────────────────────────
st.set_page_config(page_title="Navigate - N.A.R.I", page_icon="🗺️", layout="wide")

API_BASE = "http://127.0.0.1:8000"
IST = ZoneInfo("Asia/Kolkata")
PATNA_CENTER = (25.6093, 85.1500)

# ── Geocoder ────────────────────────────────────────────
@st.cache_resource
def _get_geocoder():
    return Nominatim(user_agent="NARI_Patna_App", timeout=5)


def geocode_location(query: str) -> tuple[float, float, str] | None:
    """
    Geocode a text query within the Patna region.
    Returns (lat, lng, display_name) or None on failure.
    """
    if not query or not query.strip():
        return None
    geocoder = _get_geocoder()
    search = f"{query.strip()}, Patna, Bihar, India"
    try:
        result = geocoder.geocode(search, exactly_one=True)
        #result = geocoder.geocode(f"{search}, Patna, Bihar, India", exactly_one=True)
    except (GeocoderTimedOut, GeocoderServiceError):
        return None
    if result is None:
        return None
    return (result.latitude, result.longitude, result.raw.get("display_name", query))


# ── Session state initialisation ────────────────────────
def _init_state():
    now_ist = datetime.now(IST)
    defaults = {
        "origin_lat": None,
        "origin_lng": None,
        "origin_label": "",
        "dest_lat": None,
        "dest_lng": None,
        "dest_label": "",
        "click_target": "origin",
        "auto_hour": now_ist.hour,
        "route_result": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

_init_state()


# ── Gender from user profile (mock) ────────────────────
profile_gender = st.session_state.get("user_gender")
gender_from_profile = profile_gender is not None
if not gender_from_profile:
    profile_gender = "female"


# ── Sidebar ─────────────────────────────────────────────
with st.sidebar:
    st.title("🧭 N.A.R.I")
    st.caption("Navigation Aiding Reinforced Informatics")
    st.divider()

    # Location search
    st.subheader("Origin")
    origin_query = st.text_input(
        "Search origin location",
        placeholder="e.g. Patna Junction, Gandhi Maidan",
        key="origin_search",
    )
    if st.button("Geocode origin", key="btn_geo_origin"):
        result = geocode_location(origin_query)
        if result:
            st.session_state.origin_lat = result[0]
            st.session_state.origin_lng = result[1]
            st.session_state.origin_label = result[2]
            st.rerun()
        else:
            st.warning("Location not found. Try a more specific query.")

    if st.session_state.origin_lat is not None:
        st.caption(
            f"📍 {st.session_state.origin_lat:.4f}, {st.session_state.origin_lng:.4f}"
        )
        if st.session_state.origin_label:
            st.caption(st.session_state.origin_label[:80])

    st.divider()

    st.subheader("Destination")
    dest_query = st.text_input(
        "Search destination location",
        placeholder="e.g. Kankarbagh, Bailey Road",
        key="dest_search",
    )
    if st.button("Geocode destination", key="btn_geo_dest"):
        result = geocode_location(dest_query)
        if result:
            st.session_state.dest_lat = result[0]
            st.session_state.dest_lng = result[1]
            st.session_state.dest_label = result[2]
            st.rerun()
        else:
            st.warning("Location not found. Try a more specific query.")

    if st.session_state.dest_lat is not None:
        st.caption(
            f"📍 {st.session_state.dest_lat:.4f}, {st.session_state.dest_lng:.4f}"
        )
        if st.session_state.dest_label:
            st.caption(st.session_state.dest_label[:80])

    st.divider()

    # Map click target selector
    st.subheader("Map Click Mode")
    st.session_state.click_target = st.radio(
        "Next map click sets:",
        ["origin", "destination"],
        index=0 if st.session_state.click_target == "origin" else 1,
        horizontal=True,
        key="click_mode_radio",
    )
    st.caption("Click any point on the map to set coordinates.")

    st.divider()

    # Demographics
    st.subheader("Demographics")
    gender = st.selectbox(
        "Gender",
        ["Female", "Male"],
        index=0 if profile_gender.lower() == "female" else 1,
    )
    if gender_from_profile:
        st.caption("Gender loaded from user profile.")
    else:
        st.caption("Gender inferred from User Profile (default: Female).")

    # Time
    now_ist = datetime.now(IST)
    auto_hour = now_ist.hour
    hour = st.slider(
        "Hour of day (IST)",
        min_value=0,
        max_value=23,
        value=auto_hour,
        help="Auto-detected from IST. Override for future trip planning.",
    )
    time_label = "Night (20:00-07:59)" if hour >= 20 or hour < 8 else "Day (08:00-19:59)"
    st.caption(f"Time period: **{time_label}** | IST auto-detected: {auto_hour}:00")

    st.divider()

    # Submit
    origin_ready = st.session_state.origin_lat is not None
    dest_ready = st.session_state.dest_lat is not None
    both_ready = origin_ready and dest_ready

    if not both_ready:
        missing = []
        if not origin_ready:
            missing.append("origin")
        if not dest_ready:
            missing.append("destination")
        st.info(f"Set {' and '.join(missing)} to enable routing.")

    submitted = st.button(
        "Find Safe Route",
        type="primary",
        use_container_width=True,
        disabled=not both_ready,
    )


# ── Helper functions ────────────────────────────────────
def build_map(center_lat, center_lng, zoom=13):
    """Create a base Folium map."""
    return folium.Map(
        location=[center_lat, center_lng],
        zoom_start=zoom,
        tiles="CartoDB positron",
    )


def draw_path(fmap, coords, color, label, weight=5, opacity=0.85):
    """Draw a polyline from a list of {lat, lng} dicts."""
    points = [(c["lat"], c["lng"]) for c in coords]
    folium.PolyLine(
        locations=points,
        color=color,
        weight=weight,
        opacity=opacity,
        tooltip=label,
    ).add_to(fmap)


def add_marker(fmap, lat, lng, label, color, icon_name):
    """Place a marker on the map."""
    folium.Marker(
        location=[lat, lng],
        popup=label,
        icon=folium.Icon(color=color, icon=icon_name, prefix="fa"),
    ).add_to(fmap)


def add_legend(fmap, gender_label, hour_val, m_demo):
    """Inject an HTML legend into the map."""
    html = f"""
    <div style="position:fixed; bottom:30px; left:30px; z-index:1000;
                background:white; padding:14px 18px; border-radius:10px;
                box-shadow:0 2px 12px rgba(0,0,0,0.15); font-size:13px;
                font-family: 'Segoe UI', sans-serif; line-height:1.6;">
        <b style="font-size:14px;">N.A.R.I Route Comparison</b><br>
        <span style="color:#D32F2F;">&#9644;&#9644;</span> Fastest Path<br>
        <span style="color:#388E3C;">&#9644;&#9644;</span> Safest Path (1.25x constrained)<br>
        <span style="font-size:11px; color:#666;">
            {gender_label} | {hour_val}:00 IST | M_demo = {m_demo}
        </span>
    </div>
    """
    fmap.get_root().html.add_child(folium.Element(html))


# ── Main content area ──────────────────────────────────
st.header("🗺️ Navigate — Find Your Safest Route")

# ── API call on submit ─────────────────────────────────
if submitted:
    o_lat = st.session_state.origin_lat
    o_lng = st.session_state.origin_lng
    d_lat = st.session_state.dest_lat
    d_lng = st.session_state.dest_lng

    if o_lat == d_lat and o_lng == d_lng:
        st.error("Origin and destination cannot be the same location.")
        st.stop()

    payload = {
        "origin": {"lat": o_lat, "lng": o_lng},
        "destination": {"lat": d_lat, "lng": d_lng},
        "gender": gender.lower(),
        "time_of_day": f"{hour:02d}:00",
        "k_paths": 10,
    }

    with st.spinner("Computing safest route..."):
        try:
            resp = requests.post(f"{API_BASE}/api/v1/route", json=payload, timeout=30)
        except requests.ConnectionError:
            st.error(
                "Cannot connect to the N.A.R.I API. "
                "Ensure the FastAPI server is running: `uvicorn app.main:app --reload`"
            )
            st.stop()

    if resp.status_code != 200:
        detail = resp.json().get("detail", resp.text) if resp.headers.get("content-type", "").startswith("application/json") else resp.text
        st.error(f"API error ({resp.status_code}): {detail}")
        st.stop()

    data = resp.json()
    if data["status"] != "ok":
        st.warning(f"Routing status: {data['status']} — {data.get('message', '')}")
        st.stop()

    st.session_state.route_result = data


# ── Render results or default map ──────────────────────
data = st.session_state.route_result

if data is not None:
    safest = data["safest_path"]
    fastest = data["fastest_path"]
    detour = data.get("detour_factor", 1.0)
    m_demo = data.get("m_demo", 1.0)
    demographic = data.get("demographic", "")
    candidates_total = data.get("candidates_evaluated", 0)
    candidates_ok = data.get("candidates_within_budget", 0)

    safest_dist = safest["total_distance_m"]
    fastest_dist = fastest["total_distance_m"]
    safest_score = safest["avg_safety_score"]
    fastest_score = fastest["avg_safety_score"]

    delta_safety = safest_score - fastest_score
    delta_dist = safest_dist - fastest_dist

    # Metrics panel
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(
        label="Safety Gain (ΔS_total)",
        value=f"+{delta_safety:.4f}" if delta_safety >= 0 else f"{delta_safety:.4f}",
    )
    m2.metric(
        label="Distance Delta",
        value=f"+{delta_dist:,.0f} m" if delta_dist >= 0 else f"{delta_dist:,.0f} m",
    )
    m3.metric(label="Detour Factor", value=f"{detour:.3f}x")
    m4.metric(label="M_demo", value=f"{m_demo:.2f}")

    # Comparison table
    st.divider()
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("#### Fastest Path")
        st.markdown(f"""
| Metric | Value |
|--------|-------|
| Distance | **{fastest_dist:,.0f} m** |
| S_total | **{fastest_score:.4f}** |
| Nodes | {fastest['node_count']} |
""")
    with col_right:
        st.markdown("#### Safest Path (recommended)")
        st.markdown(f"""
| Metric | Value |
|--------|-------|
| Distance | **{safest_dist:,.0f} m** |
| S_total | **{safest_score:.4f}** |
| Nodes | {safest['node_count']} |
| Detour | {detour:.3f}x |
""")

    st.caption(
        f"Evaluated {candidates_total} candidate paths, "
        f"{candidates_ok} within the 1.25x distance budget. "
        f"Demographic context: {demographic}."
    )

    # Route map
    st.divider()
    o_lat = st.session_state.origin_lat or PATNA_CENTER[0]
    o_lng = st.session_state.origin_lng or PATNA_CENTER[1]
    d_lat = st.session_state.dest_lat or PATNA_CENTER[0]
    d_lng = st.session_state.dest_lng or PATNA_CENTER[1]

    center_lat = (o_lat + d_lat) / 2
    center_lng = (o_lng + d_lng) / 2
    route_map = build_map(center_lat, center_lng, zoom=14)

    if fastest.get("coordinates"):
        draw_path(
            route_map, fastest["coordinates"], "#D32F2F",
            f"Fastest: {fastest_dist:,.0f} m | S={fastest_score:.4f}",
            weight=5, opacity=0.7,
        )
    if safest.get("coordinates"):
        draw_path(
            route_map, safest["coordinates"], "#388E3C",
            f"Safest: {safest_dist:,.0f} m | S={safest_score:.4f} | {detour:.2f}x",
            weight=6, opacity=0.9,
        )

    o_label = st.session_state.origin_label or "Origin"
    d_label = st.session_state.dest_label or "Destination"
    add_marker(route_map, o_lat, o_lng, f"Origin: {o_label}", "blue", "play")
    add_marker(route_map, d_lat, d_lng, f"Destination: {d_label}", "darkred", "flag-checkered")
    add_legend(route_map, gender, hour, m_demo)

    map_output = st_folium(route_map, use_container_width=True, height=560)

    # Handle map clicks even on the results view
    if map_output and map_output.get("last_clicked"):
        clicked = map_output["last_clicked"]
        c_lat, c_lng = clicked["lat"], clicked["lng"]
        if st.session_state.click_target == "origin":
            st.session_state.origin_lat = c_lat
            st.session_state.origin_lng = c_lng
            st.session_state.origin_label = f"Map pin ({c_lat:.4f}, {c_lng:.4f})"
            st.session_state.route_result = None
            st.rerun()
        else:
            st.session_state.dest_lat = c_lat
            st.session_state.dest_lng = c_lng
            st.session_state.dest_label = f"Map pin ({c_lat:.4f}, {c_lng:.4f})"
            st.session_state.route_result = None
            st.rerun()

else:
    # Default interactive map for point selection
    st.caption(
        "Search for locations in the sidebar, or **click the map** to set "
        "origin/destination. Toggle click mode in the sidebar."
    )
    default_map = build_map(PATNA_CENTER[0], PATNA_CENTER[1], zoom=13)

    # Show current selections on the map
    if st.session_state.origin_lat is not None:
        add_marker(
            default_map,
            st.session_state.origin_lat, st.session_state.origin_lng,
            f"Origin: {st.session_state.origin_label or 'selected'}",
            "blue", "play",
        )
    if st.session_state.dest_lat is not None:
        add_marker(
            default_map,
            st.session_state.dest_lat, st.session_state.dest_lng,
            f"Destination: {st.session_state.dest_label or 'selected'}",
            "darkred", "flag-checkered",
        )

    map_output = st_folium(default_map, use_container_width=True, height=560)

    # Process map clicks
    if map_output and map_output.get("last_clicked"):
        clicked = map_output["last_clicked"]
        c_lat, c_lng = clicked["lat"], clicked["lng"]

        if st.session_state.click_target == "origin":
            st.session_state.origin_lat = c_lat
            st.session_state.origin_lng = c_lng
            st.session_state.origin_label = f"Map pin ({c_lat:.4f}, {c_lng:.4f})"
            st.session_state.click_target = "destination"
            st.rerun()
        else:
            st.session_state.dest_lat = c_lat
            st.session_state.dest_lng = c_lng
            st.session_state.dest_label = f"Map pin ({c_lat:.4f}, {c_lng:.4f})"
            st.session_state.click_target = "origin"
            st.rerun()
