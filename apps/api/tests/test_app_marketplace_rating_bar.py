from app.services.app_marketplace_rating_bar import build_rating_bars, compute_rating_summary

def test_bars():
    dist = {"5": 50, "4": 30, "3": 10, "2": 5, "1": 5}
    bars = build_rating_bars(distribution=dist)
    assert bars[0]["stars"] == 5
    assert bars[0]["pct"] == 50.0
    assert len(bars) == 5

def test_empty():
    bars = build_rating_bars(distribution={})
    assert all(b["count"] == 0 for b in bars)

def test_summary():
    dist = {"5": 50, "4": 30, "3": 10, "2": 5, "1": 5}
    s = compute_rating_summary(distribution=dist)
    assert s["avg"] > 4.0
    assert s["recommendation_pct"] == 80.0

def test_summary_empty():
    s = compute_rating_summary(distribution={})
    assert s["avg"] == 0
    assert s["total"] == 0
