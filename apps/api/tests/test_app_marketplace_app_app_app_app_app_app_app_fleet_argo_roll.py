from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_argo_roll import fleet_argo_rollouts
def test_roll():
    r = fleet_argo_rollouts([{"phase": "Healthy"}, {"phase": "Paused"}, {"phase": "Degraded"}])
    assert r["healthy"] == 1
    assert r["paused"] == 1
    assert not r["all_healthy"]
