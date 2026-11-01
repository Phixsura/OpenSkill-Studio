from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_qwik import fleet_qwik_status
def test_qwik():
    r = fleet_qwik_status([{"deployed": True, "routes": 80, "ttfb_ms": 50}])
    assert r["routes"] == 80
    assert r["instant"]
