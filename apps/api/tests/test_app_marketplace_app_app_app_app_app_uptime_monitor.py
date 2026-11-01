from app.services.app_marketplace_app_app_app_app_app_uptime_monitor import build_uptime_monitor

def test_uptime():
    days = [{"date": f"2026-10-{i:02d}", "status": "up"} for i in range(1, 31)]
    days[15] = {"date": "2026-10-16", "status": "degraded"}
    r = build_uptime_monitor(daily_status=days, service_name="API Gateway")
    assert r["service_name"] == "API Gateway"
    assert r["total_days"] == 30
    assert r["up_days"] == 29
    assert r["uptime_pct"] == 96.67
