from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_mesh_timeout import fleet_mesh_timeout
def test_timeout():
    r = fleet_mesh_timeout([{"requests": 5000, "timeouts": 100}, {"requests": 5000, "timeouts": 50}])
    assert r["timeouts"] == 150
    assert r["timeout_rate_pct"] == 1.5
    assert r["problematic"]
