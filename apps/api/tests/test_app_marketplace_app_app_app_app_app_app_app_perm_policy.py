from app.services.app_marketplace_app_app_app_app_app_app_app_perm_policy import evaluate_policy, list_permissions

def test_allow():
    r = evaluate_policy(
        {"role": "admin", "department": "eng"},
        {"type": "document"},
        "delete",
        [{"name": "admin_all", "actions": ["read", "write", "delete"], "effect": "allow",
          "conditions": [{"attribute": "role", "operator": "eq", "value": "admin"}]}])
    assert r["allowed"]
    assert r["policy"] == "admin_all"

def test_deny():
    r = evaluate_policy(
        {"role": "viewer"},
        {},
        "delete",
        [{"name": "admin_only", "actions": ["delete"], "effect": "allow",
          "conditions": [{"attribute": "role", "operator": "eq", "value": "admin"}]}])
    assert not r["allowed"]

def test_list():
    perms = list_permissions(
        {"role": "editor"},
        [{"name": "p1", "actions": ["read", "write"], "effect": "allow",
          "conditions": [{"attribute": "role", "operator": "in", "value": ["editor", "admin"]}]}])
    assert "read" in perms
    assert "write" in perms
