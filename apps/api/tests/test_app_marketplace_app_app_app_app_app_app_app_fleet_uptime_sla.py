from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_uptime_sla import fleet_uptime_sla
def test_sla():
    r = fleet_uptime_sla({"total_minutes": 43200, "downtime_minutes": 5})
    assert r["uptime_pct"] == 99.9884
    assert r["meets_sla"]
