from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_plausible import fleet_plausible_status
def test_pl():
    r = fleet_plausible_status([{"active": True, "pageviews_24h": 1000000, "visitors_24h": 200000}])
    assert r["pageviews_24h"] == 1000000
    assert r["all_active"]
