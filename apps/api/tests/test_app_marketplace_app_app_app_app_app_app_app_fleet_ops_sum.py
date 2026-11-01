from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ops_sum import fleet_ops_summary
def test_calm():
    r = fleet_ops_summary({"incidents_open": 0, "deploys_today": 5, "alerts_firing": 0})
    assert r["status"] == "calm"
def test_storm():
    r = fleet_ops_summary({"incidents_open": 5, "deploys_today": 0, "alerts_firing": 10})
    assert r["status"] == "storm"
