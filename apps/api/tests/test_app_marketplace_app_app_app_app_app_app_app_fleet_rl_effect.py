from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_rl_effect import fleet_rl_effectiveness
def test_rl():
    r = fleet_rl_effectiveness({"total_requests": 100000, "blocked": 1000, "false_positives": 10})
    assert r["precision_pct"] == 99.0
    assert r["effective"]
