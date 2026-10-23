from app.services.app_marketplace_app_developer_integration_health import check_integration_health

def test_all_healthy():
    r = check_integration_health(integrations=[
        {"name": "Slack", "last_ping_ms": 100, "error_count": 0},
        {"name": "GitHub", "last_ping_ms": 200, "error_count": 1}])
    assert r["overall"] == "healthy"

def test_degraded():
    r = check_integration_health(integrations=[
        {"name": "Slack", "last_ping_ms": 100, "error_count": 0},
        {"name": "GitHub", "last_ping_ms": 10000, "error_count": 5}])
    assert r["overall"] == "degraded"

def test_down():
    r = check_integration_health(integrations=[
        {"name": "API", "last_ping_ms": 10000, "error_count": 20}])
    assert r["overall"] == "down"
