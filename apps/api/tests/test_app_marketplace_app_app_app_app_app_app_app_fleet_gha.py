from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gha import fleet_gha_status
def test_gha():
    r = fleet_gha_status([{"conclusion": "success", "billable_min": 5}] * 9 + [{"conclusion": "failure", "billable_min": 3}])
    assert r["success_rate"] == 90.0
    assert r["billable_minutes"] == 48
