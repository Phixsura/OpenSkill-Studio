from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_polaris import fleet_polaris_score
def test_pol():
    r = fleet_polaris_score([{"passed": True}] * 9 + [{"passed": False, "severity": "danger"}])
    assert r["score"] == 90.0
    assert r["grade"] == "A"
