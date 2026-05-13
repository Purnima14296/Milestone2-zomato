from __future__ import annotations

import json
import os
import time
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from zomato_rec.config import Settings
from zomato_rec.phase2.io import save_preferences
from zomato_rec.phase2.models import BudgetRange, UserPreferences
from zomato_rec.phase3.retrieve import load_processed_dataset, run_phase3
from zomato_rec.phase4.recommend import run_phase4

from backend.app.paths import repo_root
from backend.app.schemas import (
    PreferencesIn,
    RecommendationMetadata,
    RecommendationRequest,
    RecommendationResponse,
)


def _to_user_preferences(p: PreferencesIn) -> UserPreferences:
    budget = None
    if p.budget is not None and (p.budget.min is not None or p.budget.max is not None):
        budget = BudgetRange(min=p.budget.min, max=p.budget.max)
    return UserPreferences(
        location=p.location.strip(),
        budget=budget,
        cuisines=list(p.cuisines),
        minimum_rating=p.minimum_rating,
        additional_preferences=p.additional_preferences.strip() if p.additional_preferences else None,
    )


def default_dataset_path() -> Path:
    """Resolved Parquet path; override with env `ZOMATO_PROCESSED_DATASET` (e.g. Streamlit Cloud / CI)."""
    override = os.environ.get("ZOMATO_PROCESSED_DATASET", "").strip()
    if override:
        return Path(override)
    root = repo_root()
    return root / "data" / "processed" / "restaurants.parquet"


def list_dataset_cities(*, limit: int = 500) -> list[str]:
    """Distinct city/locality labels from the processed dataset (for UI dropdowns)."""
    dataset = default_dataset_path()
    if not dataset.is_file():
        return []
    df = pd.read_parquet(dataset, columns=["city"])
    s = df["city"].dropna().astype(str).str.strip()
    s = s[s != ""]
    unique = sorted(frozenset(s), key=str.casefold)
    if limit > 0 and len(unique) > limit:
        return unique[:limit]
    return unique


def run_recommendations(req: RecommendationRequest) -> RecommendationResponse:
    settings = Settings()
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    dataset = default_dataset_path()
    if not dataset.is_file():
        raise FileNotFoundError(f"Processed dataset not found: {dataset}")

    prefs = _to_user_preferences(req.preferences)
    t0 = time.perf_counter()

    with TemporaryDirectory(prefix="zomato_phase7_") as tmp:
        tmp_path = Path(tmp)
        prefs_path = tmp_path / "preferences.json"
        shortlist_path = tmp_path / "shortlist.json"
        recs_path = tmp_path / "recommendations.json"
        report_path = tmp_path / "phase4_report.json"

        save_preferences(prefs, str(prefs_path))

        p3 = run_phase3(
            processed_dataset_path=str(dataset),
            preferences_path=str(prefs_path),
            out_path=str(shortlist_path),
            top_n=req.shortlist_top_n,
        )

        if p3.shortlist_size == 0:
            raise ValueError(
                "No restaurants matched your filters (empty shortlist). "
                "Try relaxing location, budget, rating, or cuisine constraints."
            )

        try:
            p4 = run_phase4(
                shortlist_path=str(shortlist_path),
                preferences_path=str(prefs_path),
                out_path=str(recs_path),
                report_path=str(report_path),
                top_k=req.top_k,
                temperature=req.temperature,
                max_tokens=req.max_tokens,
            )
        except SystemExit as e:
            msg = str(e) or "Recommendation pipeline failed."
            raise RuntimeError(msg) from e

        with open(recs_path, encoding="utf-8") as f:
            recommendations = json.load(f)

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    return RecommendationResponse(
        recommendations=recommendations,
        metadata=RecommendationMetadata(
            processing_time_ms=round(elapsed_ms, 2),
            model=p4.model,
            top_k=req.top_k,
            shortlist_size=p3.shortlist_size,
            candidates_after_filtering=p3.candidates_after_filtering,
        ),
    )


def restaurants_browse(
    *,
    location: str,
    minimum_rating: float | None,
    budget_min: float | None,
    budget_max: float | None,
    limit: int,
) -> list[dict]:
    dataset = default_dataset_path()
    if not dataset.is_file():
        raise FileNotFoundError(f"Processed dataset not found: {dataset}")

    budget = None
    if budget_min is not None or budget_max is not None:
        budget = BudgetRange(min=budget_min, max=budget_max)

    prefs = UserPreferences(
        location=location.strip(),
        budget=budget,
        cuisines=[],
        minimum_rating=minimum_rating,
        additional_preferences=None,
    )
    df = load_processed_dataset(str(dataset))
    from zomato_rec.phase3.retrieve import filter_candidates, score_candidates

    filtered = filter_candidates(df, prefs)
    scored = score_candidates(filtered, prefs)
    out = scored.head(limit)
    records = out.drop(columns=[c for c in out.columns if c.startswith("__")], errors="ignore").to_dict(
        orient="records"
    )
    return records
