from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_nomad import fleet_nomad_status
def test_nomad():
    r = fleet_nomad_status([{"status": "running"}, {"status": "running"}, {"status": "dead"}])
    assert r["running"] == 2
    assert r["dead"] == 1
    assert not r["healthy"]
