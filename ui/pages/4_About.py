"""
About Page: Project Information
==================================
Explains the N.A.R.I methodology, mathematical formulation,
and tech stack.
"""

import streamlit as st

st.set_page_config(page_title="About: N.A.R.I", page_icon="ℹ️", layout="wide")

st.header("ℹ️ About N.A.R.I")

st.markdown(
    """
## About N.A.R.I. (Navigation Aiding Reinforced Informatics)

Traditional navigation systems like GPS run on shortest-path algorithms that prioritize
one thing: **speed**. They measure distance and traffic but entirely ignore the complex,
real-world socio-geographical realities of urban environments. If the fastest route cuts
through a flooded street, a riot, or a historically unsafe, unlit zone, standard mapping
apps will still send you there.

N.A.R.I. bridges this critical gap. Designed as a **safety-centric augmentation layer**,
it balances computational travel efficiency with human safety. Instead of just finding
the fastest path, N.A.R.I. actively calculates the **mathematically safest path** by
dynamically avoiding hazard zones.
"""
)

st.info(
    "🚧 **This project is currently in the testing and development stage.** "
    "The idea is to validate the core hypothesis that real-time NLP threat extraction, "
    "demographic-aware cost functions, and crowdsourced safety intelligence can be "
    "combined into a single routing engine that meaningfully improves navigation safety "
    "in underserved urban environments. Patna, Bihar serves as our proof-of-concept region."
)

st.divider()

st.markdown(
    """
### Core Modules

| Module | Description |
|--------|-------------|
| **Safety DNN** | PyTorch MLP scoring infrastructure density per H3 cell → S_infra |
| **NLP Hazard Engine** | Hugging Face NER extracts incidents from news feeds |
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

st.divider()

st.markdown(
    """
### How It Works Under the Hood

**Live Threat Intelligence:**
The engine uses Natural Language Processing (NLP) to continuously scrape public news
feeds and civic reports, extracting the exact geographic coordinates of live threats
(like civil unrest or waterlogging).

**Demographic Context:**
Physical geography poses different risks depending on *who* is traveling and *when*.
The system uses a Demographic Multiplier ($M_{demo}$) to adjust route safety scores
based on user profile (e.g., gender) and the time of day.

**Dynamic Cost Balancing:**
Hazards mathematically penalize specific road segments, forcing the algorithm to find
a safer detour. To prevent endless rerouting, N.A.R.I. strictly bounds these detours
to a maximum of **1.25x** the distance of the fastest route.

**Self-Healing Maps:**
Crowdsourced hazard reports utilize a **24-hour time-decay function**. As time passes,
the penalty naturally fades to zero, automatically reopening the route without manual
intervention.
"""
)

st.divider()

st.markdown(
    """
### Steps to Use the Web Platform

Since N.A.R.I. is fully web-hosted, all heavy geospatial computations are handled
asynchronously on our backend servers. No local installation is required.

1. **Authenticate:** Navigate to the Home page and log in or sign up.

2. **Access the Map:** Open the **Navigate** tab from the sidebar.

3. **Set Waypoints:** Use the sidebar search to geocode locations within the
   Patna, Bihar region, or click the "Map Click Mode" to drop pins directly
   onto the interactive map.

4. **Configure Context:** Verify your demographic parameters and adjust the
   time-of-day slider if you are planning a future trip.

5. **Find Safe Route:** Click the primary action button. The system will query
   the active threat database and render two paths: the standard fastest route
   (**Red**) and the $S_{total}$ optimized safest route (**Green**).

6. **Review Metrics:** Check the dynamic metrics panel to review the exact
   safety gains, total detour distance, and specific hazard zones the algorithm
   successfully avoided.
"""
)
