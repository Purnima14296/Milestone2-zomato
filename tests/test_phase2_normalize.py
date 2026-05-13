from zomato_rec.phase2.normalize import normalize_location, parse_budget, parse_cuisines, parse_min_rating


def test_normalize_location_aliases() -> None:
    assert normalize_location("Bengaluru") == "Bangalore"
    assert normalize_location("  bangalore ") == "Bangalore"


def test_parse_cuisines_splits_and_dedupes() -> None:
    assert parse_cuisines("Italian, Chinese") == ["Italian", "Chinese"]
    assert parse_cuisines("Italian / Chinese | Italian") == ["Italian", "Chinese"]


def test_parse_min_rating() -> None:
    assert parse_min_rating("4") == 4.0
    assert parse_min_rating("4+") == 4.0
    assert parse_min_rating("bad") is None
    assert parse_min_rating(6) is None


def test_parse_budget_buckets_and_ranges() -> None:
    b = parse_budget("low")
    assert b is not None and b.min == 0 and b.max == 400

    b = parse_budget("500-800")
    assert b is not None and b.min == 500 and b.max == 800

    b = parse_budget("800-500")
    assert b is not None and b.min == 500 and b.max == 800

    b = parse_budget("under 400")
    assert b is not None and b.min == 0 and b.max == 400

    b = parse_budget("any")
    assert b is None

