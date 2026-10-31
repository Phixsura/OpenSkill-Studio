from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_jenkins import fleet_jenkins_status
def test_jenkins():
    r = fleet_jenkins_status([{"online": True, "agents": 20, "queue_size": 10}])
    assert r["agents"] == 20
    assert r["healthy"]
