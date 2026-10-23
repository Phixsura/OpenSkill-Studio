from app.services.app_marketplace_app_rollback_manager import create_rollback, get_rollback_history

def test_create():
    r = create_rollback(app_id="a1", from_version="2.1.0", to_version="2.0.5", reason="Error spike")
    assert r["rollback_id"].startswith("rb_")
    assert r["status"] == "pending"
    assert len(r["steps"]) == 4

def test_history():
    r = get_rollback_history(app_id="a1")
    assert r["total"] == 1
    assert r["rollbacks"][0]["status"] == "completed"
