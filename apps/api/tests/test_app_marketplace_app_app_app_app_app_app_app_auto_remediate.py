from app.services.app_marketplace_app_app_app_app_app_app_app_auto_remediate import evaluate_remediation, remediation_stats

def test_remediate():
    r = evaluate_remediation("high_cpu", "warning")
    assert r["can_remediate"]
    assert r["action"] == "scale_up"
    assert r["auto_approve"]

def test_critical():
    r = evaluate_remediation("high_error_rate", "critical")
    assert r["can_remediate"]
    assert not r["auto_approve"]

def test_unknown():
    r = evaluate_remediation("unknown_issue", "warning")
    assert not r["can_remediate"]

def test_stats():
    actions = [{"action": "scale_up", "auto_approve": True},
               {"action": "rollback", "auto_approve": False}]
    r = remediation_stats(actions)
    assert r["auto_pct"] == 50
