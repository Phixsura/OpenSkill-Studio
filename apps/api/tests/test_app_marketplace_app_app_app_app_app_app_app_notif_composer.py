from app.services.app_marketplace_app_app_app_app_app_app_app_notif_composer import compose_notification

def test_compose():
    r = compose_notification("deploy_complete", data={"message": "v2.1 deployed successfully", "url": "/deploys/123"})
    assert r["title"] == "Deploy Complete"
    assert r["icon"] == "🚀"
    assert r["priority"] == "high"
    assert "slack" in r["channels"]
    assert r["body"] == "v2.1 deployed successfully"

def test_critical():
    r = compose_notification("error_spike", data={"message": "500 errors up 200%"})
    assert r["priority"] == "critical"
    assert "sms" in r["channels"]
    assert len(r["channels"]) == 4
