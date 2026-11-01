from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_solidstart import fleet_solidstart_status
def test_ss():
    r = fleet_solidstart_status([{"running": True, "routes": 60, "signals": 200}])
    assert r["routes"] == 60
    assert r["reactive"]
