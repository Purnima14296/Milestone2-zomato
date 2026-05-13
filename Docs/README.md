# Zomato Restaurant Recommendation System - Documentation

## 📁 Repository Structure

Phases are documented under `Docs/`. Core pipeline code lives under `src/zomato_rec/`. **Phase 7** (`backend/`) and **Phase 8** (`frontend/`) are runnable apps at the repository root.

### Initial setup (Python + API extras)

```bash
pip install -e .
pip install -e ".[api]"
```

### 🗂️ Phase Organization

```
Docs/
├── README.md                    # This file - Phase documentation overview
├── phase_wise_architecture.md   # Complete system architecture
├── edge_cases.md               # Edge cases and error handling
├── problemstatement.md         # Problem statement and requirements
├── phase1/                     # Data Ingestion Phase (from src/zomato_rec/phase1)
├── phase2/                     # Data Collection & Normalization (from src/zomato_rec/phase2)
├── phase3/                     # Candidate Retrieval & Shortlisting (from src/zomato_rec/phase3)
├── phase4/                     # LLM Integration & Recommendation Generation (from src/zomato_rec/phase4)
├── phase5/                     # Presentation Layer & UX Enhancements (structure ready)
├── phase6/                     # Evaluation, Monitoring & Quality Loop (structure ready)
├── phase7/                     # Backend API (FastAPI) — REST service over the pipeline
└── phase8/                     # Frontend (Next.js) — web client for Phase 7
```

## 📋 Phase Descriptions

### Phase 1: Data Ingestion
- **Location**: `Docs/phase1/`
- **Purpose**: Raw data ingestion and preprocessing
- **Files**: `ingest.py`, `preprocess.py`, `__init__.py`

### Phase 2: Data Collection & Normalization
- **Location**: `Docs/phase2/`
- **Purpose**: Data collection, I/O operations, and normalization
- **Files**: `collect.py`, `io.py`, `models.py`, `normalize.py`, `__init__.py`

### Phase 3: Candidate Retrieval & Shortlisting
- **Location**: `Docs/phase3/`
- **Purpose**: Retrieve and shortlist candidate restaurants
- **Files**: `retrieve.py`, `shortlist.py`, `__init__.py`

### Phase 4: LLM Integration & Recommendation Generation
- **Location**: `Docs/phase4/`
- **Purpose**: LLM integration and final recommendation generation
- **Files**: `groq_client.py`, `parsing.py`, `prompting.py`, `recommend.py`, `run.py`, `__init__.py`

### Phase 5: Presentation Layer & UX Enhancements
- **Location**: `Docs/phase5/`
- **Purpose**: Enhanced presentation and user experience
- **Files**: `renderer.py`, `cli.py`, `ux_enhancements.py`, `run.py`, `main.py`, `README.md`

### Phase 6: Evaluation, Monitoring & Quality Loop
- **Location**: `Docs/phase6/`
- **Purpose**: System evaluation, monitoring, and quality improvement
- **Files**: `golden_tests.py`, `metrics.py`, `monitoring.py`, `dashboard.py`, `quality_improvement.py`, `README.md`

### Phase 7: Backend API Layer
- **Location**: `Docs/phase7/` (overview); **implementation**: `backend/` (FastAPI) — see `backend/README.md`
- **Purpose**: Production REST API wrapping preference validation, shortlisting (Phase 3), and LLM recommendations (Phase 4); health, metadata, CORS, rate limits, request IDs
- **Contract**: OpenAPI at `/docs`; JSON only; no secrets in responses

### Phase 8: Frontend Application
- **Location**: `Docs/phase8/` (overview); **implementation**: `frontend/` (Next.js) — see `frontend/README.md`
- **Purpose**: Browser UI for capturing preferences, calling Phase 7, and rendering ranked results with loading and error states
- **Stack**: Next.js App Router, TanStack Query, `NEXT_PUBLIC_API_URL` for the API base URL

## 🚀 Running the full stack (Phases 7–8)

Prerequisites: processed dataset (`data/processed/restaurants.parquet` from Phase 1), `GROQ_API_KEY` in the **repository root** `.env`, Python venv with `pip install -e ".[api]"`.

**Backend (Phase 7)** — run from the **repository root**:

```bash
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

- OpenAPI docs: http://127.0.0.1:8000/docs  
- Health: `GET /api/health`  
- Recommendations: `POST /api/recommendations`  
- Optional browse (no LLM): `GET /api/restaurants?location=...`  

Optional environment variable: `API_CORS_ORIGINS` (comma-separated), default `http://localhost:3000`.

**Frontend (Phase 8)**:

```bash
cd frontend
copy .env.local.example .env.local
npm install
npm run dev
```

App: http://localhost:3000 — set `NEXT_PUBLIC_API_URL` in `frontend/.env.local` if the API base URL differs from `http://127.0.0.1:8000`.

Implementation READMEs: `backend/README.md`, `frontend/README.md`.

## 📝 File Alignment

All files are properly aligned and readable:
- ✅ Python files have proper imports and structure
- ✅ TypeScript/JavaScript files are syntactically correct
- ✅ Configuration files are properly formatted
- ✅ Documentation files are complete and accurate
- ✅ No changes in output functionality

## 🛠️ Development Notes

- **Phases 1–6**: documented under `Docs/phase1`–`Docs/phase6` and implemented under `src/zomato_rec/phase1`–`phase6` (plus `web_ui` for optional Streamlit-style input during development)
- **Phases 7–8**: architecture in `Docs/phase_wise_architecture.md`; phase entry points in `Docs/phase7/README.md` and `Docs/phase8/README.md`. Runnable code typically lives in sibling apps such as **`backend/`** (FastAPI) and **`frontend/`** (Next.js)
- Keep **secrets** (Groq, DB) on the server (Phase 7) only; the browser client must never embed API keys

## 📚 Additional Documentation

- **Architecture**: See `phase_wise_architecture.md`
- **Edge Cases**: See `edge_cases.md`
- **Problem Statement**: See `problemstatement.md`
- **Phase-specific READMEs**: Each phase folder contains detailed documentation

---

This documentation structure ensures all phases are properly organized while maintaining complete functionality and readability.
