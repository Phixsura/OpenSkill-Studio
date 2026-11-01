from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_azure_func import fleet_azure_func_status
def test_af():
    r = fleet_azure_func_status([{"status": "Running", "executions_24h": 3000000, "gb_seconds": 50000}])
    assert r["executions_24h"] == 3000000
    assert r["all_running"]
