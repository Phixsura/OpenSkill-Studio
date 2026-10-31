from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_mkt_analytics import fleet_mkt_analytics
def test_mkt():
    r = fleet_mkt_analytics({"total_listings": 500, "total_installs": 25000, "avg_rating": 4.5})
    assert r["install_rate"] == 50.0
    assert r["healthy"]
