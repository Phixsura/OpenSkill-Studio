from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_health import fleet_api_health_score
def test_health():
    r = fleet_api_health_score({"availability_pct": 99.9, "p99_ms": 200, "error_rate_pct": 1})
    assert r["grade"] == "A"
