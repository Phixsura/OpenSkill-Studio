from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_langchain import fleet_langchain_status
def test_lc():
    r = fleet_langchain_status([{"deployed": True, "chains": 20, "traces_24h": 500000}])
    assert r["chains"] == 20
    assert r["all_deployed"]
