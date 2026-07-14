"""
Navigate Page — Route Request & Safety Map
============================================
User selects origin/destination from Patna landmarks (or enters coordinates),
configures demographic parameters, and submits a route request to the
FastAPI backend. Results are rendered on a Folium map with fastest (red)
and safest (green) polylines, plus a metrics panel showing the safety
gain and distance delta.

Run the full platform:
    Terminal 1:  uvicorn app.main:app --reload
    Terminal 2:  streamlit run ui/Home.py
"""

import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# ── Page config ─────────────────────────────────────────
st.set_page_config(page_title="Navigate — N.A.R.I", page_icon="🗺️", layout="wide")

API_BASE = "http://127.0.0.1:8000"

# ── Patna landmark coordinates ──────────────────────────
LANDMARKS = {
    "Patna Junction":     (25.6093, 85.1376),
    "Kankarbagh":         (25.5942, 85.1748),
    "Gandhi Maidan":      (25.6120, 85.1473),
    "Bailey Road":        (25.6100, 85.1590),
    "Boring Road":        (25.6075, 85.1430),
    "Rajendra Nagar":     (25.6050, 85.1280),
    "Dak Bungalow":       (25.6105, 85.1425),
    "Patna City (East)":  (25.6070, 85.1900),
    "Custom coordinates": None,
}

# ── Sidebar controls ───────────────────────────────────
with st.sidebar:
    st.title("🧭 N.A.R.I")
    st.caption("Navigation Aiding Reinforced Informatics")
    st.divider()

    st.subheader("Route Parameters")

    origin_name = st.selectbox("Origin", list(LANDMARKS.keys()), index=0)
    dest_name = st.selectbox("Destination", list(LANDMARKS.keys()), index=1)

    # Custom coordinate inputs if selected
    if origin_name == "Custom coordinates":
        c1, c2 = st.columns(2)
        origin_lat = c1.number_input("Origin Lat", value=25.6093, format="%.4f", key="olat")
        origin_lng = c2.number_input("Origin Lng", value=85.1376, format="%.4f", key="olng")
    else:
        origin_lat, origin_lng = LANDMARKS[origin_name]

    if dest_name == "Custom coordinates":
        c1, c2 = st.columns(2)
        dest_lat = c1.number_input("Dest Lat", value=25.5942, format="%.4f", key="dlat")
        dest_lng = c2.number_input("Dest Lng", value=85.1748, format="%.4f", key="dlng")
    else:
        dest_lat, dest_lng = LANDMARKS[dest_name]

    st.divider()

    st.subheader("Demographics")
    gender = st.selectbox("Gender", ["Female", "Male"], index=0)
    hour = st.slider("Hour of day", min_value=0, max_value=23, value=22)

    time_label = "Night (20:00–07:59)" if hour >= 20 or hour < 8 else "Day (08:00–19:59)"
    st.caption(f"Time period: **{time_label}**")

    st.divider()
    submitted = st.button("Find Safe Route", type="primary", use_container_width=True)


# ── Helper functions ────────────────────────────────────
def build_map(center_lat, center_lng, zoom=13):
    """Create a base Folium map centred on the route midpoint."""
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=zoom,
        tiles="CartoDB positron",
    )
    return m


def draw_path(fmap, coords, color, label, weight=5, opacity=0.85):
    """Draw a polyline on the Folium map from a list of {lat, lng} dicts."""
    points = [(c["lat"], c["lng"]) for c in coords]
    folium.PolyLine(
        locations=points,
        color=color,
        weight=weight,
        opacity=opacity,
        tooltip=label,
    ).add_to(fmap)


def add_marker(fmap, lat, lng, label, color, icon_name):
    """Place a marker on the Folium map."""
    folium.Marker(
        location=[lat, lng],
        popup=label,
        icon=folium.Icon(color=color, icon=icon_name, prefix="fa"),
    ).add_to(fmap)


def add_legend(fmap, gender_label, hour_val, m_demo):
    """Inject an HTML legend into the Folium map."""
    html = f"""
    <div style="position:fixed; bottom:30px; left:30px; z-index:1000;
                background:white; padding:14px 18px; border-radius:10px;
                box-shadow:0 2px 12px rgba(0,0,0,0.15); font-size:13px;
                font-family: 'Segoe UI', sans-serif; line-height:1.6;">
        <b style="font-size:14px;">N.A.R.I Route Comparison</b><br>
        <span style="color:#D32F2F;">&#9644;&#9644;</span> Fastest Path<br>
        <span style="color:#388E3C;">&#9644;&#9644;</span> Safest Path (1.25x constrained)<br>
        <span style="font-size:11px; color:#666;">
            {gender_label} | {hour_val}:00 | M_demo = {m_demo}
        </span>
    </div>
    """
    fmap.get_root().html.add_child(folium.Element(html))


# ── Main content area ──────────────────────────────────
st.header("🗺️ Navigate — Find Your Safest Route")

if origin_name != "Custom coordinates" and dest_name != "Custom coordinates":
    st.caption(f"**{origin_name}** to **{dest_name}**")

if submitted:
    # Validate
    if origin_lat == dest_lat and origin_lng == dest_lng:
        st.error("Origin and destination cannot be the same location.")
        st.stop()

    # Build request payload
    payload = {
        "origin": {"lat": origin_lat, "lng": origin_lng},
        "destination": {"lat": dest_lat, "lng": dest_lng},
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
                "Make sure the FastAPI server is running: `uvicorn app.main:app --reload`"
            )
            st.stop()

    if resp.status_code != 200:
        st.error(f"API error ({resp.status_code}): {resp.json().get('detail', resp.text)}")
        st.stop()

    data = resp.json()

    if data["status"] != "ok":
        st.warning(f"Routing returned status: {data['status']} — {data.get('message', '')}")
        st.stop()

    # ── Extract response fields ─────────────────────
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

    # ── Metrics panel ───────────────────────────────
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
    m3.metric(
        label="Detour Factor",
        value=f"{detour:.3f}x",
    )
    m4.metric(
        label="M_demo",
        value=f"{m_demo:.2f}",
    )

    # ── Route comparison table ──────────────────────
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

    # ── Folium map ──────────────────────────────────
    st.divider()
    center_lat = (origin_lat + dest_lat) / 2
    center_lng = (origin_lng + dest_lng) / 2
    route_map = build_map(center_lat, center_lng, zoom=14)

    # Draw fastest path (red, behind)
    if fastest.get("coordinates"):
        draw_path(
            route_map, fastest["coordinates"], "#D32F2F",
            f"Fastest: {fastest_dist:,.0f} m | S={fastest_score:.4f}",
            weight=5, opacity=0.7,
        )

    # Draw safest path (green, on top)
    if safest.get("coordinates"):
        draw_path(
            route_map, safest["coordinates"], "#388E3C",
            f"Safest: {safest_dist:,.0f} m | S={safest_score:.4f} | {detour:.2f}x",
            weight=6, opacity=0.9,
        )

    # Origin and destination markers
    o_label = origin_name if origin_name != "Custom coordinates" else "Origin"
    d_label = dest_name if dest_name != "Custom coordinates" else "Destination"
    add_marker(route_map, origin_lat, origin_lng, f"Origin: {o_label}", "blue", "play")
    add_marker(route_map, dest_lat, dest_lng, f"Destination: {d_label}", "darkred", "flag-checkered")

    # Legend
    add_legend(route_map, gender, hour, m_demo)

    st_folium(route_map, use_container_width=True, height=560)

else:
    # Default: show Patna overview map before any route is requested
    default_map = build_map(25.6093, 85.1500, zoom=13)

    # Mark all landmarks
    for name, coords in LANDMARKS.items():
        if coords is not None:
            folium.CircleMarker(
                location=coords,
                radius=6,
                color="#1565C0",
                fill=True,
                fill_color="#42A5F5",
                fill_opacity=0.7,
                tooltip=name,
            ).add_to(default_map)

    st.caption("Select origin and destination from the sidebar, then click **Find Safe Route**.")
    st_folium(default_map, use_container_width=True, height=560)
