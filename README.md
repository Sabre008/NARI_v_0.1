# N.A.R.I: Navigation Aiding Reinforced Informatics

> An experimental, infrastructure-aware routing prototype tested on Patna, Bihar.

## Overview

N.A.R.I is an exploratory project attempting to incorporate urban infrastructure density, user demographic context, live news-extracted incidents, and crowdsourced feedback into route calculation. Standard navigation engines primarily focus on travel time and shortest distance. This prototype investigates how safety considerations might be weighted alongside distance.

### Research and Current Stage

This project is in an early experimental stage:
- **Proof of Concept**: The platform is currently a research prototype evaluated on Patna, Bihar to see if multi-source safety signals can practically influence graph traversal.
- **Ongoing Research Needed**: Significant empirical research is still required. The safety scoring formulas, demographic multipliers, and synthetic training data are preliminary hypotheses and approximations rather than definitive ground truth.
- **Not a Production Safety System**: Route suggestions are experimental explorations of cost functions and should not be relied upon as absolute safety guarantees.

Further documentation on the methodology and formulations can be reviewed on the in-app **About** page (`ui/pages/4_About.py`).

---

## Quick Start

### 1. Environment Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

### 2. Configuration

```bash
copy .env.example .env
# Edit .env with your Supabase credentials if using auth and report submission
```

### 3. Run the Backend (FastAPI)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Run the Frontend (Streamlit)

```bash
streamlit run ui/Home.py
```

---

## Project Structure

```
NARI_v_0.1/
├── app/          # FastAPI backend (routers, schemas, config)
├── models/       # Experimental models (DNN, NLP, Trust Engine)
├── routing/      # Routing logic and cost functions (Yen's KSP)
├── services/     # Scoring and demographic utilities
├── data/         # Supabase client, migrations, and local graph cache
├── ui/           # Streamlit interface
├── notebooks/    # Exploratory notebooks
└── tests/        # Test suite
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit, Folium |
| Backend API | FastAPI, Uvicorn |
| Database | Supabase (PostgreSQL) |
| DNN | PyTorch |
| NLP | Hugging Face Transformers |
| Geospatial | OSMnx, H3, NetworkX |
| Anomaly Detection | scikit-learn |

---

## License and Disclaimer

Developed for academic and experimental research purposes.
