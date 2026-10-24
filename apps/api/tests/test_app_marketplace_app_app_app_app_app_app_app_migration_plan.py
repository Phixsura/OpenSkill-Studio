from app.services.app_marketplace_app_app_app_app_app_app_app_migration_plan import plan_migration, generate_rollback

def test_plan():
    steps = [
        {"from_version": "1.0", "to_version": "1.1", "action": "add_column", "table": "users",
         "description": "Add email", "estimated_sec": 5, "breaking": False, "data_loss": False},
        {"from_version": "1.1", "to_version": "2.0", "action": "drop_column", "table": "users",
         "description": "Drop legacy", "estimated_sec": 10, "breaking": True, "data_loss": True},
    ]
    r = plan_migration("1.0", "2.0", steps)
    assert r["step_count"] == 2
    assert r["risk"] == "high"
    assert r["requires_downtime"]
    assert r["estimated_sec"] == 15

def test_rollback():
    steps = [{"action": "add_col", "table": "t", "description": "Add col"}]
    rb = generate_rollback(steps)
    assert len(rb) == 1
    assert rb[0]["action"] == "undo_add_col"
