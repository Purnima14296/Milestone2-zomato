from __future__ import annotations

import json

import pytest

from zomato_rec.phase4.parsing import LLMOutputError, validate_and_normalize_recommendations


def test_validate_recommendations_accepts_only_allowed_names() -> None:
    allowed = {"A", "B"}
    llm = {
        "recommendations": [
            {"rank": 1, "restaurant_name": "A", "reason": "Matches budget."},
            {"rank": 2, "restaurant_name": "HALLUCINATION", "reason": "Best."},
            {"rank": 3, "restaurant_name": "B", "reason": "Good rating."},
        ]
    }
    recs = validate_and_normalize_recommendations(json.dumps(llm), allowed_names=allowed, top_k=5)
    assert [r["restaurant_name"] for r in recs] == ["A", "B"]
    assert [r["rank"] for r in recs] == [1, 2]


def test_validate_recommendations_raises_when_empty_after_validation() -> None:
    allowed = {"A"}
    llm = {"recommendations": [{"rank": 1, "restaurant_name": "X", "reason": "Nope"}]}
    with pytest.raises(LLMOutputError):
        validate_and_normalize_recommendations(json.dumps(llm), allowed_names=allowed, top_k=3)


def test_validate_recommendations_extracts_json_from_wrapped_text() -> None:
    allowed = {"A"}
    wrapped = "Here you go:\n" + json.dumps({"recommendations": [{"restaurant_name": "A", "reason": "Ok"}]}) + "\nThanks"
    recs = validate_and_normalize_recommendations(wrapped, allowed_names=allowed, top_k=1)
    assert recs[0]["restaurant_name"] == "A"

