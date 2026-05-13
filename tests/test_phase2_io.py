from __future__ import annotations

from pathlib import Path

from zomato_rec.phase2.io import load_preferences, save_preferences
from zomato_rec.phase2.models import BudgetRange, UserPreferences


def test_save_and_load_preferences(tmp_path: Path) -> None:
    prefs = UserPreferences(
        location="Bangalore",
        budget=BudgetRange(min=500, max=800),
        cuisines=["Italian"],
        minimum_rating=4.0,
        additional_preferences="family-friendly",
    )

    out = tmp_path / "prefs.json"
    save_preferences(prefs, str(out))

    loaded = load_preferences(str(out))
    assert loaded == prefs

