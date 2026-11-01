from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_code_review_v9 import fleet_code_review_v9
def test_cr2_v9():
    r = fleet_code_review_v9([{"status": "approved", "review_hours": 2}])
    assert r["approved"] == 1
    assert r["avg_review_hours"] == 2.0
    assert r["healthy"]
