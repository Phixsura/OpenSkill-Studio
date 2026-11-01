from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_inc_learn import fleet_incident_learning
def test_learn():
    r = fleet_incident_learning([{"implemented": True}, {"implemented": True}, {"implemented": False}])
    assert r["implemented"] == 2
    assert r["learning_rate"] == 66.7
