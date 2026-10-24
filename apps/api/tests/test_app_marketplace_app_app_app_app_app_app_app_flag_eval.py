from app.services.app_marketplace_app_app_app_app_app_app_app_flag_eval import evaluate

def test_rule_match():
    rules = [{"name": "beta_users", "attribute": "plan", "operator": "eq", "value": "beta", "result": True}]
    r = evaluate("new_ui", {"id": "u1", "plan": "beta"}, rules)
    assert r["enabled"]
    assert r["reason"] == "rule_match"

def test_no_match():
    rules = [{"attribute": "plan", "operator": "eq", "value": "beta", "result": True}]
    r = evaluate("new_ui", {"id": "u2", "plan": "free"}, rules, default=False)
    assert not r["enabled"]
    assert r["reason"] == "default"

def test_in_operator():
    rules = [{"attribute": "country", "operator": "in", "value": ["US", "CA"], "result": True}]
    assert evaluate("feat", {"id": "u1", "country": "US"}, rules)["enabled"]
    assert not evaluate("feat", {"id": "u2", "country": "BR"}, rules, default=False)["enabled"]
