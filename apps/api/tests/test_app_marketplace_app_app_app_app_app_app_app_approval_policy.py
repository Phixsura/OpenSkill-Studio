from app.services.app_marketplace_app_app_app_app_app_app_app_approval_policy import evaluate_approval

def test_requires_approval():
    r = evaluate_approval(
        {"env": "production", "services_affected": 5},
        [{"name": "prod_deploy", "conditions": [{"field": "env", "op": "eq", "value": "production"}],
          "approvers": ["team-lead", "sre"]},
         {"name": "large_change", "conditions": [{"field": "services_affected", "op": "gt", "value": 3}],
          "approvers": ["architect"]}])
    assert r["requires_approval"]
    assert "sre" in r["required_approvers"]
    assert "architect" in r["required_approvers"]
    assert len(r["matched_policies"]) == 2

def test_auto_approve():
    r = evaluate_approval(
        {"env": "dev", "services_affected": 1},
        [{"name": "prod_deploy", "conditions": [{"field": "env", "op": "eq", "value": "production"}],
          "approvers": ["team-lead"]}])
    assert r["auto_approve"]
