from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_exec_sum import fleet_exec_summary
def test_elite():
    r = fleet_exec_summary({"uptime_pct": 99.995, "deploys_per_day": 15, "mttr_minutes": 30, "change_failure_rate_pct": 3})
    assert r["dora_grade"] == "Elite"
def test_high():
    r = fleet_exec_summary({"uptime_pct": 99.95, "deploys_per_day": 5})
    assert r["dora_grade"] == "High"
