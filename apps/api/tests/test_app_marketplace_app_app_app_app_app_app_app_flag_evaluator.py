from app.services.app_marketplace_app_app_app_app_app_app_app_flag_evaluator import FlagEvaluator

def test_targeting():
    fe = FlagEvaluator()
    fe.define("new_ui", target_users=["alice"], rollout_pct=50)
    r = fe.evaluate("new_ui", user_id="alice")
    assert r["enabled"]
    assert r["reason"] == "user_targeted"

def test_rollout():
    fe = FlagEvaluator()
    fe.define("experiment", rollout_pct=100)
    r = fe.evaluate("experiment", user_id="any_user")
    assert r["enabled"]
    assert r["reason"] == "rollout"

def test_default():
    fe = FlagEvaluator()
    fe.define("disabled", default=False, rollout_pct=0)
    r = fe.evaluate("disabled", user_id="bob")
    assert not r["enabled"]
    assert r["reason"] == "default"

def test_list():
    fe = FlagEvaluator()
    fe.define("a")
    fe.define("b", rollout_pct=50)
    assert len(fe.list_flags()) == 2
