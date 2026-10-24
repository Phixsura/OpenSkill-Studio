from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_nuxt import fleet_nuxt_status
def test_nuxt():
    r = fleet_nuxt_status([{"deployed": True, "pages": 100, "preset": "node"}])
    assert r["pages"] == 100
    assert r["all_deployed"]
