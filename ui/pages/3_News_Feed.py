"""
News Feed Page — Live Hazard Alerts
=====================================
Displays active news-detected hazards on a map with
severity indicators and expiry timers.
"""

import streamlit as st
import requests

st.set_page_config(page_title="News Feed — N.A.R.I", page_icon="📰", layout="wide")

st.title("📡 Live NLP Hazard Scanner")
st.markdown("Scrape local Patna news feeds to detect and map active safety hazards.")

col1, col2 = st.columns([3, 1])

with col2:
    if st.button("🔄 Scan News Now"):
        with st.spinner("Scraping feeds and running BERT pipeline..."):
            try:
                # Pointing to the correct API endpoint
                response = requests.post("http://127.0.0.1:8000/api/v1/update_hazards", timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"Scan complete! {data.get('hazards_detected', 0)} active hazards mapped to the routing engine.")
                    
                    if data.get("hazards_detected", 0) > 0:
                        st.markdown("### Detected Incidents")
                        for incident in data.get("incidents", []):
                            st.info(f"**Severity {incident['severity_score']}** | {incident['description']}")
                            st.caption(f"Mapped to H3 Cell: {incident['centroid_id']}")
                else:
                    st.error(f"Failed to scan news. API returned: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to the N.A.R.I API. Is the backend running?")
            except requests.exceptions.Timeout:
                st.error("Request timed out. The NLP pipeline might be taking a while.")

with col1:
    st.info("📡 Click 'Scan News Now' to run the NLP hazard pipeline.")
