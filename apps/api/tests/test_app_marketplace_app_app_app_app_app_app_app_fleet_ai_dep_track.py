from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_dep_track import fleet_ai_dependency_tracker
def test_dt():
    r = fleet_ai_dependency_tracker([{"active": True, "dependencies": 500, "outdated": 20, "vulns": 0}])
    assert r["dependencies"] == 500
    assert r["secure"]
