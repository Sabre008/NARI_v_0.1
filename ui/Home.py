"""
N.A.R.I — Streamlit Home Page
===============================
Landing page with a Folium map overview of Patna showing the
safety-scored H3 grid overlay.

Run:  streamlit run ui/Home.py
"""

import streamlit as st

st.set_page_config(
    page_title="N.A.R.I — Safe Navigation",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🧭 N.A.R.I — Navigation Aiding Reinforced Informatics")
st.markdown(
    """
    **Infrastructure-aware safety navigation for Patna, India.**

    Use the sidebar to:
    - 🗺️ **Navigate** — Find the safest route between two points
    - 📝 **Report** — Submit a crowdsourced safety rating
    - 📰 **News Feed** — View active hazard alerts
    - ℹ️ **About** — Learn how N.A.R.I works

    ---
    """
)

# TODO: Render a Folium map with the H3 safety grid overlay
st.info("🗺️ Map overlay will be rendered here once grid data is available.")
