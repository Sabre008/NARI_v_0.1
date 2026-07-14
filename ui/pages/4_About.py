"""
About Page — Project Information
==================================
Explains the N.A.R.I methodology, mathematical formulation,
and tech stack.
"""

import streamlit as st

st.set_page_config(page_title="About — N.A.R.I", page_icon="ℹ️", layout="wide")

st.header("ℹ️ About N.A.R.I")

st.markdown(
    """
    ## Navigation Aiding Reinforced Informatics

    N.A.R.I is an AI-centric safety navigation engine for **Patna, India**.
    It combines deep learning, NLP, and constrained routing to provide
    infrastructure-aware safe navigation.

    ---

    ### Core Modules

    | Module | Description |
    |--------|-------------|
    | **Safety DNN** | PyTorch MLP scoring infrastructure density per H3 cell → S_infra |
    | **NLP Hazard Engine** | Hugging Face zero-shot + NER extracts incidents from news feeds |
    | **Trust Engine** | Isolation Forest detects spam reports; verified ratings decay over time |
    | **Constrained Router** | Yen's K-Shortest Paths with 1.25× distance constraint |

    ---

    ### Safety Score Formula

    ```
    S_total = (S_infra · M_demo) + (α · Crowd_decay) − (β · News_severity)
    ```

    Where:
    - **S_infra**: Base infrastructure score from the DNN
    - **M_demo**: Demographic multiplier (gender × time-of-day)
    - **Crowd_decay**: Time-decayed verified user ratings
    - **News_severity**: Active NLP-detected hazard penalty

    ---

    ### Tech Stack

    - **Backend**: FastAPI + Uvicorn
    - **Frontend**: Streamlit + Folium
    - **Database**: Supabase (PostgreSQL)
    - **ML**: PyTorch, scikit-learn, Hugging Face Transformers
    - **Geospatial**: OSMnx, H3, NetworkX
    """
)
