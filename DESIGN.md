# Navigation Aiding Reinforced Informatics (N.A.R.I)
**Target City:** Patna, Bihar, India (Urban/Town Boundaries)
**Objective:** A deployable, AI-centric software package for safe, infrastructure-aware urban navigation, primarily themed around women's safety but universally applicable.

## 1. System Architecture & Constraints
* **Frontend UI:** Streamlit (Multi-page interface, rendering map overlays via `streamlit-folium`).
* **Backend API:** FastAPI (Python-based AI hub, handling asynchronous calculations).
* **Database & Auth:** Supabase (PostgreSQL for user accounts, crowd metrics, and incident tables).
* **Hardware Profile:** Optimized for lightweight local execution (avoiding heavy cloud reliance for core logic).
* **Core Rule:** No unnecessary features (e.g., no chatbots). Focus solely on innovative, highly accurate safety navigation.

## 2. Core AI Modules

### A. Infrastructural Safety Scoring (The "Brain")
* **Methodology:** Deep Neural Network (DNN) Regression Model (PyTorch) applied to an H3 Hexagonal Spatial Grid.
* **Inputs:** Infrastructure density (hospitals, street lights, police stations), intersection connectivity, and OpenStreetMap (OSM) land-use tags.
* **Output:** Normalized Base Safety Index ($S_{infra}$) ranging from 0.0 to 1.0 per grid cell.
* **Training:** Pre-trained on synthetic data derived from heuristics, fine-tuned with verified user reports.

### B. NLP News & Hazard Extraction
* **Process:** Scrapes local public data/news feeds.
* **Tooling:** Hugging Face pipeline (Zero-shot classification + NER) to extract severity and spatial coordinates.
* **Effect:** Applies a temporary dynamic drop penalty ($M_{news}$) to the safety index of affected graph edges.

### C. Crowdsourced Trust Engine
* **Anomaly Detection:** Unsupervised Isolation Forest model to identify and block spam/malicious reports based on account history and velocity.
* **Time-Decay Rating:** Verified ratings (1-5 scale) naturally diminish over time to prioritize fresh data, using the formula:
  $$W_{report} = \text{Rating} \cdot e^{-\lambda t}$$

## 3. Mathematical Routing Formulation
* **Algorithm:** Yen’s K-Shortest Paths (via NetworkX / OSMnx).
* **Constraint:** The navigation system must find the best safety score path while ensuring the total path distance remains within limits:
  $$\text{Distance}_{candidate} \le 1.25 \times \text{Distance}_{shortest}$$
* **Dynamic Cost Function ($S_{total}$):**
  $$S_{total} = (S_{infra} \cdot M_{demo}) + (\alpha \cdot \text{Crowd}_{decay}) - (\beta \cdot \text{News}_{severity})$$

### Demographic Context Matrix ($M_{demo}$)
Backed by NCRB crime data, adjusting safety perception based on gender and time of day (8 AM - 8 PM vs. 8 PM - 8 AM).
* **Male / Day:** 1.00
* **Male / Night:** 0.80
* **Female / Day:** 0.90
* **Female / Night:** 0.67

## 4. Database Schema (Supabase)

### `users`
* `user_id`: UUID (Primary Key, derived via Supabase Auth)
* `gender`: VARCHAR(10) (Only demographic collected)
* `trust_score`: FLOAT (Default = 1.0)
* `account_created`: TIMESTAMPTZ

### `locations_grid`
* `centroid_id`: BIGINT (Primary Key, mapping to spatial H3 Hex Index)
* `geometry`: GEOMETRY
* `base_infra_score`: FLOAT (Pre-calculated via the spatial Neural Network)
* `poi_metadata`: JSONB (Stores raw feature count dictionaries)

### `crowd_reports`
* `report_id`: BIGINT (Generated Identity)
* `centroid_id`: BIGINT (Foreign Key -> locations_grid)
* `user_id`: UUID (Foreign Key -> users)
* `rating_score`: INT (Scale 1 to 5)
* `timestamp`: TIMESTAMPTZ
* `is_verified`: BOOLEAN (State flag driven by the Isolation Forest model)

### `news_hazards`
* `incident_id`: BIGINT
* `centroid_id`: BIGINT
* `severity_score`: FLOAT
* `expiry_timer`: TIMESTAMPTZ

## 5. Implementation Roadmap
1. **Data Curation:** Map Patna via OSMnx into a hexagonal grid (H3).
2. **Intelligence Layer:** Generate synthetic training data, fit the PyTorch MLP (`safety_net.pth`), and implement the NLP pipeline.
3. **API & Routing:** Build FastAPI endpoints (`/route`, `/parse_news`, `/submit_report`) and implement Yen's K-Shortest Paths.
4. **UI Integration:** Wire the Streamlit dashboard to display paths on Folium maps with safety-vs-speed visual justifications.