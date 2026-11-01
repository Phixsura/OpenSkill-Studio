from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ff_analytics import fleet_ff_analytics
def test_ff():
    r = fleet_ff_analytics([{"enabled": True, "evaluations_24h": 10000, "age_days": 50},
                            {"enabled": True, "evaluations_24h": 5000, "age_days": 5}])
    assert r["total_evals"] == 15000
    assert r["stale"] == 1
    assert not r["cleanup_needed"]
