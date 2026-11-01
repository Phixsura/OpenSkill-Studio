from app.services.app_marketplace_complete_debug_console import build_complete_debug_console

def test_healthy():
    d = build_complete_debug_console(
        app={"id": "a1", "name": "App"}, logs=[{"level": "info"}], requests=[{"status_code": 200}],
        sandbox_status={"running": True}, feature_flags=[{"key": "x"}], cache_stats={"entries": 5})
    assert d["health"] == "healthy"
    assert len(d["panels"]) == 5

def test_degraded():
    d = build_complete_debug_console(
        app={"id": "a1", "name": "App"}, logs=[{"level": "error", "message": "fail"}],
        requests=[{"status_code": 500}], sandbox_status={}, feature_flags=[], cache_stats={})
    assert d["health"] == "degraded"
