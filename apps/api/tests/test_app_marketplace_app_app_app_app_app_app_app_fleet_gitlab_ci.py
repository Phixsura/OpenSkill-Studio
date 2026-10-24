from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gitlab_ci import fleet_gitlab_ci
def test_gl():
    r = fleet_gitlab_ci([{"status": "success", "duration_min": 12}, {"status": "failed"}])
    assert r["success"] == 1
    assert not r["reliable"]
