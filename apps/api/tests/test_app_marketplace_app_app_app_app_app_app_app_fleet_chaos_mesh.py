from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_chaos_mesh import fleet_chaos_mesh
def test_cm():
    r = fleet_chaos_mesh([{"status": "running"}, {"status": "completed"}, {"status": "paused"}])
    assert r["running"] == 1
    assert r["active"]
