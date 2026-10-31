from app.services.app_marketplace_app_app_app_app_app_app_app_slack_notify import build_alert_message, build_deploy_message

def test_alert():
    r = build_alert_message(title="High CPU", severity="critical",
                             message="CPU at 95%", service="api")
    assert r["color"] == "#DC2626"
    assert "🚨" in r["text"]
    assert len(r["blocks"]) == 3

def test_deploy():
    r = build_deploy_message(app="myapp", version="2.0", deployer="alice")
    assert r["color"] == "#10B981"
    assert "myapp" in r["text"]
    assert "2.0" in r["text"]
