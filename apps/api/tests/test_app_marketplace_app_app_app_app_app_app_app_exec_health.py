from app.services.app_marketplace_app_app_app_app_app_app_app_exec_health import generate_exec_report

def test_report():
    r = generate_exec_report({"uptime_pct": 99.95, "revenue": 100000, "users": 5000,
                                 "deploys_week": 15, "incidents_month": 2, "mttr_min": 15})
    assert r["grade"] in ("A", "B")
    assert r["score"] > 80
    assert r["kpis"]["uptime"] == "99.95%"
    assert "$100,000" in r["kpis"]["revenue"]
