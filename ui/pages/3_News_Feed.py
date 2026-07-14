"""
News Feed Page — Live Hazard Alerts
=====================================
Displays active news-detected hazards on a map with
severity indicators and expiry timers.
"""

import streamlit as st

st.set_page_config(page_title="News Feed — N.A.R.I", page_icon="📰", layout="wide")

st.header("📰 Active Hazard Alerts")

col1, col2 = st.columns([3, 1])

with col2:
    if st.button("🔄 Scan News Now"):
        st.info("⏳ NLP scan will be wired to POST /api/v1/parse_news.")
        # TODO: Call POST /api/v1/parse_news

with col1:
    st.info("📡 Active hazards will be displayed on the map once the NLP pipeline is connected.")
    # TODO: Fetch active hazards and render on Folium map with severity markers
