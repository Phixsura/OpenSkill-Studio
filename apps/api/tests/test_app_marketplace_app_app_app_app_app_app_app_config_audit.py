from app.services.app_marketplace_app_app_app_app_app_app_app_config_audit import audit_config

def test_audit():
    r = audit_config("api", {
        "timeout_configured": True, "retries_configured": True, "circuit_breaker": True,
        "health_check": True, "logging_structured": True, "metrics_enabled": True,
        "tracing_enabled": False,
    })
    assert r["score"] == 6
    assert r["compliance_pct"] == 86
    assert r["grade"] == "B"
    assert len(r["findings"]) == 1
    assert r["findings"][0]["practice"] == "tracing_enabled"
