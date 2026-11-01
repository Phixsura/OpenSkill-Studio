from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_strapi import fleet_strapi_status
def test_strapi():
    r = fleet_strapi_status([{"running": True, "content_types": 25, "entries": 50000}])
    assert r["content_types"] == 25
    assert r["all_running"]
