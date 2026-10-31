from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_design_review_v9 import fleet_api_design_review_v9
def test_adr2_v9():
    r = fleet_api_design_review_v9([{"approved": True, "changes_requested": False, "review_days": 2}])
    assert r["approved"] == 1
    assert r["healthy"]
