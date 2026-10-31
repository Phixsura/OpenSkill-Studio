from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_roadmap import fleet_roadmap_progress
def test_roadmap():
    r = fleet_roadmap_progress([{"status": "done"}, {"status": "done"}, {"status": "in_progress"}, {"status": "planned"}])
    assert r["done"] == 2
    assert r["completion_pct"] == 50.0
