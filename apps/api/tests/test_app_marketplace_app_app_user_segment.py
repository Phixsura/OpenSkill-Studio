from app.services.app_marketplace_app_app_user_segment import create_segment, evaluate_segment

def test_create():
    r = create_segment(name="Power Users", rules=[
        {"field": "plan", "operator": "eq", "value": "pro"},
        {"field": "login_count", "operator": "gt", "value": 50},
    ])
    assert r["rule_count"] == 2
    assert r["name"] == "Power Users"

def test_evaluate_match():
    rules = [{"field": "plan", "operator": "eq", "value": "pro"},
             {"field": "login_count", "operator": "gt", "value": 10}]
    r = evaluate_segment(user={"plan": "pro", "login_count": 50}, rules=rules)
    assert r["matches"]
    assert r["match_pct"] == 100

def test_evaluate_no_match():
    rules = [{"field": "plan", "operator": "eq", "value": "enterprise"}]
    r = evaluate_segment(user={"plan": "free"}, rules=rules)
    assert not r["matches"]
