from app.services.app_marketplace_app_app_app_app_app_app_app_signal_agg import aggregate_signals

def test_healthy():
    r = aggregate_signals([
        {"source": "metrics", "health_pct": 99},
        {"source": "logs", "health_pct": 100},
        {"source": "traces", "health_pct": 98},
    ])
    assert r["status"] == "healthy"
    assert r["composite_score"] > 95

def test_degraded():
    r = aggregate_signals([
        {"source": "metrics", "health_pct": 60},
        {"source": "logs", "health_pct": 100},
        {"source": "traces", "health_pct": 50},
    ])
    assert r["status"] == "degraded"
