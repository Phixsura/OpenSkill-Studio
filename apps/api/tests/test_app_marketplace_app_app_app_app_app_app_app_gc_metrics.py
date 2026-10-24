from app.services.app_marketplace_app_app_app_app_app_app_app_gc_metrics import analyze_gc, suggest_tuning

def test_analyze():
    r = analyze_gc([
        {"generation": "young", "pause_ms": 5},
        {"generation": "young", "pause_ms": 8},
        {"generation": "full", "pause_ms": 250},
    ])
    assert r["total"] == 3
    assert r["max_pause_ms"] == 250
    assert r["by_generation"]["young"] == 2

def test_suggest():
    metrics = {"gc_pressure": "high", "max_pause_ms": 500, "by_generation": {"full": 15}}
    s = suggest_tuning(metrics)
    assert len(s) == 3
    assert any(a["action"] == "increase_heap" for a in s)
