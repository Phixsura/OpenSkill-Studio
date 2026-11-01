from app.services.app_marketplace_app_app_app_app_app_app_app_resp_time_sla import check_response_time_sla, response_time_trend

def test_sla():
    r = check_response_time_sla([
        {"path": "/users", "p99_ms": 200, "target_ms": 500},
        {"path": "/orders", "p99_ms": 600, "target_ms": 500},
    ])
    assert r["met"] == 1
    assert r["breached"] == 1
    assert r["sla_pct"] == 50

def test_trend():
    r = response_time_trend([100, 120, 90, 85])
    assert r["improving"]
    assert r["delta"] == -15.0
