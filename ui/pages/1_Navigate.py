"""
Navigate Page — Route Request & Safety Map
============================================
User inputs origin/destination, gender, and time.
Displays the safest constrained route on a Folium map
with segment-level safety colour coding.
"""

import streamlit as st

st.set_page_config(page_title="Navigate — N.A.R.I", page_icon="🗺️", layout="wide")

st.header("🗺️ Navigate — Find Your Safest Route")

with st.form("route_form"):
    col1, col2 = st.columns(2)
    with col1:
        origin_lat = st.number_input("Origin Latitude", value=25.6117, format="%.4f")
        origin_lng = st.number_input("Origin Longitude", value=85.1390, format="%.4f")
    with col2:
        dest_lat = st.number_input("Destination Latitude", value=25.5942, format="%.4f")
        dest_lng = st.number_input("Destination Longitude", value=85.1748, format="%.4f")

    gender = st.selectbox("Gender", ["male", "female"])
    submitted = st.form_submit_button("🔍 Find Safe Route")

if submitted:
    st.info("⏳ Route computation will be wired to the FastAPI backend.")
    # TODO: Call POST /api/v1/route and render result on Folium map
