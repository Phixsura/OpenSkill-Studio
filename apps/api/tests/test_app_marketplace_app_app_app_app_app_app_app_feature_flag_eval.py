from app.services.app_marketplace_app_app_app_app_app_app_app_feature_flag_eval import evaluate_flag, batch_evaluate

def test_disabled():
    r = evaluate_flag("dark_mode", False, 100, "u1")
    assert not r["value"]
    assert r["reason"] == "disabled"

def test_allowlist():
    r = evaluate_flag("beta", True, 0, "u1", allowlist=["u1"])
    assert r["value"]
    assert r["reason"] == "allowlisted"

def test_blocklist():
    r = evaluate_flag("beta", True, 100, "u1", blocklist=["u1"])
    assert not r["value"]

def test_batch():
    r = batch_evaluate([
        {"name": "a", "enabled": True, "rollout_pct": 100},
        {"name": "b", "enabled": False},
    ], "u1")
    assert r["flags"]["a"]
    assert not r["flags"]["b"]
    assert r["enabled"] == 1
