from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ep_health import fleet_endpoint_health
def test_ep():
    r = fleet_endpoint_health([{"status": "up"}, {"status": "up"}, {"status": "degraded"}, {"status": "down"}])
    assert r["up"] == 2
    assert r["availability_pct"] == 50.0
