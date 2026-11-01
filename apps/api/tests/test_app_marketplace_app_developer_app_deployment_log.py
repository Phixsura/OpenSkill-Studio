from app.services.app_marketplace_app_developer_app_deployment_log import log_deployment, get_deployment_history, compute_deployment_frequency

def test_log():
    l = log_deployment(app_id="a1", version="2.0", environment="production", deployed_by="u1")
    assert l["status"] == "success"

def test_history():
    logs = [{"environment": "production", "timestamp": "2026-01-01"},
            {"environment": "staging", "timestamp": "2026-01-02"},
            {"environment": "production", "timestamp": "2026-01-03"}]
    r = get_deployment_history(logs=logs, environment="production")
    assert len(r) == 2
    assert r[0]["timestamp"] > r[1]["timestamp"]

def test_frequency():
    logs = [{"status": "success"}] * 25 + [{"status": "failed"}] * 5
    r = compute_deployment_frequency(logs=logs)
    assert r["frequency"] == "daily"
    assert r["success_rate"] > 80
