## Milestone 1 — Zomato Restaurant Recommendation (Phase 0)

This repo contains the foundation for an AI-powered restaurant recommendation system inspired by Zomato.

### Folder structure

- `Docs/`: project documentation
- `src/`: application source code
- `data/`: local datasets (ignored by git)
- `storage/`: local DB files (ignored by git)
- `backend/`: Phase 7 FastAPI service (repo root)
- `frontend/`: Phase 8 Next.js app (repo root)

### Setup (Windows PowerShell)

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
pip install -e ".[api]"
```

Create your env file:

```bash
copy .env.example .env
```

Run the phase-0 sanity check:

```bash
python -m zomato_rec.main --check
```

### Phase 1 (data ingestion)

Ingest + preprocess the dataset into `data/processed/`:

```bash
python -m zomato_rec.phase1.ingest
```

### Phase 2 (user preferences)

Collect validated user preferences and save them to `storage/preferences.json`:

#### Web UI (recommended)

Run the basic web UI (this is the primary input method):

```bash
streamlit run src/zomato_rec/web_ui/app.py
```

#### CLI (optional)

```bash
python -m zomato_rec.phase2.collect --interactive
```

Or non-interactive:

```bash
python -m zomato_rec.phase2.collect --location Bellandur --budget "500-800" --cuisines "Italian, Chinese" --min-rating 4
```

### Phase 3 (candidate retrieval + shortlist)

Build a deterministic shortlist (JSON) from the processed dataset + saved preferences:

```bash
python -m zomato_rec.phase3.shortlist --top-n 30
```

### Phase 4 (LLM ranking + explanations with Groq)

1) Set your Groq key in `.env`:

- `GROQ_API_KEY=...`
- `GROQ_MODEL=llama-3.3-70b-versatile` (or any Groq-supported model)

2) Run:

```bash
python -m zomato_rec.phase4.run --top-k 5
```

### Phase 7–8 (API + Next.js web UI)

Requires Phase 1 completed (`data/processed/restaurants.parquet`) and `GROQ_API_KEY` in `.env`.

**Terminal 1 — backend (from repo root, venv active)**

```bash
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Optional: `API_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000` in `.env` if you use another origin.

**Terminal 2 — frontend**

```bash
cd frontend
copy .env.local.example .env.local
npm install
npm run dev
```

Open http://localhost:3000 . Set `NEXT_PUBLIC_API_URL` in `frontend/.env.local` if the API is not on `http://127.0.0.1:8000`.

See `backend/README.md` and `frontend/README.md` for details.

### Phase 9 — Streamlit (hosted Python UI)

The Streamlit app runs **Phases 2 → 4 in-process** (same engine as `backend.app.pipeline.run_recommendations`), so users get full recommendations without the Next.js + FastAPI stack.

**Local**

```bash
streamlit run streamlit_app.py
```

(or `streamlit run src/zomato_rec/web_ui/app.py` — same app.)

Use repo root as the working directory. For **Streamlit Cloud**, use the in-app **Prepare dataset from Hugging Face** button the first time (or run Phase 1 locally to create `data/processed/restaurants.parquet`). Set `GROQ_API_KEY` in `.env` or copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill values.

**Streamlit Community Cloud (free tier)**

1. Push the repo to GitHub.
2. Create a new app → **Main file path:** `streamlit_app.py` (repo root). You can also use `src/zomato_rec/web_ui/app.py` if you prefer.
3. Python packages: use the repo-root **`requirements.txt`** (Streamlit’s default).
4. **Secrets** (app settings): at minimum `GROQ_API_KEY`. Optional: `GROQ_MODEL`, `ZOMATO_PROCESSED_DATASET` (absolute path if you mount or fetch data elsewhere).
5. **Dataset:** `data/` is gitignored, so Streamlit Cloud starts **without** `restaurants.parquet`. The app shows **Prepare dataset from Hugging Face** — click it once per fresh machine (first run ~1–4 minutes). Free-tier apps may lose the file after long idle periods; run the button again if recommendations fail. Alternatively commit/mount Parquet or set **`ZOMATO_PROCESSED_DATASET`** in secrets.

Cold starts on the free tier are normal; first model request may take tens of seconds.
