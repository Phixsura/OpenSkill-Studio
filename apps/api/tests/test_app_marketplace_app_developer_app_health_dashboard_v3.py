from app.services.app_marketplace_app_developer_app_health_dashboard_v3 import build_health_dashboard_v3, compute_error_budget_v2

def test_healthy():
    d = build_health_dashboard_v3(app={"id": "a1", "name": "App"}, slis=[{"metric": "latency"}],
                                    slos=[{"target": 99.9, "current": 99.95}], incidents=[], uptime_history=[])
    assert d["health"] == "healthy"
    assert len(d["panels"]) == 5

def test_warning():
    d = build_health_dashboard_v3(app={"id": "a1", "name": "App"}, slis=[],
                                    slos=[{"target": 99.9, "current": 99.0}], incidents=[], uptime_history=[])
    assert d["health"] == "warning"

def test_critical():
    d = build_health_dashboard_v3(app={"id": "a1", "name": "App"}, slis=[], slos=[],
                                    incidents=[{"status": "investigating"}], uptime_history=[])
    assert d["health"] == "critical"

def test_error_budget():
    r = compute_error_budget_v2(slo_target=99.9, actual=99.95, period_requests=100000)
    assert r["remaining"] > 0
    assert not r["exhausted"]
