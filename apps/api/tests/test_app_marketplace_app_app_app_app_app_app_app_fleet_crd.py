from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_crd import fleet_crd_status
def test_crd():
    r = fleet_crd_status([{"condition": "Established", "age_days": 30}, {"condition": "NamesAccepted", "age_days": 400}])
    assert r["healthy"] == 1
    assert r["stale"] == 1
    assert not r["all_established"]
