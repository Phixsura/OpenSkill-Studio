from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_render import fleet_render_status
def test_render():
    r = fleet_render_status([{"status": "running"}, {"status": "running"}, {"suspended": True, "status": "suspended"}])
    assert r["running"] == 2
    assert r["suspended"] == 1
    assert not r["healthy"]
