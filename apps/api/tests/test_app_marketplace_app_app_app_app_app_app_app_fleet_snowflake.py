from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_snowflake import fleet_snowflake_status
def test_sf():
    r = fleet_snowflake_status([{"state": "STARTED", "credits_24h": 50, "queries_24h": 10000}])
    assert r["credits_24h"] == 50
    assert r["cost_controlled"]
