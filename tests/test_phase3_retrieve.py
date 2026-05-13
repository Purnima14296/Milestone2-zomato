from __future__ import annotations

import pandas as pd

from zomato_rec.phase2.models import BudgetRange, UserPreferences
from zomato_rec.phase3.retrieve import build_shortlist, filter_candidates


def _df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "restaurant_name": "A",
                "city": "BTM",
                "cuisines": ["Italian"],
                "cost_estimate": 600.0,
                "rating": 4.5,
                "raw": {},
            },
            {
                "restaurant_name": "B",
                "city": "BTM",
                "cuisines": ["Chinese"],
                "cost_estimate": 1200.0,
                "rating": 4.7,
                "raw": {},
            },
            {
                "restaurant_name": "C",
                "city": "Indiranagar",
                "cuisines": ["Italian", "Chinese"],
                "cost_estimate": 700.0,
                "rating": 4.2,
                "raw": {},
            },
        ]
    )


def test_filter_candidates_location_rating_budget_cuisine() -> None:
    prefs = UserPreferences(
        location="BTM",
        budget=BudgetRange(min=500, max=800),
        cuisines=["Italian"],
        minimum_rating=4.0,
        additional_preferences=None,
    )

    filtered = filter_candidates(_df(), prefs)
    assert filtered["restaurant_name"].tolist() == ["A"]


def test_build_shortlist_top_n() -> None:
    prefs = UserPreferences(location="BTM", cuisines=[], budget=None, minimum_rating=None, additional_preferences=None)
    shortlist = build_shortlist(_df(), prefs, top_n=1)
    assert len(shortlist) == 1

