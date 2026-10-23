from app.services.app_marketplace_app_feature_gate import evaluate_gate, check_feature_access

def test_plan_allowed():
    r = evaluate_gate(gate={"type": "plan", "plans": ["pro", "enterprise"]},
                      context={"plan": "pro"})
    assert r["allowed"]

def test_plan_blocked():
    r = evaluate_gate(gate={"type": "plan", "plans": ["pro"]}, context={"plan": "free"})
    assert not r["allowed"]

def test_role():
    r = evaluate_gate(gate={"type": "role", "roles": ["admin", "owner"]},
                      context={"role": "admin"})
    assert r["allowed"]

def test_feature_access():
    gates = [{"type": "plan", "plans": ["pro", "enterprise"]},
             {"type": "role", "roles": ["admin"]}]
    r = check_feature_access(feature="advanced_analytics", gates=gates,
                              context={"plan": "pro", "role": "admin"})
    assert r["allowed"]

def test_feature_blocked():
    gates = [{"type": "plan", "plans": ["enterprise"]}]
    r = check_feature_access(feature="sso", gates=gates, context={"plan": "free"})
    assert not r["allowed"]
    assert r["blocked_by"] == "plan"
