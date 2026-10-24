from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_svc_map import fleet_service_map
def test_map():
    r = fleet_service_map([{"external": False}, {"external": True}], [{"from": "a", "to": "b"}, {"from": "a", "to": "c"}])
    assert r["internal"] == 1
    assert r["external"] == 1
    assert r["avg_connections"] == 1.0
