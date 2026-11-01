from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pod_restart import fleet_pod_restarts
def test_restarts():
    r = fleet_pod_restarts([{"restarts": 0}, {"restarts": 7}, {"restarts": 2}])
    assert r["total_restarts"] == 9
    assert r["crashlooping"] == 1
    assert not r["stable"]
