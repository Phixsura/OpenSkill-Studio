from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_astro import fleet_astro_status
def test_astro():
    r = fleet_astro_status([{"deployed": True, "pages": 500, "islands": 50}])
    assert r["pages"] == 500
    assert r["all_deployed"]
