from app.services.app_marketplace_app_user_segment import create_segment, evaluate_user, segment_users

def test_create():
    s = create_segment(name="power_users", rules=[{"field": "plan", "operator": "eq", "value": "pro"}])
    assert s["status"] == "active"

def test_evaluate_match():
    assert evaluate_user(user={"plan": "pro", "installs": 50},
                          rules=[{"field": "plan", "operator": "eq", "value": "pro"}])

def test_evaluate_no_match():
    assert not evaluate_user(user={"plan": "free"},
                              rules=[{"field": "plan", "operator": "eq", "value": "pro"}])

def test_evaluate_gt():
    assert evaluate_user(user={"installs": 100}, rules=[{"field": "installs", "operator": "gt", "value": 50}])
    assert not evaluate_user(user={"installs": 10}, rules=[{"field": "installs", "operator": "gt", "value": 50}])

def test_segment():
    users = [{"plan": "pro"}, {"plan": "free"}, {"plan": "pro"}]
    r = segment_users(users=users, rules=[{"field": "plan", "operator": "eq", "value": "pro"}])
    assert r["matched"] == 2
    assert r["match_rate"] > 60
