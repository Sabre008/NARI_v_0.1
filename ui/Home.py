"""
N.A.R.I — Streamlit Home Page / Authentication Gateway
======================================================
Landing page providing Email/Password Login and Sign-Up via Supabase.
Upon login, sets user_id, access_token, and user_gender in session_state,
unlocking the rest of the application (e.g. 1_Navigate).

Run:  streamlit run ui/Home.py
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from supabase import create_client, Client
from app.config import settings

@st.cache_resource
def init_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

supabase = init_supabase()

st.set_page_config(
    page_title="N.A.R.I — Authentication",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("🧭 N.A.R.I — Safe Navigation")
st.markdown("**Infrastructure-aware safety navigation for Patna, India.**")

if "user_id" in st.session_state:
    st.success("Successfully authenticated!")
    st.markdown("You can now use the **Navigate** page from the sidebar to find the safest route.")
    
    st.divider()
    
    st.write(f"**User ID:** {st.session_state['user_id']}")
    st.write(f"**Profile Gender:** {st.session_state.get('user_gender', 'Unknown')}")
    
    if st.button("Log out"):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
        st.session_state.clear()
        st.rerun()
else:
    st.info("Please authenticate to access the N.A.R.I platform.")
    
    tab1, tab2 = st.tabs(["Log In", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In")
            
            if submitted:
                if not email or not password:
                    st.error("Please enter email and password.")
                else:
                    try:
                        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        if res.user:
                            st.session_state["user_id"] = res.user.id
                            st.session_state["access_token"] = res.session.access_token
                            
                            # Fetch gender from users table
                            try:
                                user_record = supabase.table("users").select("gender").eq("id", res.user.id).execute()
                                if user_record.data:
                                    st.session_state["user_gender"] = user_record.data[0]["gender"].capitalize()
                                else:
                                    st.session_state["user_gender"] = "Female" # Fallback
                            except Exception:
                                st.session_state["user_gender"] = "Female" # Fallback on error
                                
                            st.rerun()
                    except Exception as e:
                        st.error(f"Login failed: {e}")
                        
    with tab2:
        with st.form("signup_form"):
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            gender = st.selectbox("Gender", ["Female", "Male"])
            signup_submitted = st.form_submit_button("Sign Up")
            
            if signup_submitted:
                if not new_email or not new_password:
                    st.error("Please enter email and password.")
                else:
                    try:
                        res = supabase.auth.sign_up({"email": new_email, "password": new_password})
                        if res.user:
                            # Insert into users table
                            try:
                                supabase.table("users").insert({
                                    "id": res.user.id,
                                    "gender": gender.lower()
                                }).execute()
                            except Exception as e:
                                # Sometimes user insert might fail if table isn't ready or permissions, 
                                # but sign_up succeeded.
                                print(f"User table insert error: {e}")
                            st.success("Sign up successful! Please log in.")
                    except Exception as e:
                        st.error(f"Sign up failed: {e}")
