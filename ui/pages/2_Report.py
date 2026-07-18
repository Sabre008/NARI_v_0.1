"""
Report Page — Crowdsourced Safety Ratings
==========================================
Users submit a safety rating (1-5) for a location.
The rating is verified by the Isolation Forest trust engine.
"""

import streamlit as st
import h3
from supabase import create_client, ClientOptions
from app.config import settings

# Check login status FIRST
if "user_id" not in st.session_state or "access_token" not in st.session_state:
    st.warning("You must be logged in to submit a report.")
    st.stop()

# Initialize client WITH the user's access token to pass Row Level Security
opts = ClientOptions(headers={'Authorization': f'Bearer {st.session_state["access_token"]}'})
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY, options=opts)

st.title("Report a Safety Hazard")

if "user_id" not in st.session_state:
    st.warning("You must be logged in to submit a report.")
    st.stop()

with st.form("hazard_report_form"):
    hazard_type = st.selectbox("Hazard Type", ["Poor Lighting", "Eve Teasing", "Accident Prone Zone"])
    description = st.text_area("Description")
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("Latitude", value=25.5941, format="%.6f")
    with col2:
        lng = st.number_input("Longitude", value=85.1376, format="%.6f")
    
    severity = st.slider("Severity Rating (1-Minor, 5-Critical)", 1, 5, 3)
    
    submitted = st.form_submit_button("Submit Report")
    
    if submitted:
        # Calculate the H3 index automatically
        h3_idx = h3.latlng_to_cell(lat, lng, 8)
        
        try:
            supabase.table("reports").insert({
                "user_id": st.session_state["user_id"],
                "hazard_type": hazard_type,
                "description": description,
                "latitude": lat,
                "longitude": lng,
                "h3_index": h3_idx,
                "severity_rating": severity
            }).execute()
            st.success("Report submitted successfully! Thank you for keeping Patna safe.")
        except Exception as e:
            st.error(f"Error submitting report: {e}")