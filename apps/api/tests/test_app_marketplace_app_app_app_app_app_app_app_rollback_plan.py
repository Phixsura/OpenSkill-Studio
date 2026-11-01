from app.services.app_marketplace_app_app_app_app_app_app_app_rollback_plan import plan_rollback, compare_versions

def test_safe_rollback():
    r = plan_rollback(
        {"version": "2.1.0"}, {"version": "2.0.0"},
        [{"type": "migration", "name": "add_col"}])
    assert r["risk"] == "medium"
    assert r["target_version"] == "2.0.0"
    assert any(s["action"] == "rollback_migrations" for s in r["steps"])

def test_irreversible():
    r = plan_rollback(
        {"version": "3.0.0"}, {"version": "2.9.0"},
        [{"type": "migration", "name": "drop_table", "irreversible": True}])
    assert r["risk"] == "high"
    assert r["has_irreversible_migrations"]

def test_compare():
    assert compare_versions("2.1.0", "2.0.0")["direction"] == "downgrade"
    assert compare_versions("1.0.0", "2.0.0")["direction"] == "upgrade"
    assert compare_versions("1.0.0", "1.0.0")["direction"] == "same"
