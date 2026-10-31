from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_health_agg import fleet_ai_health_aggregator
def test_ha():
    r = fleet_ai_health_aggregator([{"active": True, "services": 500, "healthy": 498, "degraded": 2, "down": 0}])
    assert r["health_pct"] == 99.6
    assert r["green"]
