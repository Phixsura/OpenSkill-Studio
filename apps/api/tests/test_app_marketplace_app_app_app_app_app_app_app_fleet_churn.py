from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_churn import fleet_churn_rate
def test_churn():
    r = fleet_churn_rate({"start_users": 100, "end_users": 110, "new_users": 20})
    assert r["churned"] == 10
    assert r["churn_rate_pct"] == 10.0
    assert not r["healthy"]
