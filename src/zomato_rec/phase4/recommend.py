from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from typing import Any

from zomato_rec.config import Settings
from zomato_rec.phase2.io import load_preferences
from zomato_rec.phase4.groq_client import GroqChatConfig, groq_chat
from zomato_rec.phase4.parsing import LLMOutputError, validate_and_normalize_recommendations
from zomato_rec.phase4.prompting import build_system_prompt, build_user_prompt


def load_shortlist(path: str) -> list[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("shortlist.json must be a JSON array")
    # keep only fields we need for prompting
    out: list[dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        out.append(
            {
                "restaurant_name": item.get("restaurant_name"),
                "city": item.get("city"),
                "cuisines": item.get("cuisines"),
                "cost_estimate": item.get("cost_estimate"),
                "rating": item.get("rating"),
            }
        )
    return out


def _index_by_name(candidates: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    idx: dict[str, dict[str, Any]] = {}
    for c in candidates:
        name = c.get("restaurant_name")
        if isinstance(name, str) and name and name not in idx:
            idx[name] = c
    return idx


def enrich_with_candidate_fields(
    recs: list[dict[str, Any]], candidates_by_name: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for r in recs:
        name = r["restaurant_name"]
        cand = candidates_by_name.get(name, {})
        out.append(
            {
                **r,
                "city": cand.get("city"),
                "cuisines": cand.get("cuisines"),
                "rating": cand.get("rating"),
                "cost_estimate": cand.get("cost_estimate"),
            }
        )
    return out


@dataclass(frozen=True)
class Phase4Report:
    shortlist_path: str
    preferences_path: str
    model: str
    top_k: int
    output_path: str
    report_path: str


def run_phase4(
    *,
    shortlist_path: str = os.path.join("storage", "shortlist.json"),
    preferences_path: str = os.path.join("storage", "preferences.json"),
    out_path: str = os.path.join("storage", "recommendations.json"),
    report_path: str = os.path.join("storage", "phase4_report.json"),
    top_k: int = 5,
    temperature: float = 0.2,
    max_tokens: int = 900,
) -> Phase4Report:
    settings = Settings()
    if not settings.groq_api_key:
        raise SystemExit("Missing GROQ_API_KEY. Set it in your `.env` file.")

    prefs = load_preferences(preferences_path)
    candidates = load_shortlist(shortlist_path)
    if not candidates:
        raise SystemExit("The Phase 3 shortlist is empty! Phase 4 requires at least one candidate to recommend.")

    allowed_names = {c["restaurant_name"] for c in candidates if isinstance(c.get("restaurant_name"), str)}

    system = build_system_prompt()
    user = build_user_prompt(prefs, candidates, top_k=top_k)

    llm_text = groq_chat(
        api_key=settings.groq_api_key,
        cfg=GroqChatConfig(model=settings.groq_model, temperature=temperature, max_tokens=max_tokens),
        system=system,
        user=user,
    )

    try:
        recs = validate_and_normalize_recommendations(llm_text, allowed_names=allowed_names, top_k=top_k)
    except LLMOutputError as e:
        raise SystemExit(f"Groq output validation failed: {e}") from e

    candidates_by_name = _index_by_name(candidates)
    recs = enrich_with_candidate_fields(recs, candidates_by_name)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(recs, f, indent=2, ensure_ascii=False)

    rep = Phase4Report(
        shortlist_path=shortlist_path,
        preferences_path=preferences_path,
        model=settings.groq_model,
        top_k=top_k,
        output_path=out_path,
        report_path=report_path,
    )
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(asdict(rep), f, indent=2, ensure_ascii=False)

    return rep

