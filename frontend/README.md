# Phase 8 — Next.js frontend

## Setup

```bash
cd frontend
copy .env.local.example .env.local
npm install
npm run dev
```

Open http://localhost:3000 . The UI calls the Phase 7 API; set `NEXT_PUBLIC_API_URL` in `.env.local` if the backend is not at `http://127.0.0.1:8000`.

## Scripts

| Command | Purpose |
|---------|---------|
| `npm run dev` | Development server on port 3000 |
| `npm run build` | Production build |
| `npm run start` | Run production build |

No Groq or other secrets belong in this app — only the public API base URL.
