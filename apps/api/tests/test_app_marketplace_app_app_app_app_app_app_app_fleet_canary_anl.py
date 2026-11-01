from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_canary_anl import fleet_canary_analysis
def test_promote():
    r = fleet_canary_analysis({"error_rate_delta_pct": 0.5, "latency_delta_pct": 2})
    assert r["verdict"] == "promote"
def test_rollback():
    r = fleet_canary_analysis({"error_rate_delta_pct": 5, "latency_delta_pct": 10})
    assert r["verdict"] == "rollback"
