from app.services.app_marketplace_app_app_app_app_app_app_app_readiness_dash import readiness_dashboard

def test_dashboard():
    r = readiness_dashboard([
        {"name": "api", "health_check": True, "monitoring": True, "logging": True,
         "alerting": True, "runbooks": True, "load_tested": True},
        {"name": "worker", "health_check": True, "monitoring": True, "logging": True,
         "alerting": False, "runbooks": False, "load_tested": False},
    ])
    assert r["ready"] == 1
    assert r["not_ready"] == 1
    assert r["readiness_pct"] == 50.0
    assert r["services"][0]["ready"]
    assert not r["services"][1]["ready"]
