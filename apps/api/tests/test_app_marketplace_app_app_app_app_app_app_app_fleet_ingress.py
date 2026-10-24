from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ingress import fleet_ingress_traffic
def test_ingress():
    r = fleet_ingress_traffic([{"rps": 500, "error_rate_pct": 1}, {"rps": 300, "error_rate_pct": 8}])
    assert r["total_rps"] == 800
    assert r["error_routes"] == 1
    assert not r["healthy"]
