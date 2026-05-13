from __future__ import annotations

import os
import sys
from pathlib import Path

# Repo root: src/zomato_rec/web_ui/app.py → parents[3] == repository root (for `backend` imports on Streamlit Cloud).
_REPO_ROOT = Path(__file__).resolve().parents[3]
for _p in (_REPO_ROOT / "src", _REPO_ROOT):
    _s = str(_p)
    if _s not in sys.path:
        sys.path.insert(0, _s)

from dotenv import load_dotenv

load_dotenv(_REPO_ROOT / ".env", override=False)

import streamlit as st

from backend.app.pipeline import default_dataset_path, list_dataset_cities, run_recommendations
from backend.app.schemas import BudgetRangeIn, PreferencesIn, RecommendationRequest


def _inject_streamlit_secrets() -> None:
    """Map Streamlit Cloud / local `.streamlit/secrets.toml` into os.environ for Settings + pipeline."""
    try:
        sec = st.secrets
    except FileNotFoundError:
        return
    for key in ("GROQ_API_KEY", "GROQ_MODEL", "ZOMATO_PROCESSED_DATASET"):
        if key in sec and str(sec[key]).strip():
            os.environ[key] = str(sec[key]).strip()


def _dataset_ok() -> bool:
    return default_dataset_path().is_file()


def _parse_cuisines(raw: str) -> list[str]:
    parts = [p.strip() for p in raw.replace("\n", ",").split(",")]
    return [p for p in parts if p]


def _maybe_handle_parquet_upload(uploaded) -> None:
    if uploaded is None:
        return
    dest_dir = _REPO_ROOT / ".streamlit"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "uploaded_restaurants.parquet"
    dest.write_bytes(uploaded.getvalue())
    os.environ["ZOMATO_PROCESSED_DATASET"] = str(dest)


def main() -> None:
    _inject_streamlit_secrets()

    st.set_page_config(
        page_title="Zomato AI Recommender",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("Restaurant recommendations")
    st.caption(
        "Phase 9 — Streamlit deployment UI. Runs the same in-process pipeline as the Phase 7 API "
        "(preferences → shortlist → Groq → ranked results)."
    )

    from zomato_rec.config import Settings

    settings = Settings()

    with st.sidebar:
        st.subheader("Deployment")
        ds_path = default_dataset_path()
        if _dataset_ok():
            st.success("Dataset OK")
            st.code(str(ds_path), language="text")
        else:
            st.warning("No processed Parquet at the default path. Upload a file below or set `ZOMATO_PROCESSED_DATASET`.")

        if settings.groq_api_key:
            st.success("Groq API key is set (`GROQ_API_KEY`).")
        else:
            st.error("Missing Groq key. Add `GROQ_API_KEY` to `.env` or Streamlit **Secrets**.")

        st.markdown(
            "**Streamlit Community Cloud:** set secrets to match `.streamlit/secrets.toml.example`, "
            "point the main file to `src/zomato_rec/web_ui/app.py`, and use `requirements.txt` at repo root."
        )

    up = st.file_uploader("Upload processed `restaurants.parquet` (optional)", type=["parquet"])
    _maybe_handle_parquet_upload(up)

    cities: list[str] = []
    if _dataset_ok():
        try:
            cities = list_dataset_cities(limit=500)
        except Exception:
            cities = []

    with st.form("preferences"):
        st.subheader("Your preferences")
        c1, c2 = st.columns(2)

        with c1:
            if cities:
                loc_options = [""] + cities

                def _loc_label(v: str) -> str:
                    return "Select location" if v == "" else v

                location = st.selectbox("Location", options=loc_options, format_func=_loc_label)
            else:
                location = st.text_input("Location (city/locality)", placeholder="e.g. Koramangala")

            budget_max = st.slider("Budget max (for two, ₹)", min_value=0, max_value=5000, value=1500, step=100)

            rating_choice = st.selectbox(
                "Minimum rating",
                options=["Any", "3.0+", "3.5+", "4.0+", "4.5+"],
                index=0,
            )
            rating_map = {"Any": None, "3.0+": 3.0, "3.5+": 3.5, "4.0+": 4.0, "4.5+": 4.5}
            min_rating = rating_map[rating_choice]

        with c2:
            cuisines_raw = st.text_input(
                "Cuisines (optional, comma-separated)",
                placeholder="North Indian, Thai",
                autocomplete="off",
            )
            extra = st.text_area("Additional preferences (optional)", placeholder="Date night, outdoor seating…")

        with st.expander("Advanced"):
            top_k = st.number_input("Top K recommendations", min_value=1, max_value=20, value=5, step=1)
            shortlist_n = st.number_input("Shortlist size (Phase 3)", min_value=5, max_value=100, value=30, step=5)

        submitted = st.form_submit_button("Get recommendations", type="primary")

    if not submitted:
        return

    if not (location or "").strip():
        st.error("Please choose or enter a location.")
        return

    if not settings.groq_api_key:
        st.error("Configure `GROQ_API_KEY` before running recommendations.")
        return

    if not _dataset_ok():
        st.error("Processed dataset not found. Run Phase 1, set `ZOMATO_PROCESSED_DATASET`, or upload `restaurants.parquet`.")
        return

    cuisines = _parse_cuisines(cuisines_raw)
    prefs = PreferencesIn(
        location=location.strip(),
        budget=BudgetRangeIn(min=0.0, max=float(budget_max)),
        cuisines=cuisines,
        minimum_rating=min_rating,
        additional_preferences=extra.strip() if extra.strip() else None,
    )
    req = RecommendationRequest(
        preferences=prefs,
        top_k=int(top_k),
        shortlist_top_n=int(shortlist_n),
    )

    with st.spinner("Retrieving candidates and calling the model…"):
        try:
            result = run_recommendations(req)
        except FileNotFoundError as e:
            st.error(str(e))
            return
        except ValueError as e:
            st.warning(str(e))
            return
        except RuntimeError as e:
            st.error(str(e))
            return
        except Exception as e:
            st.exception(e)
            return

    meta = result.metadata
    st.subheader("Results")
    st.caption(
        f"Model `{meta.model}` · {meta.processing_time_ms:.0f} ms · shortlist {meta.shortlist_size} "
        f"(filtered {meta.candidates_after_filtering})"
    )

    for row in result.recommendations:
        name = row.get("restaurant_name", "Restaurant")
        rank = row.get("rank", "")
        with st.container():
            st.markdown(f"#### #{rank} — {name}")
            bits = [
                row.get("city"),
                f"★ {row['rating']}" if row.get("rating") is not None else None,
                f"~₹{row['cost_estimate']}" if row.get("cost_estimate") is not None else None,
            ]
            st.write(" · ".join(str(b) for b in bits if b))
            if row.get("cuisines"):
                cu = row["cuisines"]
                st.caption(", ".join(map(str, cu)) if isinstance(cu, list) else str(cu))
            st.write(row.get("reason", ""))
            st.divider()


if __name__ == "__main__":
    main()
