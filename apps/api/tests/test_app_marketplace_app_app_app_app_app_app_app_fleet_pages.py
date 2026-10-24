from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pages import fleet_pages_status
def test_pages():
    r = fleet_pages_status([{"deployed": True, "builds_24h": 20, "custom_domains": 3}])
    assert r["builds_24h"] == 20
    assert r["all_deployed"]
