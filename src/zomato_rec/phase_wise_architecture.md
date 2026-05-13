## Phase-wise Architecture: AI-Powered Restaurant Recommendation System

### Phase 0 — Project Setup (Foundation)

- **Repo structure**: `Docs/`, `src/`, `data/` (or `storage/`)
- **Configuration**: dataset source/path, model provider + API key, runtime environment variables
- **Logging**: basic request + error logs

**Deliverable**: runnable skeleton (CLI or minimal UI) with configs wired.

---

### Phase 1 — Data Ingestion & Preparation (Offline/Batch)

- **Dataset loader**: pulls Zomato dataset from Hugging Face
- **Preprocessor/cleaner**: missing values, duplicates, normalization (city/cuisine/cost/rating)
- **Schema mapping**: standardize fields like:
  - restaurant name
  - city/location
  - cuisine(s)
  - average cost / price range
  - rating
  - other useful metadata (if available)
- **Storage layer (choose one)**:
  - simple: CSV/Parquet
  - query-friendly: SQLite/Postgres

**Data flow**: Hugging Face dataset → preprocess/normalize → stored restaurant dataset.

**Deliverable**: clean, queryable dataset with consistent schema.

---

### Phase 2 — User Preference Collection & Validation (Online)

- **Input UI**: capture location, budget, cuisine, minimum rating, extra preferences
- **Validator/normalizer**:
  - budget mapping (low/medium/high → numeric range)
  - city/cuisine standardization (case, synonyms, typos if needed)

**Deliverable**: validated `UserPreferences` object ready for retrieval + prompting.

---

### Phase 3 — Candidate Retrieval (Deterministic Layer)

- **Filter engine**: applies hard constraints (city, min rating, budget range, cuisine)
- **Scoring/heuristics (optional)**: tie-break scoring (rating, budget match, cuisine match)
- **Shortlist builder**: select top \(N\) candidates for the LLM (e.g., 20–50)

**Data flow**: stored dataset + user preferences → filter/score → candidate shortlist (structured).

**Deliverable**: compact, high-quality candidate list (cost-controlled, relevant).

---

### Phase 4 — LLM Recommendation & Explanation (AI Layer)

- **Prompt builder**: formats user preferences + candidate shortlist + strict output rules
- **LLM gateway**: model call (timeouts, retries, rate-limit handling)
- **Structured output parser**: enforce JSON output (ranked list + explanations)
- **Quality/safety checks**:
  - ensure recommendations come only from the provided shortlist
  - handle malformed outputs safely

**Deliverable**: ranked recommendations with concise, human-like explanations.

---

### Phase 5 — Presentation Layer (User Output) ✅ COMPLETED

- **Renderer**: show top \(K\) results with:
  - restaurant name, cuisine, rating, estimated cost, location
  - AI-generated explanation with word wrapping
  - Multiple output formats: Console, JSON, Markdown, Enhanced
- **UX enhancements**:
  - **Sorting**: By rank, rating (high/low), cost (high/low), name (A/Z)
  - **Filtering**: By minimum rating, maximum cost, cuisine, location
  - **Comparison tools**: Side-by-side restaurant analysis with statistics
  - **Preference refinement**: AI-powered suggestions for better results
  - **Filter suggestions**: Context-aware filtering recommendations

**Deliverable**: user-friendly output for comparison and decision-making.

**Implementation Details**:
- `phase5/renderer.py`: Core rendering functionality
- `phase5/ux_enhancements.py`: Advanced UX features
- `phase5/main_simple.py`: Standalone CLI interface
- Supports Unicode-safe console output for cross-platform compatibility

---

### Phase 6 — Evaluation, Monitoring & Iteration (Quality Loop)

- **Golden test queries**: repeatable preference cases to validate behavior
- **Metrics**:
  - constraint satisfaction (location/budget/cuisine/rating match)
  - diversity of results
  - latency and token/cost tracking
- **Logging/monitoring**: input stats (anonymized), shortlist size, parse success, error rates

**Deliverable**: measurable quality improvements over time (prompt + retrieval tuning).

---

### Phase 7 — Backend API Layer (Production Service)

Exposes the pipeline (Phases 2–4) as a **stateless HTTP API** so clients, automation, and the web UI can call it safely and consistently.

- **Framework**: FastAPI (or equivalent) with async-capable workers, OpenAPI/Swagger docs auto-generated.
- **Service orchestration** (single place for business flow):
  - validate/normalize preferences (Phase 2 models + rules)
  - build shortlist from processed dataset (Phase 3)
  - call LLM and validate output (Phase 4)
  - return stable JSON contracts (ranked list + metadata)
- **Core endpoints** (indicative):
  - `GET /api/health` — liveness/readiness, dependency checks (dataset path, Groq key present)
  - `POST /api/recommendations` — body: user preferences + `top_k`; response: ranked restaurants + explanations + request metadata (latency, model id)
  - `GET /api/metadata` — dataset/pipeline version, supported cities, model name (no secrets)
  - optional: `GET /api/restaurants` — browse/filter against processed data without LLM (cheaper)
- **Cross-cutting concerns**:
  - **CORS** configured for the Phase 8 origin(s) only in non-local environments
  - **Request IDs** and structured logging (correlate with Phase 6 metrics)
  - **Timeouts and retries** on outbound LLM calls; bounded `max_tokens` / `top_k`
  - **Rate limiting** (per IP or API key) to control cost and abuse
  - **Secrets** only via environment variables (never committed)
- **Deployment**: container image (Docker), one process per CPU with uvicorn workers or behind a reverse proxy; health checks wired for orchestrators.

**Deliverable**: a documented, testable REST API that wraps the recommendation pipeline and is ready for the frontend and external consumers.

---

### Phase 8 — Frontend Application (Web Client)

A **dedicated web client** that talks only to Phase 7 over HTTPS (or local dev proxy), keeping presentation and API concerns separate from the Python pipeline.

- **Stack** (recommended): **Next.js** (App Router) + **TypeScript** + **Tailwind CSS** for layout and responsive behavior.
- **Data layer**: typed API client (hand-written or generated from OpenAPI); **TanStack Query** for caching, loading/error states, and deduplication; optional **Zustand** for UI-only state (wizard step, filters).
- **Key surfaces**:
  - **Preference capture**: location, budget, cuisines, minimum rating, free-text extras — aligned with Phase 2 `UserPreferences`
  - **Results**: ranked cards with rating, cost, cuisines, LLM explanation; optional export/share
  - **Empty/error states**: clear messages when shortlist is empty, LLM validation fails, or API is unavailable
- **Quality bar**:
  - accessible forms (labels, focus order, errors announced)
  - mobile-first layout; sane loading skeletons during recommendation requests
  - environment-based **API base URL** (`NEXT_PUBLIC_API_URL` or build-time config), no secrets in client bundles
- **Build & ship**: static assets + Node server or edge deployment; CI runs lint, typecheck, and smoke tests against a mocked or staging API.

**Deliverable**: a deployable frontend that exercises the full user journey through the backend API and matches the product’s UX expectations.

---

## End-to-End Flow (High-level)

### Core pipeline (Phases 1–6, shared by CLI and API)

User Preferences → Validation → Candidate Retrieval (Dataset) → Prompt Builder → LLM → Parse/Validate → Structured Results → Logs/Metrics

### Web path (Phases 7–8)

```text
Browser (Phase 8)  --HTTPS-->  Backend API (Phase 7)  -->  Phases 2 → 3 → 4  -->  JSON response  -->  UI render
                                      |
                                      +--> Phase 1 dataset (read)  +  optional Phase 6 telemetry
```

### Offline / CLI path (unchanged)

Local scripts and storage (`storage/preferences.json`, `storage/shortlist.json`) continue to support development and regression tests without running the HTTP stack.

