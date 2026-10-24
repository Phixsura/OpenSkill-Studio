from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_beam import fleet_beam_status
def test_beam():
    r = fleet_beam_status([{"state": "RUNNING"}, {"state": "DRAINED"}, {"state": "RUNNING"}])
    assert r["running"] == 2
    assert r["healthy"]
