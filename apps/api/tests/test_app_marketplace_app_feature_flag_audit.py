from app.services.app_marketplace_app_feature_flag_audit import record_flag_change, get_flag_history

def test_record():
    r = record_flag_change(flag_name="dark_mode", old_value=False, new_value=True,
        changed_by="alice", reason="User request")
    assert r["audit_id"].startswith("ffa_")
    assert r["change_type"] == "enabled"

def test_disabled():
    r = record_flag_change(flag_name="beta", old_value=True, new_value=False,
        changed_by="bob", reason="End of beta")
    assert r["change_type"] == "disabled"

def test_history():
    history = [
        {"flag_name": "dark_mode", "change_type": "enabled"},
        {"flag_name": "dark_mode", "change_type": "disabled"},
        {"flag_name": "beta", "change_type": "enabled"},
    ]
    r = get_flag_history(history=history, flag_name="dark_mode")
    assert r["total"] == 2

def test_most_changed():
    history = [{"flag_name": "a"}, {"flag_name": "a"}, {"flag_name": "b"}]
    r = get_flag_history(history=history)
    assert r["most_changed_flag"] == "a"
