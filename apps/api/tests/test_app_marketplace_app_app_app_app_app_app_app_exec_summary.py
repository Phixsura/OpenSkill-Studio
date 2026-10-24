from app.services.app_marketplace_app_app_app_app_app_app_app_exec_summary import generate_executive_summary

def test_summary():
    r = generate_executive_summary({"revenue": 100000, "total_apps": 500, "total_users": 25000,
                                      "uptime_pct": 99.95, "nps": 45, "incidents_month": 3})
    assert r["health"] == "strong"
    assert len(r["kpis"]) == 6
    assert "500" in r["summary"]
