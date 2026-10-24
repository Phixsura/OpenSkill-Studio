from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_code_review import fleet_code_review
def test_review():
    r = fleet_code_review([{"reviewed": True, "review_hours": 4}, {"reviewed": True, "review_hours": 8}, {"reviewed": False}])
    assert r["reviewed"] == 2
    assert r["avg_review_hours"] == 6.0
    assert r["fast"]
