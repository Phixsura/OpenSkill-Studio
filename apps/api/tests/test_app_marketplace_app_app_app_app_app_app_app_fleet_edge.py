from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_edge import fleet_edge_computing
def test_edge():
    r = fleet_edge_computing([{"status": "online", "rps": 5000}, {"status": "offline", "rps": 0}])
    assert r["online"] == 1
    assert r["offline"] == 1
    assert not r["all_online"]
