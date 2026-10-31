from app.services.app_marketplace_app_app_app_app_app_app_app_flow_profile import profile_flow

def test_profile():
    r = profile_flow([
        {"service": "gateway", "start_ms": 0, "duration_ms": 5},
        {"service": "api", "start_ms": 10, "duration_ms": 50},
        {"service": "db", "start_ms": 65, "duration_ms": 20},
    ])
    assert r["total_ms"] == 75
    assert r["bottleneck"] == "api"
    assert r["spans"] == 3
    assert r["overhead_ms"] == 10  # gap between gateway end(5) and api start(10) + api end(60) and db start(65)
