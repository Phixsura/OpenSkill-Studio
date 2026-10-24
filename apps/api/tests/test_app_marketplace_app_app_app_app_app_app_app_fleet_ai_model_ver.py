from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_ver import fleet_ai_model_versioning
def test_mv():
    r = fleet_ai_model_versioning([{"models": 100, "versions": 1000, "active_versions": 200}])
    assert r["versions"] == 1000
    assert r["well_managed"]
