from app.services.app_marketplace_complete_app_debug_page import build_complete_debug_page

def test_healthy():
    p = build_complete_debug_page(app={"id": "a1", "name": "App"}, logs=[{"level": "info"}],
                                    requests=[{"status_code": 200}], errors=[], traces=[], sandbox={"status": "running"})
    assert p["health"] == "healthy"
    assert len(p["panels"]) == 6

def test_critical():
    logs = [{"level": "error"}] * 15
    p = build_complete_debug_page(app={"id": "a1", "name": "App"}, logs=logs, requests=[], errors=[], traces=[], sandbox={})
    assert p["health"] == "critical"
