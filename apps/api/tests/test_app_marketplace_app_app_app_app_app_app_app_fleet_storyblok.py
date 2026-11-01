from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_storyblok import fleet_storyblok_status
def test_sb():
    r = fleet_storyblok_status([{"active": True, "stories": 5000, "components": 100}])
    assert r["stories"] == 5000
    assert r["all_active"]
