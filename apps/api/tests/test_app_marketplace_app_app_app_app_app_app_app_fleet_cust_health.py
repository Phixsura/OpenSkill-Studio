from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cust_health import fleet_customer_health
def test_health():
    r = fleet_customer_health([{"health_score": 90}, {"health_score": 50}, {"health_score": 20}])
    assert r["healthy"] == 1
    assert r["at_risk"] == 1
    assert r["churning"] == 1
