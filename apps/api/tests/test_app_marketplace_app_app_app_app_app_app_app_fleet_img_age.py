from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_img_age import fleet_image_age
def test_age():
    r = fleet_image_age([{"age_days": 5}, {"age_days": 45}, {"age_days": 120}])
    assert r["old"] == 2
    assert r["ancient"] == 1
    assert r["needs_update"]
