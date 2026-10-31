from app.services.app_marketplace_app_app_app_app_app_app_app_prio_queue_stats import analyze_queue, queue_health

def test_analyze():
    r = analyze_queue([
        {"priority": "critical", "wait_ms": 10},
        {"priority": "normal", "wait_ms": 100},
        {"priority": "normal", "wait_ms": 200},
        {"priority": "low", "wait_ms": 500},
    ])
    assert r["total_queued"] == 4
    assert r["deepest"] == "normal"

def test_health():
    r = queue_health(800, 1000)
    assert r["status"] == "critical"
    r2 = queue_health(100, 1000)
    assert r2["status"] == "healthy"
