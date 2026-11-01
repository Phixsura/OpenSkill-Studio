from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dspy import fleet_dspy_status
def test_dspy():
    r = fleet_dspy_status([{"deployed": True, "modules": 15, "optimizations_24h": 500}])
    assert r["modules"] == 15
    assert r["all_deployed"]
