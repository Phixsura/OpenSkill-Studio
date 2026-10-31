from app.services.app_marketplace_app_app_app_app_app_app_app_perm_policy import evaluate_policy, list_permissions

def test_allow():
    r = evaluate_policy(
        {"role": "admin", "department": "eng"},
        {"type": "document"},
        "delete",
        [{"name": "admin_all", "actions": ["read", "write", "delete"], "effect": "allow",
          "conditions": [{"attribute": "role", "operator": "eq", "value": "admin", "source": "subject"}]}])
    assert r["allowed"]
    assert r["policy"] == "admin_all"

def test_deny():
    r = evaluate_policy(
        {"role": "viewer"},
        {},
        "delete",
        [{"name": "admin_only", "actions": ["delete"], "effect": "allow",
          "conditions": [{"attribute": "role", "operator": "eq", "value": "admin", "source": "subject"}]}])
    assert not r["allowed"]

def test_deny_overrides():
    r = evaluate_policy(
        {"role": "admin"},
        {},
        "delete",
        [{"name": "allow_admin", "actions": ["delete"], "effect": "allow",
          "conditions": [{"attribute": "role", "operator": "eq", "value": "admin", "source": "subject"}]},
         {"name": "deny_delete", "actions": ["delete"], "effect": "deny",
          "conditions": [{"attribute": "role", "operator": "eq", "value": "admin", "source": "subject"}]}])
    assert not r["allowed"]  # deny overrides

def test_unknown_operator_fails_closed():
    r = evaluate_policy(
        {"role": "admin"},
        {},
        "read",
        [{"name": "p1", "actions": ["read"], "effect": "allow",
          "conditions": [{"attribute": "role", "operator": "unknown_op", "value": "admin", "source": "subject"}]}])
    assert not r["allowed"]

def test_list():
    perms = list_permissions(
        {"role": "editor"},
        [{"name": "p1", "actions": ["read", "write"], "effect": "allow",
          "conditions": [{"attribute": "role", "operator": "in", "value": ["editor", "admin"], "source": "subject"}]}])
    assert "read" in perms
    assert "write" in perms
