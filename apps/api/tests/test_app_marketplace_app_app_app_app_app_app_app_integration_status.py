from app.services.app_marketplace_app_app_app_app_app_app_app_integration_status import check_integrations

def test_integrations():
    r = check_integrations([
        {"name": "Slack", "provider": "slack", "status": "connected", "last_sync": "5m ago", "icon": "💬"},
        {"name": "GitHub", "provider": "github", "status": "connected", "last_sync": "1m ago", "icon": "🐙"},
        {"name": "Jira", "provider": "jira", "status": "disconnected", "icon": "📋"},
    ])
    assert r["connected"] == 2
    assert r["disconnected"] == 1
    assert r["health"] == "partial"
