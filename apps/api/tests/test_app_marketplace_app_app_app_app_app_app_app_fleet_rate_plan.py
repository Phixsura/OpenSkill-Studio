from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_rate_plan import fleet_rate_plan
def test_plan():
    r = fleet_rate_plan([{"tier": "free"}, {"tier": "pro"}, {"tier": "pro"}, {"tier": "enterprise"}])
    assert r["by_tier"]["pro"] == 2
    assert r["tiers"] == 3
