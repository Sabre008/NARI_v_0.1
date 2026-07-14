# 🧭 N.A.R.I — Navigation Aiding Reinforced Informatics

> Infrastructure-aware safety navigation engine for Patna, India.

## Overview

N.A.R.I combines deep learning, NLP, and constrained graph routing to provide
safe urban navigation. It scores geographic areas by infrastructure density,
adjusts for demographics and time-of-day, and integrates real-time news hazards
and verified crowdsourced reports.

See [`DESIGN.md`](DESIGN.md) for the full architecture and mathematical
formulation.

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
# Edit .env with your Supabase credentials
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
├── models/       # AI/ML modules (DNN, NLP, Trust Engine)
├── routing/      # Constrained routing engine (Yen's KSP)
├── services/     # Business logic orchestration
├── data/         # Supabase data layer & CRUD
├── ui/           # Streamlit multi-page frontend
├── notebooks/    # Research & prototyping
└── tests/        # Test suite
```

---

## Tech Stack

| Layer        | Technology                |
|--------------|---------------------------|
| Frontend     | Streamlit + Folium        |
| Backend API  | FastAPI + Uvicorn         |
| Database     | Supabase (PostgreSQL)     |
| DNN          | PyTorch                   |
| NLP          | Hugging Face Transformers |
| Geospatial   | OSMnx + H3 + NetworkX    |
| Anomaly Det. | scikit-learn              |

---

## License

This project is developed for academic purposes.
