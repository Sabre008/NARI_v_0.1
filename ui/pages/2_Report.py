"""
Report Page — Crowdsourced Safety Ratings
==========================================
Users submit a safety rating (1-5) for a location.
The rating is verified by the Isolation Forest trust engine.
"""

import streamlit as st

st.set_page_config(page_title="Report — N.A.R.I", page_icon="📝", layout="wide")

st.header("📝 Submit a Safety Report")

with st.form("report_form"):
    lat = st.number_input("Latitude", value=25.6117, format="%.4f")
    lng = st.number_input("Longitude", value=85.1390, format="%.4f")
    rating = st.slider("Safety Rating", min_value=1, max_value=5, value=3)
    notes = st.text_area("Optional Notes", placeholder="Describe the area conditions...")
    submitted = st.form_submit_button("📤 Submit Report")

if submitted:
    st.info("⏳ Report submission will be wired to the FastAPI backend.")
    # TODO: Call POST /api/v1/submit_report
