from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sla_report import fleet_sla_report
def test_met():
    r = fleet_sla_report({"uptime_pct": 99.95, "target_pct": 99.9, "month": "Oct"})
    assert r["met"]
    assert r["credits_usd"] == 0
def test_missed():
    r = fleet_sla_report({"uptime_pct": 99.5, "target_pct": 99.9, "month": "Sep"})
    assert not r["met"]
    assert r["credits_usd"] == 400.0
