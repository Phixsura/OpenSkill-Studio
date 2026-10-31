from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_slsa import fleet_slsa_status
def test_slsa():
    r = fleet_slsa_status([{"slsa_level": 3}, {"slsa_level": 2}, {"slsa_level": 1}])
    assert r["avg_level"] == 2.0
    assert r["mature"]
