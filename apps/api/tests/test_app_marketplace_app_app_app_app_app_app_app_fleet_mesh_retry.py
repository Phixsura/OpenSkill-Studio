from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_mesh_retry import fleet_mesh_retry
def test_retry():
    r = fleet_mesh_retry([{"requests": 1000, "retries": 50}, {"requests": 2000, "retries": 300}])
    assert r["retries"] == 350
    assert r["retry_rate_pct"] == 11.67
    assert r["excessive"]
