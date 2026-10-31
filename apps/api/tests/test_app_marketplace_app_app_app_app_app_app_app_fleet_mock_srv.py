from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_mock_srv import fleet_mock_server
def test_mock():
    r = fleet_mock_server([{"active": True, "hits_24h": 5000}, {"active": False, "hits_24h": 0}])
    assert r["active"] == 1
    assert r["hits_24h"] == 5000
    assert r["well_used"]
