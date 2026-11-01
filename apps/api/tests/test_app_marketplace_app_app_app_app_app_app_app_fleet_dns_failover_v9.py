from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dns_failover_v9 import fleet_dns_failover_v9
def test_df_v9():
    r = fleet_dns_failover_v9([{"role": "primary", "health_check_passing": True}])
    assert r["primary"] == 1
    assert r["healthy"]
