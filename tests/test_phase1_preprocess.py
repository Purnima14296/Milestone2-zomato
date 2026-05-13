from __future__ import annotations

import pandas as pd

from zomato_rec.phase1.preprocess import build_processed_df


def test_build_processed_df_maps_expected_columns() -> None:
    raw = pd.DataFrame(
        [
            {
                "name": "Test Resto",
                "listed_in(city)": "BTM",
                "cuisines": "Italian, Chinese",
                "approx_cost(for two people)": "₹500 for two",
                "rate": "4.2/5",
                "address": "Some address text",
            }
        ]
    )

    processed, mapping = build_processed_df(raw)
    assert len(processed) == 1
    assert mapping["name"] == "name"
    assert mapping["city"] == "listed_in(city)"
    assert mapping["rating"] == "rate"

    row = processed.iloc[0]
    assert row["restaurant_name"] == "Test Resto"
    assert row["city"] == "BTM"
    assert row["cuisines"] == ["Italian", "Chinese"]
    assert row["cost_estimate"] == 500.0
    assert row["rating"] == 4.2

